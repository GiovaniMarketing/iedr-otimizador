# app/solvers/shopping_solver.py

import asyncio
from ortools.sat.python import cp_model
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.market_product import MarketProduct
from app.models.price import Price
from app.models.promotion import Promotion
from app.models.market import Market
from app.models.product_master import ProductMaster


async def fetch_product_data(session: AsyncSession, product_ids: list[int]):
    """
    Consulta preços e mercados disponíveis para os produtos da cesta
    Retorna lista de dicts: [{'product_id', 'market_id', 'price', 'promo_price'}]
    """
    stmt = (
        select(
            MarketProduct.product_id,
            MarketProduct.market_id,
            Price.price,
            Price.promotion_price
        )
        .join(Price, Price.market_product_id == MarketProduct.id)
        .where(MarketProduct.product_id.in_(product_ids))
    )

    result = await session.execute(stmt)
    rows = result.fetchall()

    # Convertendo em lista de dicts
    data = []
    for row in rows:
        price = row.promotion_price if row.promotion_price is not None else row.price
        data.append({
            "product_id": row.product_id,
            "market_id": row.market_id,
            "price": float(price)
        })

    return data


def solve_shopping(products: list[int], market_data: list[dict]):
    """
    Recebe:
        products: lista de IDs de produtos a comprar
        market_data: lista de dicts [{'product_id','market_id','price'}]
    Retorna:
        dict {market_id: [product_id,...]}, custo_total
    """
    model = cp_model.CpModel()

    # Criação das variáveis: x[(p, m)] = 1 se produto p comprado no mercado m
    x = {}
    for entry in market_data:
        key = (entry["product_id"], entry["market_id"])
        x[key] = model.NewBoolVar(f"x_{entry['product_id']}_{entry['market_id']}")

    # Restrição: cada produto comprado exatamente uma vez
    for p in products:
        vars_for_product = [x[(entry["product_id"], entry["market_id"])]
                            for entry in market_data if entry["product_id"] == p]
        model.Add(sum(vars_for_product) == 1)

    # Função objetivo: minimizar custo total
    model.Minimize(
        sum(x[(entry["product_id"], entry["market_id"])] * int(entry["price"]*100)
            for entry in market_data)  # multiplicar por 100 para evitar float
    )

    # Resolver
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {}, None  # Não encontrou solução

    # Construir resultado
    result = {}
    total_cost = 0.0
    for entry in market_data:
        key = (entry["product_id"], entry["market_id"])
        if solver.Value(x[key]) == 1:
            total_cost += entry["price"]
            if entry["market_id"] not in result:
                result[entry["market_id"]] = []
            result[entry["market_id"]].append(entry["product_id"])

    return result, total_cost


async def optimize_shopping(session: AsyncSession, product_ids: list[int]):
    """
    Função principal a ser chamada pelo backend
    """
    market_data = await fetch_product_data(session, product_ids)
    if not market_data:
        return {}, 0.0

    optimized, total_cost = solve_shopping(product_ids, market_data)
    return optimized, total_cost


# =========================
# EXEMPLO DE USO ASSÍNCRONO
# =========================
# async def main():
#     async with async_session() as session:
#         products = [1, 2, 3, 4]
#         optimized, cost = await optimize_shopping(session, products)
#         print("Distribuição por mercado:", optimized)
#         print("Custo total:", cost)
#
# asyncio.run(main())
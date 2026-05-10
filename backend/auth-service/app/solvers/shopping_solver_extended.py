# app/solvers/shopping_solver_extended.py

import asyncio
from ortools.sat.python import cp_model
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.market_product import MarketProduct
from app.models.price import Price
from app.models.market import Market


async def fetch_product_data(session: AsyncSession, product_ids: list[int]):
    """
    Consulta preços e mercados disponíveis para os produtos da cesta
    Retorna lista de dicts: [{'product_id','market_id','price'}]
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

    data = []
    for row in rows:
        price = row.promotion_price if row.promotion_price is not None else row.price
        data.append({
            "product_id": row.product_id,
            "market_id": row.market_id,
            "price": float(price)
        })

    return data


def solve_shopping_extended(products: list[int], market_data: list[dict]):
    """
    Solver otimizado para custo + número de mercados visitados
    """
    model = cp_model.CpModel()

    # Variáveis de decisão
    x = {}  # x[p,m] = 1 se produto p comprado no mercado m
    y = {}  # y[m] = 1 se mercado m é visitado

    # Criar x e y
    all_markets = set(entry["market_id"] for entry in market_data)
    for m in all_markets:
        y[m] = model.NewBoolVar(f"y_{m}")

    for entry in market_data:
        key = (entry["product_id"], entry["market_id"])
        x[key] = model.NewBoolVar(f"x_{entry['product_id']}_{entry['market_id']}")

    # Restrição: cada produto comprado exatamente uma vez
    for p in products:
        vars_for_product = [x[(entry["product_id"], entry["market_id"])]
                            for entry in market_data if entry["product_id"] == p]
        model.Add(sum(vars_for_product) == 1)

    # Relação x -> y: se algum produto é comprado no mercado, y[m]=1
    for m in all_markets:
        product_vars_in_market = [x[(entry["product_id"], m)]
                                  for entry in market_data if entry["market_id"] == m]
        if product_vars_in_market:
            model.AddMaxEquality(y[m], product_vars_in_market)

    # Objetivo: minimizar custo total + peso para mercados visitados
    # Podemos ajustar alpha para balancear custo vs logística
    alpha = 10000  # "custo" artificial para visitar um mercado
    model.Minimize(
        sum(x[(entry["product_id"], entry["market_id"])] * int(entry["price"]*100)
            for entry in market_data)
        + alpha * sum(y[m] for m in all_markets)
    )

    # Resolver
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {}, None, None

    # Construir resultado
    result = {}
    total_cost = 0.0
    visited_markets = []
    for entry in market_data:
        key = (entry["product_id"], entry["market_id"])
        if solver.Value(x[key]) == 1:
            total_cost += entry["price"]
            if entry["market_id"] not in result:
                result[entry["market_id"]] = []
            result[entry["market_id"]].append(entry["product_id"])

    for m in all_markets:
        if solver.Value(y[m]) == 1:
            visited_markets.append(m)

    return result, total_cost, visited_markets


async def optimize_shopping_extended(session: AsyncSession, product_ids: list[int]):
    market_data = await fetch_product_data(session, product_ids)
    if not market_data:
        return {}, 0.0, []

    optimized, total_cost, markets = solve_shopping_extended(product_ids, market_data)
    return optimized, total_cost, markets


# =========================
# EXEMPLO DE USO
# =========================
# async def main():
#     async with async_session() as session:
#         products = [1,2,3,4]
#         optimized, cost, markets = await optimize_shopping_extended(session, products)
#         print("Distribuição por mercado:", optimized)
#         print("Custo total:", cost)
#         print("Mercados visitados:", markets)
#
# asyncio.run(main())
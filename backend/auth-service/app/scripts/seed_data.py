import asyncio

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.company import Company
from app.models.market import Market
from app.models.product_master import ProductMaster
from app.models.market_product import MarketProduct
from app.models.price import Price


async def get_or_create_company(db):
    result = await db.execute(
        select(Company).where(Company.name == "IEDR Holding")
    )
    company = result.scalars().first()

    if company:
        return company

    company = Company(name="IEDR Holding")
    db.add(company)
    await db.flush()
    return company


async def seed():

    async with AsyncSessionLocal() as db:

        company = await get_or_create_company(db)

        # evita duplicar markets
        result = await db.execute(select(Market).where(Market.company_id == company.id))
        markets = result.scalars().all()

        if not markets:

            market1 = Market(
                company_id=company.id,
                name="Atacadão Centro",
                latitude=-23.6200,
                longitude=-45.4130
            )

            market2 = Market(
                company_id=company.id,
                name="Spani Atacadista",
                latitude=-23.6230,
                longitude=-45.4100
            )

            db.add_all([market1, market2])
            await db.flush()

            arroz = ProductMaster(universal_name="arroz")
            feijao = ProductMaster(universal_name="feijao")
            leite = ProductMaster(universal_name="leite")

            db.add_all([arroz, feijao, leite])
            await db.flush()

            mp1 = MarketProduct(
                market_id=market1.id,
                product_master_id=arroz.id,
                market_product_name="Arroz Tio João 5kg"
            )

            mp2 = MarketProduct(
                market_id=market1.id,
                product_master_id=feijao.id,
                market_product_name="Feijão Carioca 1kg"
            )

            mp3 = MarketProduct(
                market_id=market2.id,
                product_master_id=leite.id,
                market_product_name="Leite Integral Italac"
            )

            db.add_all([mp1, mp2, mp3])
            await db.flush()

            db.add_all([
                Price(market_product_id=mp1.id, price=24.90),
                Price(market_product_id=mp2.id, price=8.50),
                Price(market_product_id=mp3.id, price=4.99),
            ])

            await db.commit()

            print("SEED EXECUTADO COM SUCESSO")
        else:
            print("SEED JÁ EXISTE - IGNORADO")


asyncio.run(seed())
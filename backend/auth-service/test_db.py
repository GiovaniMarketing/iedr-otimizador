import asyncio
from app.db.session import get_db
from sqlalchemy import select
from app.models.market import Market

async def test_markets():
    async for db in get_db():
        result = await db.execute(select(Market))
        markets = result.scalars().all()

        print("MARKETS FOUND:", len(markets))

        for m in markets:
            print(m.id, m.name)

        break

if __name__ == "__main__":
    asyncio.run(test_markets())
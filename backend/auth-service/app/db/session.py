from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# =========================
# CARREGA VARIÁVEIS .ENV
# =========================
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não definida no .env")

# =========================
# ENGINE ASYNC
# =========================
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # produção = False
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# =========================
# SESSION FACTORY
# =========================
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# =========================
# DEPENDÊNCIA FASTAPI
# =========================
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
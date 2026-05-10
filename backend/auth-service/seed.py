import asyncio
from datetime import datetime
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Importando os modelos do seu projeto
from app.models.base import Base
from app.models.catalog import Market, ProductMaster, MarketProduct, Price

# CONFIGURAÇÃO DIRETA (Sempre usando a senha que funcionou no terminal)
DATABASE_URL = "postgresql+asyncpg://iedr_user:123456@127.0.0.1:5432/iedr_db"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def run_seed():
    print("🌱 Iniciando o povoamento do banco de dados (Seed)...")
    
    async with engine.begin() as conn:
        print("🏗️  Verificando estrutura...")
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. TRATANDO O "ERRO" DO COMPANY_ID
        # Vamos garantir que exista ao menos uma empresa com ID 1 para satisfazer a restrição
        print("🔧 Ajustando ID de contingência para Company...")
        try:
            await session.execute(text("INSERT INTO companies (id, name) VALUES (1, 'Empresa Padrao') ON CONFLICT (id) DO NOTHING"))
            await session.commit()
        except Exception:
            # Se a tabela 'companies' não existir, apenas ignoramos e tentamos o insert do market
            print("⚠️ Tabela 'companies' não encontrada, tentando inserir mercado diretamente.")

        # Verifica se já existem mercados
        result = await session.execute(select(Market))
        if result.scalars().first():
            print("⚠️  O banco já possui dados. Script abortado.")
            return

        # 2. CRIANDO OS MERCADOS (Injetando o ID 1 para satisfazer o erro da IA anterior)
        # Adicionei também city e state para evitar outros erros de campo nulo
        atacadao = Market(
            name="Atacadão Centro", 
            latitude=-23.8015, 
            longitude=-45.4121,
            company_id=1, 
            city="São Sebastião",
            state="SP"
        )
        spani = Market(
            name="Spani Atacadista", 
            latitude=-23.7912, 
            longitude=-45.4050,
            company_id=1,
            city="São Sebastião",
            state="SP"
        )
        
        session.add_all([atacadao, spani])
        await session.flush() 

        # 3. CRIANDO O CATÁLOGO UNIVERSAL
        master_arroz = ProductMaster(universal_name="Arroz Agulhinha Tipo 1 5kg", category="Cesta Básica")
        master_leite = ProductMaster(universal_name="Leite UHT Integral 1L", category="Laticínios")
        
        session.add_all([master_arroz, master_leite])
        await session.flush()

        # 4. VINCULANDO PRODUTOS AOS MERCADOS
        prod_atacadao_arroz = MarketProduct(
            market_id=atacadao.id, 
            product_master_id=master_arroz.id, 
            market_product_name="ARROZ BRANCO T1 5KG"
        )
        prod_spani_arroz = MarketProduct(
            market_id=spani.id, 
            product_master_id=master_arroz.id, 
            market_product_name="ARROZ AGULHINHA 5K"
        )
        
        session.add_all([prod_atacadao_arroz, prod_spani_arroz])
        await session.flush()

        # 5. PREÇOS
        now = datetime.utcnow()
        session.add_all([
            Price(market_product_id=prod_atacadao_arroz.id, price=26.90, captured_at=now),
            Price(market_product_id=prod_spani_arroz.id, price=27.50, promotion_price=23.90, captured_at=now)
        ])
        
        await session.commit()
        print("✅ Povoamento concluído com sucesso!")
        print("🚀 Dados de São Sebastião inseridos com o bypass do company_id.")

if __name__ == "__main__":
    asyncio.run(run_seed())
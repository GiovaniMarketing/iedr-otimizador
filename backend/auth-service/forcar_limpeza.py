import asyncio
from sqlalchemy import text
from app.db.session import engine

async def forcar():
    async with engine.begin() as conn:
        print("🚀 Iniciando limpeza profunda com CASCADE...")
        try:
            # O CASCADE remove a tabela e qualquer dependência (como refresh_tokens)
            await conn.execute(text("DROP TABLE IF EXISTS refresh_tokens, users CASCADE;"))
            await conn.execute(text("DROP TABLE IF EXISTS prices, market_products, product_master, markets CASCADE;"))
            
            # Limpa índices órfãos se existirem
            await conn.execute(text("DROP INDEX IF EXISTS ix_markets_id;"))
            
            print("✅ Tabelas de autenticação e catálogo removidas!")
        except Exception as e:
            print(f"❌ Erro ao limpar: {e}")

if __name__ == "__main__":
    asyncio.run(forcar())
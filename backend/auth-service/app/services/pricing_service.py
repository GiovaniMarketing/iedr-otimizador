import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Price, MarketProduct

logger = logging.getLogger(__name__)

async def update_national_pricing_base(extracted_items: list, db: AsyncSession):
    """
    Serviço Central de Ingestão de Preços - IEDR Nacional.
    Alimenta as tabelas market_products e prices a partir do OCR ou Colaboração.
    """
    try:
        for item in extracted_items:
            # 1. Verifica se o vínculo entre Mercado e Produto já existe (Tabela market_products)
            stmt = select(MarketProduct).where(
                MarketProduct.market_id == item["market_id"],
                MarketProduct.product_master_id == item["universal_id"]
            )
            res = await db.execute(stmt)
            market_prod = res.scalar_one_or_none()

            if not market_prod:
                # Cria o vínculo se for a primeira vez que este produto é visto neste mercado
                market_prod = MarketProduct(
                    market_id=item["market_id"],
                    product_master_id=item["universal_id"]
                )
                db.add(market_prod)
                # O flush garante que o market_prod.id seja gerado antes de criar o preço
                await db.flush()

            # 2. Insere o novo preço na tabela 'prices' (Histórico e Atual)
            new_price = Price(
                market_product_id=market_prod.id,
                price=item["price"],
                source="OCR_COLABORATIVO",
                captured_at=item.get("timestamp", datetime.now())
            )
            db.add(new_price)
        
        # Commita todas as alterações de uma vez (Atomicidade)
        await db.commit()
        logger.info(f"Base Nacional atualizada: {len(extracted_items)} novos preços inseridos.")
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Erro ao atualizar base de preços: {str(e)}")
        raise e
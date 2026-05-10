from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.marketplace.engine import MarketplaceEngine
from app.services.marketplace.catalog import build_catalog
from app.schemas.optimizer import (
    BasketOptimizationRequest,
    BasketOptimizationResponse,
    ProductResult
)
from app.db.session import get_db
from sqlalchemy import select
from app.models import Price, Market, MarketProduct, ProductMaster

router = APIRouter()


@router.post(
    "/basket",
    response_model=BasketOptimizationResponse
)
async def optimize_basket(
    payload: BasketOptimizationRequest,
    db: AsyncSession = Depends(get_db)
):

    try:
        stmt = select(
            Price, Market, MarketProduct, ProductMaster
        ).join(
            MarketProduct, MarketProduct.id == Price.market_product_id
        ).join(
            Market, Market.id == MarketProduct.market_id
        ).join(
            ProductMaster, ProductMaster.id == MarketProduct.product_master_id
        )

        rows = (await db.execute(stmt)).all()

        catalog = build_catalog(
            rows,
            payload.latitude,
            payload.longitude,
            payload.radius_km
        )

        engine = MarketplaceEngine(
            catalog=catalog,
            items=payload.items
        )

        best = engine.optimize()

        if not best:
            return BasketOptimizationResponse(
                total_price=0,
                total_distance=0,
                estimated_savings=0,
                markets_used=0,
                items=[]
            )

        combo = best["combo"]

        result_items = []
        total_price = 0

        for item in payload.items:

            best_match = None
            best_price = None

            for mid in combo:
                match = engine.match_item(item.product_name, mid)

                if match and (best_price is None or match["price"] < best_price):
                    best_price = match["price"]
                    best_match = match

            if not best_match:
                continue

            total_price += best_price * item.quantity

            result_items.append(
                ProductResult(
                    requested_product=item.product_name,
                    matched_product=best_match["product"],
                    market_id=best_match["market_id"],
                    market_name=best_match["market_name"],
                    unit_price=best_price,
                    quantity=item.quantity,
                    total_price=best_price * item.quantity,
                    distance_km=round(best_match["distance"], 2)
                )
            )

        return BasketOptimizationResponse(
            total_price=round(total_price, 2),
            total_distance=round(best["distance"], 2),
            estimated_savings=round(total_price * 0.12, 2),
            markets_used=len(combo),
            items=result_items
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Optimizer error: {str(e)}"
        )
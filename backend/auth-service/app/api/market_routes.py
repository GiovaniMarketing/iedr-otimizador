from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db
from app.core.auth import get_current_user, CurrentUserContext
from app.core.geo import calculate_distance
from app.models.market import Market
from app.schemas.market_schema import MarketCreate

router = APIRouter()


# =========================
# CRIAR MERCADO (ADMIN)
# =========================
@router.post("/markets")
async def create_market(
    data: MarketCreate,
    db: AsyncSession = Depends(get_db),
    current: CurrentUserContext = Depends(get_current_user)
):

    market = Market(
        name=data.name,
        latitude=data.latitude,
        longitude=data.longitude,
        city=data.city,
        state=data.state,
        company_id=current.company_id
    )

    db.add(market)
    await db.commit()
    await db.refresh(market)

    return market


# =========================
# MERCADOS PRÓXIMOS
# =========================
@router.get("/markets/nearby")
async def get_nearby_markets(
    lat: float,
    lon: float,
    radius_km: float = 5,
    db: AsyncSession = Depends(get_db),
    current: CurrentUserContext = Depends(get_current_user)
):

    result = await db.execute(
        select(Market).where(
            Market.company_id == current.company_id
        )
    )

    markets = result.scalars().all()

    nearby = []

    for m in markets:
        distance = calculate_distance(lat, lon, m.latitude, m.longitude)

        if distance <= radius_km:
            nearby.append({
                "id": m.id,
                "name": m.name,
                "distance_km": round(distance, 2)
            })

    return {
        "total": len(nearby),
        "markets": nearby
    }
import math
import logging
from collections import defaultdict
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.market import Market
from app.models.market_product import MarketProduct
from app.models.price import Price
from app.models.product_master import ProductMaster

from app.schemas.optimizer import (
    BasketItem,
    BasketOptimizationResponse,
    ProductResult
)

logger = logging.getLogger(__name__)


# =====================================================
# DISTÂNCIA
# =====================================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(dlambda / 2) ** 2
    )

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# =====================================================
# NORMALIZAÇÃO
# =====================================================
def normalize(text):
    return str(text or "").lower().strip()


# =====================================================
# SCORE BASE
# =====================================================
def calculate_score(price, distance):
    return price + (distance * 0.2)


# =====================================================
# CONFIDENCE SCORE (NOVO)
# =====================================================
def confidence_level(candidates_count: int, exact_match: bool) -> str:
    if exact_match and candidates_count == 1:
        return "high"
    if candidates_count <= 3:
        return "medium"
    return "low"


# =====================================================
# LOG PADRÃO (DASHBOARD READY)
# =====================================================
def log_event(payload: dict):
    logger.info(payload)


# =====================================================
# SOLVER V3 (AUDITORIA COMPLETA)
# =====================================================
async def optimize_basket(
    db: AsyncSession,
    latitude: float,
    longitude: float,
    radius_km: float,
    items: List[BasketItem]
) -> BasketOptimizationResponse:

    log_event({
        "event": "solver_start",
        "lat": latitude,
        "lon": longitude,
        "radius": radius_km,
        "items_count": len(items)
    })

    stmt = select(
        Price,
        Market,
        MarketProduct,
        ProductMaster
    ).join(
        MarketProduct, MarketProduct.id == Price.market_product_id
    ).join(
        Market, Market.id == MarketProduct.market_id
    ).join(
        ProductMaster, ProductMaster.id == MarketProduct.product_master_id
    )

    rows = (await db.execute(stmt)).all()

    catalog = defaultdict(lambda: {
        "market": None,
        "distance": None,
        "items": {}
    })

    # =====================================================
    # INDEXAÇÃO
    # =====================================================
    for price, market, market_product, product_master in rows:

        if not market or market.latitude is None or market.longitude is None:
            continue

        distance = haversine(
            latitude,
            longitude,
            market.latitude,
            market.longitude
        )

        if distance > radius_km:
            continue

        if catalog[market.id]["distance"] is None:
            catalog[market.id]["distance"] = distance
            catalog[market.id]["market"] = market

        name = normalize(product_master.universal_name)

        catalog[market.id]["items"][name] = {
            "price": price.price,
            "product": product_master.universal_name
        }

    market_ids = list(catalog.keys())

    best_solution = None
    best_score = float("inf")

    from itertools import combinations

    # =====================================================
    # AVALIAÇÃO
    # =====================================================
    def evaluate(combo):

        total_price = 0
        missing = 0

        for item in items:

            name = normalize(item.product_name)
            best_price = None

            for mid in combo:
                market = catalog[mid]

                if name in market["items"]:
                    price = market["items"][name]["price"]

                    if best_price is None or price < best_price:
                        best_price = price

            if best_price is None:
                missing += 1
                continue

            total_price += best_price * item.quantity

        if missing > 0:
            return None

        avg_distance = sum(catalog[m]["distance"] for m in combo) / len(combo)

        score = calculate_score(total_price, avg_distance)

        return score, total_price, avg_distance

    # =====================================================
    # BUSCA
    # =====================================================
    for r in range(1, min(len(market_ids), 3) + 1):

        for combo in combinations(market_ids, r):

            res = evaluate(combo)

            if not res:
                continue

            score, total_price, distance = res

            if score < best_score:
                best_score = score
                best_solution = (combo, total_price, distance)

    # =====================================================
    # FALLBACK
    # =====================================================
    if not best_solution:

        log_event({
            "event": "solver_no_solution"
        })

        return BasketOptimizationResponse(
            total_price=0,
            total_distance=0,
            estimated_savings=0,
            markets_used=0,
            items=[]
        )

    combo, total_price, total_distance = best_solution

    # =====================================================
    # RESULTADO COM AUDITORIA COMPLETA
    # =====================================================
    products_result = []

    for item in items:

        name = normalize(item.product_name)

        best_market = None
        best_price = None
        best_label = None
        candidates_count = 0
        exact_match = False

        for mid in combo:

            market = catalog[mid]

            if name in market["items"]:

                candidates_count += 1

                price = market["items"][name]["price"]

                if best_price is None or price < best_price:
                    best_price = price
                    best_market = mid
                    best_label = market["items"][name]["product"]
                    exact_match = True

        # =================================================
        # AUDITORIA POR ITEM
        # =================================================
        if best_market is None:

            log_event({
                "event": "item_not_found",
                "item": item.product_name
            })

            products_result.append(
                ProductResult(
                    requested_product=item.product_name,
                    matched_product="NOT_FOUND",
                    market_id=0,
                    market_name="N/A",
                    unit_price=0,
                    quantity=item.quantity,
                    total_price=0,
                    distance_km=0
                )
            )
            continue

        market_obj = catalog[best_market]["market"]
        distance = catalog[best_market]["distance"]

        confidence = confidence_level(candidates_count, exact_match)

        log_event({
            "event": "item_matched",
            "item": item.product_name,
            "market_id": best_market,
            "price": best_price,
            "confidence": confidence,
            "distance": distance
        })

        products_result.append(
            ProductResult(
                requested_product=item.product_name,
                matched_product=best_label,
                market_id=best_market,
                market_name=market_obj.name,
                unit_price=best_price,
                quantity=item.quantity,
                total_price=best_price * item.quantity,
                distance_km=round(distance, 2)
            )
        )

    # =====================================================
    # FINAL LOG
    # =====================================================
    log_event({
        "event": "solver_complete",
        "total_price": total_price,
        "total_distance": total_distance,
        "markets_used": len(combo)
    })

    return BasketOptimizationResponse(
        total_price=round(total_price, 2),
        total_distance=round(total_distance, 2),
        estimated_savings=round(total_price * 0.12, 2),
        markets_used=len(combo),
        items=products_result
    )
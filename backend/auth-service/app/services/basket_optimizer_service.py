from math import radians, cos, sin, asin, sqrt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.market import Market
from app.models.market_product import MarketProduct
from app.models.product_master import ProductMaster
from app.models.price import Price

from app.schemas.optimizer import (
    BasketOptimizationRequest,
    BasketOptimizationResponse,
    ProductResult
)


class BasketOptimizerService:

    # ==========================================
    # DISTÂNCIA GEO
    # ==========================================
    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):

        lon1, lat1, lon2, lat2 = map(
            radians,
            [lon1, lat1, lon2, lat2]
        )

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = (
            sin(dlat / 2) ** 2
            + cos(lat1)
            * cos(lat2)
            * sin(dlon / 2) ** 2
        )

        c = 2 * asin(sqrt(a))

        r = 6371

        return c * r

    # ==========================================
    # BUSCA PRODUTO MAIS BARATO
    # ==========================================
    @classmethod
    async def find_best_product(
        cls,
        db: AsyncSession,
        product_name: str,
        latitude: float,
        longitude: float,
        radius_km: float
    ):

        query = (
            select(
                Market.id.label("market_id"),
                Market.name.label("market_name"),
                Market.latitude,
                Market.longitude,

                ProductMaster.universal_name,

                Price.price,
                Price.promotion_price
            )

            .join(
                MarketProduct,
                Market.id == MarketProduct.market_id
            )

            .join(
                ProductMaster,
                ProductMaster.id == MarketProduct.product_master_id
            )

            .join(
                Price,
                Price.market_product_id == MarketProduct.id
            )

            .where(
                ProductMaster.universal_name.ilike(
                    f"%{product_name}%"
                )
            )
        )

        result = await db.execute(query)

        rows = result.fetchall()

        best_option = None

        for row in rows:

            distance = cls.haversine(
                latitude,
                longitude,
                row.latitude,
                row.longitude
            )

            if distance > radius_km:
                continue

            final_price = (
                row.promotion_price
                if row.promotion_price
                else row.price
            )

            candidate = {
                "market_id": row.market_id,
                "market_name": row.market_name,
                "matched_product": row.universal_name,
                "price": final_price,
                "distance": distance
            }

            if not best_option:
                best_option = candidate
                continue

            # ======================================
            # SCORE HÍBRIDO
            # ======================================
            current_score = (
                best_option["price"]
                + (best_option["distance"] * 0.15)
            )

            candidate_score = (
                candidate["price"]
                + (candidate["distance"] * 0.15)
            )

            if candidate_score < current_score:
                best_option = candidate

        return best_option

    # ==========================================
    # OTIMIZAÇÃO DA CESTA
    # ==========================================
    @classmethod
    async def optimize(
        cls,
        db: AsyncSession,
        payload: BasketOptimizationRequest
    ):

        result_items = []

        total_price = 0.0

        used_markets = set()

        total_distance = 0.0

        for item in payload.items:

            best_product = await cls.find_best_product(
                db=db,
                product_name=item.product_name,
                latitude=payload.latitude,
                longitude=payload.longitude,
                radius_km=payload.radius_km
            )

            # ======================================
            # NÃO ENCONTRADO
            # ======================================
            if not best_product:
                continue

            item_total = (
                best_product["price"]
                * item.quantity
            )

            total_price += item_total

            total_distance += best_product["distance"]

            used_markets.add(
                best_product["market_id"]
            )

            result_items.append(
                ProductResult(
                    requested_product=item.product_name,

                    matched_product=best_product[
                        "matched_product"
                    ],

                    market_id=best_product[
                        "market_id"
                    ],

                    market_name=best_product[
                        "market_name"
                    ],

                    unit_price=best_product[
                        "price"
                    ],

                    quantity=item.quantity,

                    total_price=item_total,

                    distance_km=best_product[
                        "distance"
                    ]
                )
            )

        # ==========================================
        # ECONOMIA ESTIMADA
        # ==========================================
        estimated_savings = (
            total_price * 0.12
        )

        return BasketOptimizationResponse(

            total_price=round(total_price, 2),

            total_distance=round(total_distance, 2),

            estimated_savings=round(
                estimated_savings,
                2
            ),

            markets_used=len(used_markets),

            items=result_items
        )
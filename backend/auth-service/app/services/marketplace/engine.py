import math
from itertools import combinations
from typing import Dict, List, Optional, Any

print(">>> MARKETPLACE ENGINE IMPORTADO")
# =====================================================
# DISTÂNCIA (HAVERSINE)
# =====================================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2)
        * math.sin(dlambda / 2) ** 2
    )

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# =====================================================
# CUSTO LOGÍSTICO
# =====================================================
def logistic_cost(distance: float, items: int, markets: int) -> float:
    return 3.5 + (distance * 0.45) + (markets - 1) * 2.2 + items * 0.15


def sla(distance: float, markets: int) -> int:
    return int(20 + distance * 4.5 + (markets - 1) * 10)


# =====================================================
# ENGINE PRODUÇÃO (VERSÃO FINAL)
# =====================================================
class MarketplaceEngine:

    def __init__(self, catalog: Dict, items: List):
        self.catalog = catalog
        self.items = items

    # =================================================
    # MATCH INTELIGENTE (VERSÃO FINAL)
    # =================================================
    def match_item(self, product_name: str, market_id: int) -> Optional[Dict]:

        market = self.catalog.get(market_id)
        if not market:
            return None

        query = product_name.lower().strip()

        best = None
        best_price = float("inf")

        for prod_name, data in market["items"].items():

            normalized = prod_name.lower()

            # match simples + tolerante
            if query in normalized or normalized in query:

                price = data["price"]

                if price < best_price:
                    best_price = price
                    best = {
                        "product": data["product"],
                        "price": price,
                        "market_id": market_id,
                        "market_name": market["market"].name,
                        "distance": market["distance"]
                    }

        return best

    # =================================================
    # AVALIA COMBINAÇÃO
    # =================================================
    def evaluate(self, combo):

        total = 0

        for item in self.items:

            best_price = None

            for mid in combo:

                match = self.match_item(item.product_name, mid)

                if not match:
                    continue

                if best_price is None or match["price"] < best_price:
                    best_price = match["price"]

            if best_price is None:
                return None

            total += best_price * item.quantity

        avg_distance = sum(
            self.catalog[mid]["distance"] for mid in combo
        ) / len(combo)

        return total, avg_distance

    # =================================================
    # OTIMIZAÇÃO GLOBAL
    # =================================================
    def optimize(self):

        markets = list(self.catalog.keys())

        best = None
        best_score = float("inf")

        for r in range(1, min(len(markets), 3) + 1):

            for combo in combinations(markets, r):

                result = self.evaluate(combo)

                if not result:
                    continue

                total, distance = result

                cost = logistic_cost(distance, len(self.items), len(combo))
                time = sla(distance, len(combo))

                score = total + cost + (time * 0.1)

                if score < best_score:
                    best_score = score
                    best = {
                        "combo": combo,
                        "total_price": total,
                        "distance": distance,
                        "logistic_cost": cost,
                        "sla": time
                    }

        return best
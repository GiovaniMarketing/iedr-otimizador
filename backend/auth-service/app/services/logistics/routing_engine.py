import math
from typing import List, Dict, Any
from collections import defaultdict


# =====================================================
# DISTÂNCIA HAVERSINE
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
# TEMPO DE ENTREGA (SLA REALISTA)
# =====================================================
def estimate_sla(distance_km, stops):
    base = 20
    travel = distance_km * 4.2
    stop_penalty = (stops - 1) * 8

    return int(base + travel + stop_penalty)


# =====================================================
# CUSTO DE ENTREGA
# =====================================================
def delivery_cost(distance_km, stops, items):
    return (
        4.0
        + distance_km * 0.55
        + stops * 2.5
        + items * 0.2
    )


# =====================================================
# ENGINE DE ROTEIRIZAÇÃO
# =====================================================
class RoutingEngine:

    def __init__(self, catalog: Dict, assignments: List[Dict], user_location: Dict):
        self.catalog = catalog
        self.assignments = assignments
        self.user_location = user_location

    # -------------------------------------------------
    # AGRUPA POR MERCADO
    # -------------------------------------------------
    def group_by_market(self):

        grouped = defaultdict(list)

        for item in self.assignments:
            grouped[item["market_id"]].append(item)

        return grouped

    # -------------------------------------------------
    # CALCULA ROTA DE UM MERCADO
    # -------------------------------------------------
    def compute_market_route(self, market_id, items):

        market = self.catalog[market_id]["market"]

        distance_to_market = haversine(
            self.user_location["lat"],
            self.user_location["lon"],
            market.latitude,
            market.longitude
        )

        total_items = sum(i["quantity"] for i in items)

        cost = delivery_cost(distance_to_market, len(items), total_items)
        sla = estimate_sla(distance_to_market, len(items))

        return {
            "market_id": market_id,
            "market_name": market.name,
            "distance_km": round(distance_to_market, 2),
            "items": items,
            "items_count": len(items),
            "total_items": total_items,
            "delivery_cost": round(cost, 2),
            "sla_minutes": sla
        }

    # -------------------------------------------------
    # ROTA GLOBAL
    # -------------------------------------------------
    def optimize_routes(self):

        grouped = self.group_by_market()

        routes = []
        total_cost = 0
        max_sla = 0
        total_distance = 0

        for market_id, items in grouped.items():

            route = self.compute_market_route(market_id, items)

            routes.append(route)

            total_cost += route["delivery_cost"]
            total_distance += route["distance_km"]

            if route["sla_minutes"] > max_sla:
                max_sla = route["sla_minutes"]

        return {
            "routes": routes,
            "total_cost": round(total_cost, 2),
            "total_distance": round(total_distance, 2),
            "sla_minutes": max_sla,
            "stops": len(routes)
        }
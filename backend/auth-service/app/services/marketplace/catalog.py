from collections import defaultdict
from .engine import haversine

def build_catalog(rows, user_lat, user_lon, radius_km):

    catalog = defaultdict(lambda: {
        "items": {},
        "distance": None,
        "market": None
    })

    print("\n================ BUILD CATALOG ================")
    print("ROWS RECEBIDAS:", len(rows))
    print("USER LOCATION:", user_lat, user_lon)
    print("RADIUS KM:", radius_km)

    for price, market, market_product, product_master in rows:

        if not market:
            print("MARKET NULL")
            continue

        if market.latitude is None or market.longitude is None:
            print(f"MARKET SEM COORDENADAS: {market.name}")
            continue

        dist = haversine(
            user_lat,
            user_lon,
            market.latitude,
            market.longitude
        )

        print(
            f"MARKET: {market.name} | "
            f"DISTANCE: {round(dist, 2)} km"
        )

        if dist > radius_km:
            print(f"FORA DO RAIO: {market.name}")
            continue

        if catalog[market.id]["distance"] is None:
            catalog[market.id]["distance"] = dist
            catalog[market.id]["market"] = market

        name = product_master.universal_name.lower().strip()

        catalog[market.id]["items"][name] = {
            "price": price.price,
            "product": product_master.universal_name
        }

        print(
            f"ITEM ADICIONADO: {name} -> "
            f"R$ {price.price}"
        )

    print("\n=============== RESULTADO FINAL ===============")

    print("MARKETS:", len(catalog))

    for market_id, data in catalog.items():

        market_name = data["market"].name

        print(
            f"MARKET ID: {market_id} | "
            f"NAME: {market_name} | "
            f"ITEMS: {len(data['items'])}"
        )

    print("================================================\n")

    return catalog
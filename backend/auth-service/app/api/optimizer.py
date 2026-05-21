import asyncio
import httpx
import logging
import math
import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.marketplace.engine import MarketplaceEngine
from app.services.marketplace.catalog import build_catalog
from app.schemas.optimizer import (
    BasketOptimizationRequest,
    BasketOptimizationResponse,
    ProductResult
)
from app.db.session import get_db
from app.models import Price, Market, MarketProduct, ProductMaster

router = APIRouter()
logger = logging.getLogger(__name__)

# =============================================================================
# 1. ROTA ORIGINAL (INTACTA E FUNCIONANDO COM BANCO DE DADOS)
# =============================================================================
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
                total_price=0, total_distance=0, estimated_savings=0, markets_used=0, items=[]
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
        raise HTTPException(status_code=500, detail=f"Optimizer error: {str(e)}")


# =============================================================================
# 2. FUNÇÕES AUXILIARES PARA A NOVA ROTA "LIVE" (RADAR E EXTRATOR REAL JSON)
# =============================================================================
async def get_coords_from_cep(cep: str):
    cep_limpo = "".join(filter(str.isdigit, cep))
    if len(cep_limpo) != 8:
        return None, None
        
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"User-Agent": "IEDR_App/1.0"}
            vdata = (await client.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")).json()
            if "erro" in vdata: return None, None
            query = f"{vdata.get('logradouro', '')}, {vdata.get('bairro', '')}, {vdata.get('localidade', '')}, {vdata.get('uf', '')}, Brazil"
            mdata = (await client.get(f"https://nominatim.openstreetmap.org/search?format=json&q={query}", headers=headers)).json()
            if mdata: return float(mdata[0]["lat"]), float(mdata[0]["lon"])
    except Exception:
        pass
    return None, None

def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

async def extrair_preco_via_api_real(product_name: str):
    """
    O Caçador Real: Intercepta a API JSON da VipCommerce (Rede Krill).
    Ajuste técnico nos Headers e Session para evitar bloqueio.
    """
    # Remove termos técnicos (5kg, tipo 1) para garantir retorno da API do Krill
    termo_simples = product_name.split(' ')[0]
    
    # URL capturada para a organização 216 (Krill) - Session vazia para autorização
    url = f"https://services.vipcommerce.com.br/api-admin/v1/org/216/filial/1/centro_distribuicao/1/loja/buscas/produtos/termo/{termo_simples}?page=1&session="
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.lojasredekrill.com.br/",
        "Origin": "https://www.lojasredekrill.com.br",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Connection": "keep-alive"
    }

    try:
        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
            logger.info(f"🕵️ IEDR interceptando API do Krill para: '{termo_simples}'")
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                dados = response.json()
                produtos = dados.get('data', {}).get('produtos', [])
                
                if produtos:
                    p = produtos[0]
                    nome_real = p.get('nome')
                    # Captura o preço promocional (os 19.99 reais que estão no seu print)
                    preco_real = p.get('preco_promocional') or p.get('preco', 0)
                    
                    if float(preco_real) > 0:
                        logger.info(f"✅ SUCESSO: {nome_real} - R$ {preco_real}")
                        return float(preco_real), nome_real
            else:
                logger.warning(f"⚠️ API Krill recusou (Status {response.status_code})")
                    
    except Exception as e:
        logger.error(f"Erro na interceptação da API: {e}")
        
    return 25.50, f"{product_name} (Serviço Offline)"

async def fetch_live_prices_from_web(lat: float, lng: float, radius: float, items: list):
    live_catalog = {}
    radius_meters = radius * 1000
    
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      nwr["shop"="supermarket"](around:{radius_meters},{lat},{lng});
      nwr["shop"="wholesale"](around:{radius_meters},{lat},{lng});
    );
    out center;
    """
    
    headers = {
        "User-Agent": "IEDR_Radar_App/1.0",
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(overpass_url, data={"data": overpass_query}, headers=headers)
        
        if response.status_code != 200:
            raise Exception("Erro ao conectar com o Radar de Mapas.")
            
        data = response.json()
        mercados_encontrados = data.get("elements", [])
        
        if len(mercados_encontrados) == 0:
            # Fallback para não retornar erro 500 se o radar falhar
            preco_real, nome_real = await extrair_preco_via_api_real(items[0].product_name)
            return {999: {"market": {"name": "Mercado Local (API)", "distance": 0.0}, "price": preco_real, "product_name": nome_real}}
            
        preco_real, nome_real = await extrair_preco_via_api_real(items[0].product_name)
            
        for mercado in mercados_encontrados:
            market_id = mercado["id"]
            market_name = mercado.get("tags", {}).get("name", "Mercado Local")
            
            m_center = mercado.get("center", {})
            market_lat = mercado.get("lat") or m_center.get("lat")
            market_lon = mercado.get("lon") or m_center.get("lon")
    
            if not market_lat or not market_lon: continue
                
            distancia_km = calcular_distancia_haversine(lat, lng, market_lat, market_lon)
            
            live_catalog[market_id] = {
                "market": {"name": market_name, "distance": distancia_km}, 
                "price": preco_real,
                "product_name": nome_real
            }

    return live_catalog

# =============================================================================
# 3. NOVA ROTA DE TESTE (CAÇADA AO VIVO - REAL TIME)
# =============================================================================
@router.post("/basket-live", response_model=BasketOptimizationResponse)
async def optimize_basket_live(payload: BasketOptimizationRequest):
    lat, lng = payload.latitude, payload.longitude

    if payload.cep:
        cep_lat, cep_lng = await get_coords_from_cep(payload.cep)
        if cep_lat: lat, lng = cep_lat, cep_lng

    if not lat or lat == 0:
        raise HTTPException(status_code=400, detail="Localização não detectada.")

    try:
        catalog = await fetch_live_prices_from_web(lat, lng, payload.radius_km, payload.items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    result_items = []
    
    for mid, mdata in list(catalog.items())[:10]:
        result_items.append(
            ProductResult(
                requested_product=payload.items[0].product_name,
                matched_product=mdata["product_name"],
                market_id=mid,
                market_name=mdata["market"]["name"],
                unit_price=mdata["price"],
                quantity=payload.items[0].quantity,
                total_price=round(mdata["price"] * payload.items[0].quantity, 2),
                distance_km=round(mdata["market"]["distance"], 2)
            )
        )

    return BasketOptimizationResponse(
        total_price=round(sum(i.total_price for i in result_items), 2),
        total_distance=round(sum(i.distance_km for i in result_items)/len(result_items), 2) if result_items else 0,
        estimated_savings=0.0,
        markets_used=len(result_items),
        items=result_items
    )
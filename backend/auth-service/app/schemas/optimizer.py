from pydantic import BaseModel
from typing import List, Optional # Importamos o Optional

class BasketItem(BaseModel):
    product_name: str
    quantity: int = 1

class BasketOptimizationRequest(BaseModel):
    latitude: Optional[float] = None 
    longitude: Optional[float] = None
    radius_km: float = 10
    items: List[BasketItem]
    cep: Optional[str] = None # <--- ESSA LINHA É A CHAVE 

class ProductResult(BaseModel):
    requested_product: str
    matched_product: str
    market_id: int
    market_name: str
    unit_price: float
    quantity: int
    total_price: float
    distance_km: float

class BasketOptimizationResponse(BaseModel):
    total_price: float
    total_distance: float
    estimated_savings: float
    markets_used: int
    items: List[ProductResult]
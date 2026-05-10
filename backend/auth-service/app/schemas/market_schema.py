from pydantic import BaseModel


class MarketCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    city: str | None = None
    state: str | None = None
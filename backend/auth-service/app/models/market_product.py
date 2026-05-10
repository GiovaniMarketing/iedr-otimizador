from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class MarketProduct(Base):
    __tablename__ = "market_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    market_id: Mapped[int] = mapped_column(ForeignKey("markets.id"), index=True)

    product_master_id: Mapped[int] = mapped_column(
        ForeignKey("product_master.id"),
        index=True
    )

    market_product_name: Mapped[str] = mapped_column(String(255), nullable=False)

    barcode: Mapped[str] = mapped_column(String(100), nullable=True)
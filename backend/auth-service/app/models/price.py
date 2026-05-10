from sqlalchemy import Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.models.base import Base


class Price(Base):
    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    market_product_id: Mapped[int] = mapped_column(
        ForeignKey("market_products.id"),
        index=True,
        nullable=False
    )

    price: Mapped[float] = mapped_column(Float, nullable=False)

    promotion_price: Mapped[float] = mapped_column(Float, nullable=True)

    captured_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    source: Mapped[str] = mapped_column(String(50), nullable=True)
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.models.base import Base


class Promotion(Base):
    __tablename__ = "promotions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    market_id: Mapped[int] = mapped_column(ForeignKey("markets.id"), index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    image_url: Mapped[str] = mapped_column(String(500), nullable=True)

    start_date: Mapped[datetime] = mapped_column(DateTime)

    end_date: Mapped[datetime] = mapped_column(DateTime)
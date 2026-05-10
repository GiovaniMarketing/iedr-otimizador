from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class ProductMaster(Base):
    __tablename__ = "product_master"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    universal_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    brand: Mapped[str] = mapped_column(String(120), nullable=True)

    category: Mapped[str] = mapped_column(String(120), nullable=True)

    weight: Mapped[str] = mapped_column(String(50), nullable=True)

    unit: Mapped[str] = mapped_column(String(20), nullable=True)
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.models.base import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
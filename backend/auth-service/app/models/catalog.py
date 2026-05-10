from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class Market(Base):
    __tablename__ = "markets"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Usando string com caminho completo para evitar conflitos
    products = relationship("app.models.catalog.MarketProduct", back_populates="market")

class ProductMaster(Base):
    __tablename__ = "product_master"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    universal_name = Column(String, index=True) 
    category = Column(String, index=True)       
    
    market_versions = relationship("app.models.catalog.MarketProduct", back_populates="master")

class MarketProduct(Base):
    __tablename__ = "market_products"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    market_id = Column(Integer, ForeignKey("markets.id"))
    product_master_id = Column(Integer, ForeignKey("product_master.id"))
    market_product_name = Column(String) 
    
    market = relationship("app.models.catalog.Market", back_populates="products")
    master = relationship("app.models.catalog.ProductMaster", back_populates="market_versions")
    prices = relationship("app.models.catalog.Price", back_populates="market_product")

class Price(Base):
    __tablename__ = "prices"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    market_product_id = Column(Integer, ForeignKey("market_products.id"))
    price = Column(Float)               
    promotion_price = Column(Float, nullable=True) 
    captured_at = Column(DateTime, default=datetime.utcnow)
    
    # Correção: O back_populates deve apontar para o atributo na MarketProduct
    market_product = relationship("app.models.catalog.MarketProduct", back_populates="prices")
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class Tyre(Base):
    __tablename__ = "tyres"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("tyre_brands.id", ondelete="CASCADE"), nullable=False)
    model = Column(String(200), nullable=False)
    size = Column(String(50), nullable=False)
    type = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=False, default=0)
    stock = Column(Integer, nullable=False, default=0)
    min_stock_level = Column(Integer, nullable=False, default=50)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    brand = relationship("TyreBrand", back_populates="tyres")
    order_items = relationship("OrderItem", back_populates="tyre")

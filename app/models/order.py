from sqlalchemy import Column, Float, Integer, Enum as SAEnum, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime, timezone
import uuid

class Order(Base):
    __tablename__="orders"
    
    id=Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    buyer_id=Column(UUID(as_uuid=True),ForeignKey("users.id"),nullable=False)
    listing_id  = Column(UUID(as_uuid=True), ForeignKey("listings.id"), nullable=False)
    quantity=Column(Integer,nullable=False)
    total_price=Column(Float,nullable=False)
    image_urls = Column(JSON, nullable=True)
    status=Column(
        SAEnum("pending", "confirmed", "completed", "cancelled", name="order_status"),
        default="pending"
    )
    created_at    = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    buyer=relationship("User",back_populates="orders")
    listing=relationship("Listing",back_populates="orders")

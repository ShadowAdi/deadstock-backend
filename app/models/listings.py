from sqlalchemy import Column, String, Float, Integer, Enum as SAEnum, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime
import uuid

class Listing(Base):
    __tablename__="listings"
    
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    seller_id=Column(UUID(as_uuid=True))
    title=Column(String,  nullable=False)
    description=Column(String,nullable=True)
    category=Column(String,  nullable=False, index=True)
    quantity=Column(String,nullable=False)
    original_price=Column(Float,nullable=False)
    discount_price = Column(Float, nullable=False)
    city           = Column(String,  nullable=False, index=True)
    status         = Column(
        SAEnum("active", "sold", "closed", name="listing_status"),
        default="active"
    )
    created_at     = Column(DateTime, default=datetime.utcnow)

    seller = relationship("User",  back_populates="listings")
    orders = relationship("Order", back_populates="listing")
    
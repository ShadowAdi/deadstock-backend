from sqlalchemy import Column, String, Enum as SAEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime, timezone
import uuid

class User(Base):
    __tablename__ ="users"
    
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    email=Column(String,unique=True,nullable=False,index=True)
    password = Column(String, nullable=False)
    role          = Column(SAEnum("seller", "buyer", name="user_role"), nullable=False)
    business_name = Column(String, nullable=False)
    city          = Column(String, nullable=False)
    phone         = Column(String, nullable=False)
    created_at    = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    listings=relationship("Listing",back_populates="seller")
    orders=relationship("Order",back_populates="buyer")
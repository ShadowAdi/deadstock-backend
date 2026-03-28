from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum
from .base import BaseResponse

class OrderStatus(str, Enum):
    pending="pending"
    confirmed="confirmed"
    completed = "completed"
    cancelled = "cancelled"

class CreateOrderRequest(BaseModel):
    listing_id: UUID
    quantity: int

class OrderData(BaseModel):
    id: UUID
    buyer_id: UUID
    listing_id: UUID
    quantity: int
    total_price: float
    status:      OrderStatus
    created_at:  datetime
    image_urls: Optional[List[str]] = None
    
    class Config:
        from_attributes=True


class OrderWithListingData(OrderData):      
    listing_title:    str
    listing_city:     str
    seller_name:      str

class OrderResponse(BaseResponse):
    data: Optional[OrderData] = None

class OrdersResponse(BaseResponse):
    data: Optional[List[OrderWithListingData]] = None
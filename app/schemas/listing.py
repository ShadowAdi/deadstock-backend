from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum
from schemas.base import BaseResponse

class ListingStatus(str, Enum):
    active="active"
    sold="sold"
    closed="closed"

class CreateListingRequest(BaseModel):
    title: str
    description: Optional[str]=None
    category: str
    quantity: int
    original_price: float
    discount_price: float
    city:           str

class UpdateListingRequest(BaseModel):
    title:          Optional[str]   = None
    description:    Optional[str]   = None
    quantity:       Optional[int]   = None
    discount_price: Optional[float] = None
    status:         Optional[ListingStatus] = None


class ListingData(BaseModel):
    id:             UUID
    seller_id:      UUID
    title:          str
    description:    Optional[str]
    category:       str
    quantity:       int
    original_price: float
    discount_price: float
    discount_pct:   float           
    city:           str
    status:         ListingStatus
    created_at:     datetime

    class Config:
        from_attributes = True
        
class ListingResponse(BaseResponse):
    data: Optional[ListingData] = None

class ListingsResponse(BaseResponse):
    data: Optional[List[ListingData]] = None
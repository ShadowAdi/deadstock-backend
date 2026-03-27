from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from fastapi import HTTPException, status
from models.listings import Listing
from models.User import User
from schemas.listing import CreateListingRequest, UpdateListingRequest
import logging

logger = logging.getLogger(__name__)

class ListingService:
    def create_listing(self,db:Session,seller:User,data:CreateListingRequest)->Listing:
        if data.discount_price>=data.original_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount price must be lower than original price"
            )
        
        if data.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be at least 1"
            )

        if data.discount_price<=0 or data.original_price<=0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prices must be greater than 0"
            )
        
        listing=Listing(
            seller_id=seller.id,
            title=data.title,
            description    = data.description,
            category       = data.category,
            quantity       = data.quantity,
            original_price = data.original_price,
            discount_price = data.discount_price,
            city           = data.city,
            status         = "active"
        )
        
        db.add(listing)
        db.commit()
        db.refresh(listing)
        
        logger.info(f"Listing {listing.id} created by seller {seller.id}")
        return listing
    
    def get_listing_by_id(self, db: Session, listing_id: str) -> Listing:
        listing = (
            db.query(Listing)
            .options(joinedload(Listing.seller))
            .filter(Listing.id == listing_id)
            .first()
        )

        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found"
            )

        return listing
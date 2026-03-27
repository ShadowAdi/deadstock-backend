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
    
    def get_all_listings(
        self,
        db:         Session,
        category:   str  = None,
        city:       str  = None,
        max_price:  float = None,
        min_price:  float = None,
        q:          str  = None,      
        page:       int  = 1,
        page_size:  int  = 20,
    ) -> dict:

        query = (
            db.query(Listing)
            .options(joinedload(Listing.seller))
            .filter(Listing.status == "active")
        )

        if q:
            query = query.filter(
                or_(
                    Listing.title.ilike(f"%{q}%"),
                    Listing.description.ilike(f"%{q}%")
                )
            )

        if category:
            query = query.filter(Listing.category.ilike(f"%{category}%"))

        if city:
            query = query.filter(Listing.city.ilike(f"%{city}%"))

        if max_price:
            query = query.filter(Listing.discount_price <= max_price)

        if min_price:
            query = query.filter(Listing.discount_price >= min_price)

        total   = query.count()
        offset  = (page - 1) * page_size
        listings = query.order_by(Listing.created_at.desc()).offset(offset).limit(page_size).all()

        return {
            "listings":  listings,
            "total":     total,
            "page":      page,
            "page_size": page_size,
            "pages":     (total + page_size - 1) // page_size
        }
    
    def get_my_listings(
        self,
        db:        Session,
        seller:    User,
        status_filter: str = None    
    ) -> list[Listing]:

        query = db.query(Listing).filter(Listing.seller_id == seller.id)

        if status_filter:
            query = query.filter(Listing.status == status_filter)

        return query.order_by(Listing.created_at.desc()).all()
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from fastapi import HTTPException, status
from models.listings import Listing
from models.User import User
from schemas.listing import CreateListingRequest, UpdateListingRequest
from core.logger import logger

class ListingService:
    def create_listing(self,db:Session,seller:User,data:CreateListingRequest)->Listing:
        if data.discount_price>=data.original_price:
            logger.warning(f"Listing creation failed: discount price {data.discount_price} >= original price {data.original_price} for seller {seller.id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount price must be lower than original price"
            )
        
        if data.quantity <= 0:
            logger.warning(f"Listing creation failed: invalid quantity {data.quantity} provided by seller {seller.id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be at least 1"
            )

        if data.discount_price<=0 or data.original_price<=0:
            logger.warning(f"Listing creation failed: invalid prices (discount: {data.discount_price}, original: {data.original_price}) for seller {seller.id}")
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
            logger.warning(f"Listing {listing_id} not found")
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
    
    
    def update_listing(
        self,
        db:         Session,
        listing_id: str,
        seller:     User,
        data:       UpdateListingRequest
    ) -> Listing:

        listing = db.query(Listing).filter(Listing.id == listing_id).first()

        if not listing:
            logger.warning(f"Update listing failed: listing {listing_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found"
            )

        if str(listing.seller_id) != str(seller.id):
            logger.warning(f"Seller {seller.id} attempted to edit listing {listing_id} they don't own")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own listings"
            )

        if listing.status == "sold":
            logger.warning(f"Update listing failed: listing {listing_id} is already sold, cannot edit")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot edit a listing that is already sold"
            )

        update_data = data.model_dump(exclude_unset=True)  

        new_discount = update_data.get("discount_price", listing.discount_price)
        new_original = update_data.get("original_price", listing.original_price)

        if new_discount >= new_original:
            logger.warning(f"Update listing failed: new discount price {new_discount} >= original price {new_original} for listing {listing_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount price must be lower than original price"
            )

        for field, value in update_data.items():
            setattr(listing, field, value)

        db.commit()
        db.refresh(listing)

        logger.info(f"Listing {listing.id} updated by seller {seller.id}")
        return listing
    
    def delete_listing(self, db: Session, listing_id: str, seller: User) -> bool:
        listing = db.query(Listing).filter(Listing.id == listing_id).first()

        if not listing:
            logger.warning(f"Delete listing failed: listing {listing_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found"
            )

        if str(listing.seller_id) != str(seller.id):
            logger.warning(f"Seller {seller.id} attempted to delete listing {listing_id} they don't own")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own listings"
            )

        if listing.orders:
            listing.status = "closed"
            db.commit()
            logger.info(f"Listing {listing.id} closed (has orders) by seller {seller.id}")
            return "closed"

        db.delete(listing)
        db.commit()

        logger.info(f"Listing {listing.id} deleted by seller {seller.id}")
        return "deleted"
    
    
    def get_nearby_listings(self, db: Session, city: str) -> list[Listing]:
        if not city:
            logger.warning("Get nearby listings failed: city parameter is required")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="City is required"
            )

        listings = (
            db.query(Listing)
            .options(joinedload(Listing.seller))
            .filter(
                Listing.city.ilike(f"%{city}%"),
                Listing.status == "active"
            )
            .order_by(Listing.created_at.desc())
            .limit(50)
            .all()
        )

        return listings
    
    def get_by_category(self, db: Session, category: str) -> list[Listing]:
        listings = (
            db.query(Listing)
            .options(joinedload(Listing.seller))
            .filter(
                Listing.category.ilike(f"%{category}%"),
                Listing.status == "active"
            )
            .order_by(Listing.created_at.desc())
            .all()
        )

        return listings
    
    def compute_discount_pct(self, listing: Listing) -> float:
        if listing.original_price == 0:
            return 0.0
        return round(
            ((listing.original_price - listing.discount_price) / listing.original_price) * 100,
            2
        )


listing_service = ListingService()

    
    
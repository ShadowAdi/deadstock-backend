from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.db import get_db
from app.auth.dependencies import require_seller
from service.listing_service import listing_service
from schemas.listing import (
    CreateListingRequest,
    UpdateListingRequest,
    ListingResponse,
    ListingsResponse,
    ListingData,
)
from schemas.base import BaseResponse
from models.User import User

router = APIRouter(prefix="/listings", tags=["Listings"])

@router.post("/", response_model=ListingResponse, status_code=status.HTTP_201_CREATED)
def create_listing(
    data:   CreateListingRequest,
    seller: User    = Depends(require_seller),
    db:     Session = Depends(get_db)
):
    listing = listing_service.create_listing(db, seller, data)
    return ListingResponse(
        success = True,
        message = "Listing created successfully",
        data    = ListingData(
            **listing.__dict__,
            discount_pct = listing_service.compute_discount_pct(listing)
        )
    )

@router.get("/search", response_model=BaseResponse)
def search_listings(
    q:          Optional[str]   = Query(None, description="Search keyword"),
    category:   Optional[str]   = Query(None),
    city:       Optional[str]   = Query(None),
    min_price:  Optional[float] = Query(None),
    max_price:  Optional[float] = Query(None),
    page:       int             = Query(1,  ge=1),
    page_size:  int             = Query(20, ge=1, le=100),
    db:         Session         = Depends(get_db)
):
    result = listing_service.get_all_listings(
        db, category, city, max_price, min_price, q, page, page_size
    )

    return BaseResponse(
        success = True,
        message = f"{result['total']} listings found",
        data    = {
            "listings": [
                ListingData(
                    **l.__dict__,
                    discount_pct = listing_service.compute_discount_pct(l)
                )
                for l in result["listings"]
            ],
            "pagination": {
                "total":     result["total"],
                "page":      result["page"],
                "page_size": result["page_size"],
                "pages":     result["pages"],
            }
        }
    )
    
@router.get("/nearby", response_model=ListingsResponse)
def get_nearby(
    city: str     = Query(..., description="Your city"),
    db:   Session = Depends(get_db)
):
    listings = listing_service.get_nearby_listings(db, city)
    return ListingsResponse(
        success = True,
        message = f"{len(listings)} listings near {city}",
        data    = [
            ListingData(
                **l.__dict__,
                discount_pct = listing_service.compute_discount_pct(l)
            )
            for l in listings
        ]
    )

@router.get("/category/{category}", response_model=ListingsResponse)
def get_by_category(category: str, db: Session = Depends(get_db)):
    listings = listing_service.get_by_category(db, category)
    return ListingsResponse(
        success = True,
        message = f"{len(listings)} listings in {category}",
        data    = [
            ListingData(
                **l.__dict__,
                discount_pct = listing_service.compute_discount_pct(l)
            )
            for l in listings
        ]
    )


@router.get("/mine", response_model=ListingsResponse)
def get_my_listings(
    status_filter: Optional[str] = Query(None, alias="status"),
    seller:        User           = Depends(require_seller),
    db:            Session        = Depends(get_db)
):
    listings = listing_service.get_my_listings(db, seller, status_filter)
    return ListingsResponse(
        success = True,
        message = f"{len(listings)} listings found",
        data    = [
            ListingData(
                **l.__dict__,
                discount_pct = listing_service.compute_discount_pct(l)
            )
            for l in listings
        ]
    )

@router.get("/{listing_id}", response_model=ListingResponse)
def get_listing(listing_id: str, db: Session = Depends(get_db)):
    listing = listing_service.get_listing_by_id(db, listing_id)
    return ListingResponse(
        success = True,
        message = "Listing fetched",
        data    = ListingData(
            **listing.__dict__,
            discount_pct = listing_service.compute_discount_pct(listing)
        )
    )


@router.patch("/{listing_id}", response_model=ListingResponse)
def update_listing(
    listing_id: str,
    data:       UpdateListingRequest,
    seller:     User    = Depends(require_seller),
    db:         Session = Depends(get_db)
):
    listing = listing_service.update_listing(db, listing_id, seller, data)
    return ListingResponse(
        success = True,
        message = "Listing updated",
        data    = ListingData(
            **listing.__dict__,
            discount_pct = listing_service.compute_discount_pct(listing)
        )
    )


@router.delete("/{listing_id}", response_model=BaseResponse)
def delete_listing(
    listing_id: str,
    seller:     User    = Depends(require_seller),
    db:         Session = Depends(get_db)
):
    result = listing_service.delete_listing(db, listing_id, seller)
    return BaseResponse(
        success = True,
        message = "Listing deleted" if result == "deleted" else "Listing closed (has existing orders)"
    )

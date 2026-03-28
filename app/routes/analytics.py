from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.auth.dependencies import require_seller, get_current_user
from app.service.analytics_service import analytics_service
from app.schemas.base import BaseResponse
from app.models.User import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/trending", response_model=BaseResponse)
def get_trending(db: Session = Depends(get_db)):
    data = analytics_service.get_trending_categories(db)
    return BaseResponse(
        success = True,
        message = "Trending categories fetched",
        data    = data
    )
    
@router.get("/savings", response_model=BaseResponse)
def get_savings(db: Session = Depends(get_db)):
    data = analytics_service.get_total_savings(db)
    return BaseResponse(
        success = True,
        message = "Platform savings fetched",
        data    = data
    )
    
@router.get("/dashboard", response_model=BaseResponse)
def get_dashboard(
    seller: User    = Depends(require_seller),
    db:     Session = Depends(get_db)
):
    data = analytics_service.get_seller_dashboard(db, seller)
    return BaseResponse(
        success = True,
        message = "Dashboard data fetched",
        data    = data
    )
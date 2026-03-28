from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.auth.dependencies import get_current_user
from app.service.user_service import user_service
from app.schemas.user import (
    RegisterRequest, LoginRequest,
    RegisterResponse, LoginResponse,
    ProfileResponse, TokenData, UserData
)
from app.schemas.base import BaseResponse
from app.models.User import User
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/user", tags=["Auth & Users"])

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = user_service.register(db, data)
    return RegisterResponse(
        success = True,
        message = "Account created successfully",
        data    = UserData.model_validate(user)
    )


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    result = user_service.login(db, data)
    return LoginResponse(
        success = True,
        message = "Login successful",
        data    = TokenData(
            access_token = result["access_token"],
            token_type   = result["token_type"],
            user         = UserData.model_validate(result["user"])
        )
    )


@router.get("/me", response_model=ProfileResponse)
def get_my_profile(
    current_user: User    = Depends(get_current_user),
    db:           Session = Depends(get_db)
):
    user = user_service.get_my_profile(db, current_user.id)
    return ProfileResponse(
        success = True,
        message = "Profile fetched",
        data    = UserData.model_validate(user)
    )


class UpdateProfileRequest(BaseModel):
    business_name: Optional[str] = None
    city:          Optional[str] = None
    phone:         Optional[str] = None
    

@router.patch("/me", response_model=ProfileResponse)
def update_profile(
    data:         UpdateProfileRequest,
    current_user: User    = Depends(get_current_user),
    db:           Session = Depends(get_db)
):
    user = user_service.update_profile(db, current_user, data.model_dump())
    return ProfileResponse(
        success = True,
        message = "Profile updated",
        data    = UserData.model_validate(user)
    )

@router.get("/seller/{seller_id}", response_model=BaseResponse)
def get_seller_profile(seller_id: str, db: Session = Depends(get_db)):
    result = user_service.get_seller_profile(db, seller_id)
    return BaseResponse(
        success = True,
        message = "Seller profile fetched",
        data    = {
            "seller":         UserData.model_validate(result["seller"]),
            "listings_count": result["listings_count"]
        }
    )
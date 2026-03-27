from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.User import User
from schemas.user import RegisterRequest, LoginRequest
from auth.utils import hash_password, verify_password, create_access_token
from app.core.logger import logger

class UserService:
    def register(self,db:Session,data:RegisterRequest)->dict:
        existing=db.query(User).filter(User.email==data.email).first()
        if existing:
            logger.error('Email already registered')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if len(data.password) < 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 4 characters"
            )
        
        user = User(
            email         = data.email,
            password_hash = hash_password(data.password),
            role          = data.role,
            business_name = data.business_name,
            city          = data.city,
            phone         = data.phone,
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
        
    
    def login(self, db: Session, data: LoginRequest) -> dict:
        user=db.query(User).filter(User.email==data.email).first()
        
        if not user or not verify_password(data.password, user.password_hash):
            logger.error('Invalid email or password')
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        token = create_access_token(user_id=str(user.id), role=user.role)

        return {
            "access_token": token,
            "token_type":   "bearer",
            "user":         user
        }
    
    def get_my_profile(self, db: Session, user_id: str) -> User:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    def get_public_profile(self, db: Session, user_id: str) -> User:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        return user

    def update_profile(self, db: Session, current_user: User, data: dict) -> User:
        allowed_fields = {"business_name", "city", "phone"}

        for field, value in data.items():
            if field in allowed_fields and value is not None:
                setattr(current_user, field, value)

        db.commit()
        db.refresh(current_user)
        return current_user


    def get_seller_profile(self, db: Session, seller_id: str) -> dict:
        seller = db.query(User).filter(
            User.id   == seller_id,
            User.role == "seller"
        ).first()

        if not seller:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Seller not found"
            )

        return {
            "seller":         seller,
            "listings_count": len([l for l in seller.listings if l.status == "active"])
        }

user_service=UserService()

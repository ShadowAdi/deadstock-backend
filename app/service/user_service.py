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

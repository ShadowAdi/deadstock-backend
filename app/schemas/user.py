from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum
from schemas.base import BaseResponse

class UserRole(str, Enum):
    seller="seller"
    buyer="buyer"
    
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: UserRole
    business_name: str
    city: str
    phone: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class UserData(BaseModel):
    id: UUID
    email: str
    role: UserRole
    business_name: str
    city:          str
    phone:         str
    created_at:    datetime
    
    class Config:
        from_attributes = True
    
class TokenData(BaseModel):
    access_token: str
    token_type:str
    user: UserData

class RegisterResponse(BaseResponse):
    data: Optional[UserData] = None

class LoginResponse(BaseResponse):
    data: Optional[TokenData] = None

class ProfileResponse(BaseResponse):
    data: Optional[UserData] = None
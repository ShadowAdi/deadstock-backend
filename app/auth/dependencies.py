from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from auth.utils import decode_token
from app.db import get_db
from models.User import User
from app.core.logger import logger

bearer=HTTPBearer()

def get_current_user(creds:HTTPAuthorizationCredentials=Depends(bearer),db:Session=Depends(get_db))->User:
    token=creds.credentials
    payload=decode_token(token=token)
    
    if not payload:
        logger.error("Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user=db.query(User).filter(User.id==payload["sub"]).first()
    
    if not user:
        logger.error('User no longer exists')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists"
        )
    
    return user
    
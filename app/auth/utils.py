from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime,timedelta,timezone
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM     = "HS256"
TOKEN_EXPIRE  = 60 * 24 

pwd_context= CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password:str)->str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(user_id: str, role: str) -> str:
    payload = {
        "sub":  str(user_id),
        "role": role,
        "exp":  datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
from datetime import datetime, timezone,timedelta
from typing import Optional
import jwt
from backend.app.utils.config import settings
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

SECRET_KEY = "1CGZhi090Ye07JfGrRz6kMgeb0HSJlERfvFfjd3IjQw"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """Hashing a plain text password before storing it"""
    
    return password_hash.hash(password)

def verify_password(plain_password:str,hashed_password:str)->bool:
    "checking password match"
    return password_hash.verify(plain_password,hashed_password,)

def create_access_token(user_id,role)->str:
    "creating JWT ACCESS TOKEN FOR AUTHENTICATED USER"
    
    expires_at = datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub":str(user_id),
        "sub":role,
        "exp": expires_at
    }
    
    token = jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)
    
    return token

def decode_access_token(token)->dict:
    "verIFY JWT and return its payload"
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    return payload

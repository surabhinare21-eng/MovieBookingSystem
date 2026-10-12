from datetime import datetime, timezone,timedelta
import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher
from pwdlib.exceptions import UnknownHashError

password_hash = PasswordHash([Argon2Hasher(), BcryptHasher()])

SECRET_KEY = "1CGZhi090Ye07JfGrRz6kMgeb0HSJlERfvFfjd3IjQw"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """Hashing a plain text password before storing it"""
    
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check whether a plain-text password matches a stored hash."""
    return password_hash.verify(plain_password, hashed_password)


def verify_password_and_update(
    plain_password: str,
    hashed_password: str,
) -> tuple[bool, str | None]:
    """Verify a password and return a stronger replacement hash when needed."""
    try:
        return password_hash.verify_and_update(plain_password, hashed_password)
    except UnknownHashError:
        # Treat malformed or unsupported stored hashes like invalid credentials.
        # Do not expose hash-format details through the login endpoint.
        return False, None

def create_access_token(user_id,role)->str:
    "creating JWT ACCESS TOKEN FOR AUTHENTICATED USER"
    
    expires_at = datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub":str(user_id),
        "role": role,
        "exp": expires_at
    }
    
    token = jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)
    
    return token

def decode_access_token(token)->dict:
    "verIFY JWT and return its payload"
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    return payload

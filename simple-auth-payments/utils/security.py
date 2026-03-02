from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from config import settings

# Configure password context with explicit bcrypt rounds
# This will automatically upgrade hashes with less than 12 rounds
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__min_rounds=12,  # Minimum acceptable rounds
    bcrypt__default_rounds=12,  # Default rounds for new hashes
    bcrypt__max_rounds=14  # Maximum rounds (for future-proofing)
)


def hash_password(password: str) -> str:
    # Truncate password to 72 bytes for bcrypt compatibility
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Truncate password to 72 bytes for bcrypt compatibility
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)


def verify_and_update_password(plain_password: str, hashed_password: str) -> tuple[bool, Optional[str]]:
    """
    Verify password and check if hash needs upgrade.
    
    Returns:
        tuple: (is_correct, new_hash)
        - is_correct: True if password matches
        - new_hash: New hash if upgrade needed, None otherwise
    """
    # Truncate password to 72 bytes for bcrypt compatibility
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password[:72]
    
    # This automatically checks if the hash needs upgrading
    # (e.g., old bcrypt rounds, deprecated algorithm, etc.)
    is_correct, new_hash = pwd_context.verify_and_update(plain_password, hashed_password)
    
    return is_correct, new_hash


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

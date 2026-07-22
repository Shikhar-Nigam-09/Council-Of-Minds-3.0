from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
from typing import Optional
from app.cache.redis_client import redis_client
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: str | int, expires_delta: Optional[timedelta] = None, jti: Optional[str] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    if jti:
        to_encode["jti"] = jti
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: str | int, expires_delta: Optional[timedelta] = None, jti: Optional[str] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    if jti:
        to_encode["jti"] = jti
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

async def is_jti_blacklisted(jti: str) -> bool:
    if not jti:
        return False
    client = redis_client.get_client()
    if not client:
        return False
    try:
        val = await client.get(f"blacklist:{jti}")
        return val is not None
    except Exception as e:
        logger.warning(f"Failed to check blacklist: {e}")
        return False

async def blacklist_jti(jti: str, exp_timestamp: int) -> None:
    if not jti:
        return
    client = redis_client.get_client()
    if not client:
        return
    try:
        now = int(datetime.utcnow().timestamp())
        ttl = max(0, exp_timestamp - now)
        if ttl > 0:
            await client.setex(f"blacklist:{jti}", ttl, "1")
    except Exception as e:
        logger.warning(f"Failed to blacklist jti: {e}")

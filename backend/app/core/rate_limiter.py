import time
import logging
from fastapi import Request, HTTPException, status
from app.cache.redis_client import redis_client
from app.core.config import settings

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, category: str, requests: int, window: int):
        self.category = category
        self.requests = requests
        self.window = window

    async def __call__(self, request: Request):
        client = redis_client.get_client()
        if not client:
            return  # Fail open if no redis

        identifier = request.client.host if request.client else "unknown_ip"
        
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            from jose import jwt
            try:
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM], options={"verify_exp": False})
                if sub := payload.get("sub"):
                    identifier = sub
            except Exception:
                pass

        key = f"ratelimit:{self.category}:{identifier}"
        
        try:
            current = await client.get(key)
            if current and int(current) >= self.requests:
                ttl = await client.ttl(key)
                headers = {"Retry-After": str(ttl if ttl > 0 else self.window)}
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too Many Requests",
                    headers=headers
                )
            
            pipe = client.pipeline()
            pipe.incr(key)
            if not current:
                pipe.expire(key, self.window)
            await pipe.exec()
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"RateLimiter Redis error, failing open: {e}")

rate_limit_general = RateLimiter("general", settings.RATE_LIMIT_GENERAL_PER_MINUTE, 60)
rate_limit_upload = RateLimiter("upload", settings.RATE_LIMIT_UPLOAD_PER_HOUR, 3600)
rate_limit_llm = RateLimiter("llm", settings.RATE_LIMIT_LLM_PER_HOUR, 3600)

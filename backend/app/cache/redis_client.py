import logging
from upstash_redis.asyncio import Redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    _client: Redis | None = None
    _mock_mode: bool = False

    @classmethod
    def get_client(cls) -> Redis | None:
        if not settings.UPSTASH_REDIS_REST_URL or not settings.UPSTASH_REDIS_REST_TOKEN:
            if not cls._mock_mode:
                logger.warning("UPSTASH_REDIS_REST_URL or TOKEN is not set. Cache/RateLimiting/CostGuardrail will fail open (mock mode).")
                cls._mock_mode = True
            return None
            
        if cls._client is None:
            cls._client = Redis(
                url=settings.UPSTASH_REDIS_REST_URL, 
                token=settings.UPSTASH_REDIS_REST_TOKEN
            )
            
        return cls._client

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.close()
            cls._client = None

redis_client = RedisClient()

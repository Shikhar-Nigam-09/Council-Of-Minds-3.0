import logging
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    _pool: redis.ConnectionPool | None = None
    _client: redis.Redis | None = None
    _mock_mode: bool = False

    @classmethod
    def get_client(cls) -> redis.Redis | None:
        if not settings.REDIS_URL:
            if not cls._mock_mode:
                logger.warning("REDIS_URL is not set. Cache/RateLimiting/CostGuardrail will fail open (mock mode).")
                cls._mock_mode = True
            return None
            
        if cls._pool is None:
            cls._pool = redis.ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)
            cls._client = redis.Redis(connection_pool=cls._pool)
            
        return cls._client

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.aclose()
            cls._client = None
        if cls._pool:
            await cls._pool.disconnect()
            cls._pool = None

redis_client = RedisClient()

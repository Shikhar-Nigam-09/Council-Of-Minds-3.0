import pytest
from app.core.rate_limiter import RateLimiter
from fastapi import Request
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_rate_limiter_fail_open():
    limiter = RateLimiter("test", 10, 60)
    mock_request = AsyncMock(spec=Request)
    mock_request.client.host = "127.0.0.1"
    
    with patch("app.cache.redis_client.redis_client.get_client", return_value=None):
        await limiter(mock_request)

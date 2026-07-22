import pytest
import uuid
from app.core.cost_guardrail import check_and_reserve
from unittest.mock import patch

@pytest.mark.asyncio
async def test_cost_guardrail_fail_open():
    user_id = uuid.uuid4()
    with patch("app.cache.redis_client.redis_client.get_client", return_value=None):
        await check_and_reserve(user_id, 100.0)

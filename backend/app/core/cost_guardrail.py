import logging
import time
from fastapi import HTTPException, status
from app.cache.redis_client import redis_client
from app.core.config import settings
import uuid

logger = logging.getLogger(__name__)

async def check_and_reserve(user_id: uuid.UUID, estimated_cost: float) -> None:
    client = redis_client.get_client()
    if not client:
        return
        
    try:
        date_str = time.strftime("%Y-%m-%d")
        key = f"cost_guardrail:{user_id}:{date_str}"
        
        current = await client.get(key)
        current_spend = float(current) if current else 0.0
        
        if current_spend + estimated_cost > settings.DAILY_COST_CAP_USD:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Daily cost cap of ${settings.DAILY_COST_CAP_USD:.2f} exceeded."
            )
            
        await client.incrbyfloat(key, estimated_cost)
        if not current:
            await client.expire(key, 86400 * 2)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"CostGuardrail Redis error, failing open: {e}")

import hashlib
import json
import logging
from typing import Dict, Any, Optional
from app.cache.redis_client import redis_client

logger = logging.getLogger(__name__)

PLANNER_CACHE_TTL = 3600  # 1 hour

def _get_cache_key(document_id: str, question: str) -> str:
    normalized_q = question.lower().strip()
    key_input = f"{document_id}:{normalized_q}".encode("utf-8")
    hashed_key = hashlib.sha256(key_input).hexdigest()
    return f"planner_cache:{hashed_key}"

async def get_planner_recommendation(document_id: str, question: str) -> Optional[Dict[str, Any]]:
    client = redis_client.get_client()
    if not client:
        return None
        
    try:
        key = _get_cache_key(document_id, question)
        cached_val = await client.get(key)
        if cached_val:
            logger.info(f"Planner cache hit for document {document_id}")
            return json.loads(cached_val)
    except Exception as e:
        logger.warning(f"Failed to read from planner cache: {e}")
        
    return None

async def set_planner_recommendation(document_id: str, question: str, recommendation: Dict[str, Any]) -> None:
    client = redis_client.get_client()
    if not client:
        return
        
    try:
        key = _get_cache_key(document_id, question)
        await client.setex(key, PLANNER_CACHE_TTL, json.dumps(recommendation))
    except Exception as e:
        logger.warning(f"Failed to write to planner cache: {e}")

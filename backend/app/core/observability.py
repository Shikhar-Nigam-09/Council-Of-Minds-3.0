import logging
from functools import wraps
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from langsmith import traceable
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False

def trace_llm_call(run_type="llm", name=None):
    def decorator(func):
        if LANGSMITH_AVAILABLE and settings.LANGSMITH_API_KEY:
            return traceable(run_type=run_type, name=name or func.__name__)(func)
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not getattr(wrapper, "_warned", False):
                    logger.warning(f"LangSmith API Key missing or langsmith not installed. Trace for {func.__name__} skipped.")
                    wrapper._warned = True
                return func(*args, **kwargs)
            
            import asyncio
            if asyncio.iscoroutinefunction(func):
                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    if not getattr(async_wrapper, "_warned", False):
                        logger.warning(f"LangSmith API Key missing or langsmith not installed. Trace for {func.__name__} skipped.")
                        async_wrapper._warned = True
                    return await func(*args, **kwargs)
                return async_wrapper
            return wrapper
    return decorator

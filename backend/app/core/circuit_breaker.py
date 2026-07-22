import time
import logging
from functools import wraps
from app.core.config import settings

logger = logging.getLogger(__name__)

class CircuitBreakerException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, name: str, failure_threshold: int, cooldown_seconds: int):
        self.name = name
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.failures = 0
        self.last_failure_time = 0
        self.state = "CLOSED" 

    def _update_state(self):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.cooldown_seconds:
                self.state = "HALF_OPEN"
                logger.info(f"Circuit Breaker {self.name} transitioned to HALF_OPEN")

    def __call__(self, func):
        import asyncio
        import inspect
        
        if inspect.isasyncgenfunction(func):
            @wraps(func)
            async def async_gen_wrapper(*args, **kwargs):
                self._update_state()
                if self.state == "OPEN":
                    raise CircuitBreakerException(f"Circuit {self.name} is OPEN")
                
                try:
                    async for item in func(*args, **kwargs):
                        yield item
                    if self.state == "HALF_OPEN":
                        self.state = "CLOSED"
                        self.failures = 0
                        logger.info(f"Circuit Breaker {self.name} transitioned to CLOSED")
                except Exception as e:
                    self.failures += 1
                    self.last_failure_time = time.time()
                    if self.failures >= self.failure_threshold:
                        self.state = "OPEN"
                        logger.error(f"Circuit Breaker {self.name} transitioned to OPEN due to: {e}")
                    raise
            return async_gen_wrapper
        elif asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                self._update_state()
                if self.state == "OPEN":
                    raise CircuitBreakerException(f"Circuit {self.name} is OPEN")
                
                try:
                    result = await func(*args, **kwargs)
                    if self.state == "HALF_OPEN":
                        self.state = "CLOSED"
                        self.failures = 0
                        logger.info(f"Circuit Breaker {self.name} transitioned to CLOSED")
                    return result
                except Exception as e:
                    self.failures += 1
                    self.last_failure_time = time.time()
                    if self.failures >= self.failure_threshold:
                        self.state = "OPEN"
                        logger.error(f"Circuit Breaker {self.name} transitioned to OPEN due to: {e}")
                    raise
            return async_wrapper
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                self._update_state()
                if self.state == "OPEN":
                    raise CircuitBreakerException(f"Circuit {self.name} is OPEN")
                
                try:
                    result = func(*args, **kwargs)
                    if self.state == "HALF_OPEN":
                        self.state = "CLOSED"
                        self.failures = 0
                        logger.info(f"Circuit Breaker {self.name} transitioned to CLOSED")
                    return result
                except Exception as e:
                    self.failures += 1
                    self.last_failure_time = time.time()
                    if self.failures >= self.failure_threshold:
                        self.state = "OPEN"
                        logger.error(f"Circuit Breaker {self.name} transitioned to OPEN due to: {e}")
                    raise
            return wrapper

def with_circuit_breaker(name: str):
    return CircuitBreaker(
        name=name, 
        failure_threshold=settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD, 
        cooldown_seconds=settings.CIRCUIT_BREAKER_COOLDOWN_SECONDS
    )

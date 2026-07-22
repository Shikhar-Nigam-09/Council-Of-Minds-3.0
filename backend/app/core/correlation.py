import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar

request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="")

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_ctx_var.set(req_id)
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        
        request_id_ctx_var.reset(token)
        return response

class CorrelationIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx_var.get()
        return True

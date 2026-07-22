from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from app.api.v1.evaluation import router as evaluation_router
from app.core.exceptions import AppError, app_error_handler, generic_exception_handler
from app.core.logging import setup_logging
from app.core.correlation import CorrelationIdMiddleware
from app.core.security_headers import SecurityHeadersMiddleware

logger = setup_logging()

import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from contextlib import asynccontextmanager
from app.graph.checkpointer import close_checkpointer

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("STARTUP: Starting lifespan handler")
    # Checkpointer is now lazy-loaded on first use
    logger.info("STARTUP: Lifespan setup complete")
    yield
    # Teardown checkpointer
    await close_checkpointer()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CorrelationIdMiddleware)

# CORS configuration
if settings.get_cors_origins():
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Exception handlers
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(evaluation_router, prefix="/api/v1")

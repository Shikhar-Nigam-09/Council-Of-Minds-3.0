from fastapi import APIRouter
from app.api.v1 import auth, health, documents, conversations

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])

from app.core.config import settings
from .base import VectorStoreProvider
from .qdrant_provider import QdrantProvider
from .in_memory_provider import InMemoryProvider

_in_memory_store = InMemoryProvider()

def get_vectorstore_provider() -> VectorStoreProvider:
    if settings.QDRANT_URL and settings.QDRANT_API_KEY:
        return QdrantProvider(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            collection_name=settings.QDRANT_COLLECTION_NAME
        )
    return _in_memory_store

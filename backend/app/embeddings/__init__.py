from app.core.config import settings
from .base import EmbeddingProvider
from .huggingface_provider import HuggingFaceEmbeddingProvider
from .mock_provider import MockEmbeddingProvider

def get_embedding_provider() -> EmbeddingProvider:
    if settings.HUGGINGFACE_API_KEY:
        return HuggingFaceEmbeddingProvider(
            api_key=settings.HUGGINGFACE_API_KEY, 
            model_id=settings.HUGGINGFACE_EMBEDDING_MODEL
        )
    return MockEmbeddingProvider()

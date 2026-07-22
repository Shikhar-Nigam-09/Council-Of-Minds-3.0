import hashlib
from typing import List
from app.embeddings.base import EmbeddingProvider

class MockEmbeddingProvider(EmbeddingProvider):
    @property
    def dimension(self) -> int:
        return 384

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            h = hashlib.sha256(text.encode('utf-8')).digest()
            vec = [(b / 128.0) - 1.0 for b in h]
            full_vec = (vec * (384 // len(vec) + 1))[:384]
            embeddings.append(full_vec)
        return embeddings

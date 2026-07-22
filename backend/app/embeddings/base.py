from abc import ABC, abstractmethod
from typing import List

class EmbeddingProvider(ABC):
    @property
    @abstractmethod
    def dimension(self) -> int:
        pass

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        pass

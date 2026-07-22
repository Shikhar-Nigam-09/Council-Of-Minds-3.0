from abc import ABC, abstractmethod
from typing import List, Dict, Any

class VectorStoreProvider(ABC):
    @abstractmethod
    def ensure_collection(self, dimension: int) -> None:
        pass

    @abstractmethod
    def upsert_chunks(self, document_id: str, chunks_with_vectors: List[Dict[str, Any]]) -> None:
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        pass

    @abstractmethod
    def search(self, query_vector: List[float], top_k: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        pass

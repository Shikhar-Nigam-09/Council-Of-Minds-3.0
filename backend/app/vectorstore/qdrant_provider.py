from typing import List, Dict, Any, Optional
import logging
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from app.vectorstore.base import VectorStoreProvider
from app.core.exceptions import AppError
from app.core.circuit_breaker import with_circuit_breaker

logger = logging.getLogger(__name__)

class QdrantProvider(VectorStoreProvider):
    def __init__(self, url: str, api_key: str, collection_name: str):
        self.client = QdrantClient(url=url, api_key=api_key)
        self.collection_name = collection_name

    @with_circuit_breaker("qdrant")
    def ensure_collection(self, dimension: int) -> None:
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection_name for c in collections):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
            )

    @with_circuit_breaker("qdrant")
    def upsert_chunks(self, document_id: str, chunks_with_vectors: List[Dict[str, Any]]) -> None:
        if not chunks_with_vectors:
            return
            
        points = []
        for c in chunks_with_vectors:
            payload = c.copy()
            vector = payload.pop("vector")
            points.append(
                PointStruct(
                    id=c["vector_id"],
                    vector=vector,
                    payload=payload
                )
            )
        self.client.upsert(collection_name=self.collection_name, points=points)

    @with_circuit_breaker("qdrant")
    def delete_document(self, document_id: str) -> None:
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
            )
        )

    @with_circuit_breaker("qdrant")
    def search(self, query_vector: List[float], top_k: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        qdrant_filter = None
        if filters:
            must_conditions = []
            for k, v in filters.items():
                must_conditions.append(FieldCondition(key=k, match=MatchValue(value=v)))
            qdrant_filter = Filter(must=must_conditions)
            
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=qdrant_filter
        )
        
        results = []
        for point in search_result:
            # point.id is the vector_id, but the payload might also contain 'vector_id' and other metadata
            res = point.payload.copy() if point.payload else {}
            res["id"] = str(point.id)  # Qdrant's ID is the vector_id
            res["score"] = point.score
            results.append(res)
            
        return results

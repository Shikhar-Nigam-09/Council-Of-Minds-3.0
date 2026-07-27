from typing import List, Dict, Any, Optional
import logging
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, PayloadSchemaType

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
            
        # Ensure the payload index exists for document_id (idempotent operation)
        logger.info(f"[QdrantProvider] Creating/verifying payload index for 'document_id' on collection: '{self.collection_name}'")
        try:
            res = self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="document_id",
                field_schema=PayloadSchemaType.KEYWORD,
            )
            logger.info(f"[QdrantProvider] Payload index successfully created or verified. Response: {res}")
        except Exception as e:
            logger.error(f"[QdrantProvider] EXACT EXCEPTION during create_payload_index: {repr(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
        try:
            info = self.client.get_collection(self.collection_name)
            logger.info(f"[QdrantProvider] Collection info payload_schema: {info.payload_schema}")
        except Exception as e:
            logger.error(f"[QdrantProvider] Failed to fetch collection info: {e}")

    @with_circuit_breaker("qdrant")
    def upsert_chunks(self, document_id: str, chunks_with_vectors: List[Dict[str, Any]]) -> None:
        logger.info(f"[QdrantProvider] upsert_chunks called for document_id: {document_id}, collection: '{self.collection_name}'")
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
            
        if len(points) > 0:
            logger.info(f"[QdrantProvider] Sample payload being upserted: {points[0].payload}")
            
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
        logger.info(f"[QdrantProvider] search called on collection: '{self.collection_name}', top_k: {top_k}, filters: {filters}")
        qdrant_filter = None
        if filters:
            must_conditions = []
            for k, v in filters.items():
                must_conditions.append(FieldCondition(key=k, match=MatchValue(value=v)))
            qdrant_filter = Filter(must=must_conditions)
            logger.info(f"[QdrantProvider] Executing query_points with filter: {qdrant_filter}")
            
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            query_filter=qdrant_filter
        )
        
        results = []
        for point in search_result.points:
            # point.id is the vector_id, but the payload might also contain 'vector_id' and other metadata
            res = point.payload.copy() if point.payload else {}
            res["id"] = str(point.id)  # Qdrant's ID is the vector_id
            res["score"] = point.score
            results.append(res)
            
        return results

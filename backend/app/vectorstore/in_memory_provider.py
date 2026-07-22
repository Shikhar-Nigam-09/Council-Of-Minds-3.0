import os
import json
from typing import List, Dict, Any
from app.vectorstore.base import VectorStoreProvider

class InMemoryProvider(VectorStoreProvider):
    def __init__(self, file_path: str = ".local_vectorstore.json"):
        self.file_path = file_path
        self.store = {}
        self.dimension = None
        self.last_mtime = 0
        self._load()

    def _load(self):
        if os.path.exists(self.file_path):
            current_mtime = os.path.getmtime(self.file_path)
            if current_mtime == self.last_mtime:
                return  # Skip loading, we already have the latest data
            
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.store = json.load(f)
                self.last_mtime = current_mtime
            except Exception:
                self.store = {}
        else:
            self.store = {}
            self.last_mtime = 0

    def _save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.store, f)
        if os.path.exists(self.file_path):
            self.last_mtime = os.path.getmtime(self.file_path)

    def ensure_collection(self, dimension: int) -> None:
        self.dimension = dimension

    def upsert_chunks(self, document_id: str, chunks_with_vectors: List[Dict[str, Any]]) -> None:
        self._load()
        for c in chunks_with_vectors:
            payload = c.copy()
            vector = payload.pop("vector")
            self.store[c["vector_id"]] = {
                "vector": vector,
                "payload": payload
            }
        self._save()

    def delete_document(self, document_id: str) -> None:
        self._load()
        ids_to_delete = [
            vid for vid, data in self.store.items()
            if data["payload"].get("document_id") == document_id
        ]
        for vid in ids_to_delete:
            del self.store[vid]
        if ids_to_delete:
            self._save()

    def search(self, query_vector: List[float], top_k: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        self._load()
        import math
        def dot_product(v1, v2):
            return sum(x*y for x, y in zip(v1, v2))
        def magnitude(v):
            return math.sqrt(sum(x*x for x in v))
            
        results = []
        for vid, data in self.store.items():
            if filters:
                # Basic strict match for single-level dictionary filters
                skip = False
                for k, v in filters.items():
                    if k in data["payload"] and data["payload"][k] != v:
                        skip = True
                        break
                if skip:
                    continue
                    
            v2 = data["vector"]
            mag1 = magnitude(query_vector)
            mag2 = magnitude(v2)
            if mag1 == 0 or mag2 == 0:
                sim = 0
            else:
                sim = dot_product(query_vector, v2) / (mag1 * mag2)
            results.append({"id": vid, "score": sim, "payload": data["payload"]})
            
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

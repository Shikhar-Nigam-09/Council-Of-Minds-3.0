import time
import requests
import logging
from typing import List
from app.embeddings.base import EmbeddingProvider
from app.core.exceptions import AppError
from app.core.circuit_breaker import with_circuit_breaker

logger = logging.getLogger(__name__)

class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str = None, model_id: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_id = model_id
        self.api_key = api_key
        self.is_local = not bool(api_key)

        if self.is_local:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_id)
            except ImportError:
                raise AppError("EMBEDDING_INIT_FAILED", "sentence_transformers is not installed. Install it to use local models.", status_code=500)
            except Exception as e:
                logger.error(f"Failed to load embedding model {model_id}: {e}")
                raise AppError("EMBEDDING_INIT_FAILED", f"Could not load model {model_id}", status_code=500)
        else:
            self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.model_id}"
            self.headers = {"Authorization": f"Bearer {self.api_key}"}

    @property
    def dimension(self) -> int:
        return 384

    @with_circuit_breaker("huggingface")
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
            
        if self.is_local:
            try:
                embeddings = self.model.encode(texts)
                return embeddings.tolist() if hasattr(embeddings, 'tolist') else embeddings
            except Exception as e:
                logger.error(f"Local embedding failed: {e}")
                raise AppError("EMBEDDING_FAILED", "Failed to generate local embeddings", status_code=500)
        else:
            return self._call_api_with_retry(texts)

    def _call_api_with_retry(self, payload: List[str], max_retries: int = 3) -> List[List[float]]:
        for attempt in range(max_retries):
            try:
                response = requests.post(self.api_url, headers=self.headers, json={"inputs": payload, "options": {"wait_for_model": True}})
                if response.status_code == 200:
                    return response.json()
                elif response.status_code in [429, 500, 503]:
                    logger.warning(f"Transient error {response.status_code} from HF API. Retrying...")
                    time.sleep(2 ** attempt)
                    continue
                else:
                    raise AppError("EMBEDDING_FAILED", f"HuggingFace API error: {response.text}", status_code=500)
            except requests.RequestException as e:
                logger.warning(f"Request failed: {e}. Retrying...")
                time.sleep(2 ** attempt)
        
        raise AppError("EMBEDDING_FAILED", "Failed to get embeddings after retries.", status_code=500)

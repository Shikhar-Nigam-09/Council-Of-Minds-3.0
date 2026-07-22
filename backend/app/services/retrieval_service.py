import logging
import asyncio
from typing import List
from app.embeddings import get_embedding_provider
from app.vectorstore import get_vectorstore_provider
from app.core.config import settings

logger = logging.getLogger(__name__)

class RetrievalService:
    @staticmethod
    def _is_summarization_query(question: str) -> bool:
        keywords = ["summarize", "summary", "overview", "explain", "report", "everything"]
        q = question.lower()
        return any(k in q for k in keywords)

    @staticmethod
    async def retrieve_chunks(document_id: str, question: str, top_k: int = None) -> List[str]:
        if not document_id:
            logger.error("Missing document_id")
            return []
            
        embedder = get_embedding_provider()
        vstore = get_vectorstore_provider()
        
        query_vector = await asyncio.to_thread(embedder.embed_texts, [question])
        if not query_vector:
            raise ValueError("Embedding returned empty list")
        query_vector = query_vector[0]
        
        is_summary = RetrievalService._is_summarization_query(question)
        if top_k is None:
            top_k = 12 if is_summary else getattr(settings, "RETRIEVAL_TOP_K", 8)
            
        filters = {"document_id": document_id}
        
        fetch_k = max(top_k * 3, 40) if is_summary else top_k
        
        results = await asyncio.to_thread(
            vstore.search, 
            query_vector=query_vector, 
            top_k=fetch_k, 
            filters=filters
        )
        
        if is_summary and results:
            from collections import defaultdict
            page_groups = defaultdict(list)
            for res in results:
                page = res.get("payload", {}).get("page_number", 1)
                page_groups[page].append(res)
                
            selected = []
            pages = sorted(list(page_groups.keys()))
            page_indices = {p: 0 for p in pages}
            
            while len(selected) < top_k:
                added_this_round = False
                for p in pages:
                    if len(selected) >= top_k:
                        break
                    idx = page_indices[p]
                    if idx < len(page_groups[p]):
                        selected.append(page_groups[p][idx])
                        page_indices[p] += 1
                        added_this_round = True
                if not added_this_round:
                    break
            results = selected
            
        logger.info(f"Top-K selected: {len(results)}")
        for i, res in enumerate(results):
            score = res.get('score', 0)
            page = res.get('payload', {}).get('page_number', 'Unknown')
            preview = res.get('payload', {}).get('content', '')[:50].replace('\n', ' ')
            logger.info(f"[{i+1}] Score: {score:.4f} | Page: {page} | Preview: {preview}...")
            
        chunk_ids = [res.get("id") for res in results]
        return chunk_ids

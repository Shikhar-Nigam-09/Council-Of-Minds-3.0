import uuid
import logging
from typing import List, Dict, Any
from app.models.chunk import Chunk, ChunkType, SourceType

logger = logging.getLogger(__name__)

class ChunkingService:
    @staticmethod
    def chunk_extractions(document_id: str, extractions: List[Dict[str, Any]]) -> List[Chunk]:
        chunks = []
        chunk_idx = 0
        
        for item in extractions:
            content = item.get("content", "")
            if not content:
                continue
                
            if item.get("type") == "text" and len(content) > 1000:
                parts = ChunkingService._split_text(content, chunk_size=200, overlap=50) # using smaller chunks in words
            else:
                parts = [content]
                
            for part in parts:
                chunks.append(
                    Chunk(
                        document_id=document_id,
                        chunk_index=chunk_idx,
                        chunk_type=ChunkType(item["type"]),
                        source_type=SourceType(item["source_type"]),
                        page_number=item.get("page_number", 1),
                        section_title=item.get("section_title"),
                        content=part,
                        caption_pending=item.get("caption_pending", False),
                        vector_id=str(uuid.uuid4())
                    )
                )
                chunk_idx += 1
                
        return chunks
        
    @staticmethod
    def _split_text(text: str, chunk_size: int, overlap: int) -> List[str]:
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk_words = words[i:i + chunk_size]
            chunks.append(" ".join(chunk_words))
            if i + chunk_size >= len(words):
                break
            i += (chunk_size - overlap)
        return chunks

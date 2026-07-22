import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.chunk import ChunkType, SourceType

class ChunkBase(BaseModel):
    chunk_index: int
    chunk_type: ChunkType
    source_type: SourceType
    page_number: int
    section_title: Optional[str] = None
    content: str
    caption_pending: bool
    vector_id: str
    created_at: datetime

class ChunkRead(ChunkBase):
    id: uuid.UUID
    document_id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.document import DocumentStatus

class DocumentBase(BaseModel):
    filename: str
    file_size_bytes: int
    status: DocumentStatus
    error_message: Optional[str] = None
    page_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime

class DocumentRead(DocumentBase):
    id: uuid.UUID
    user_id: uuid.UUID
    storage_url: str
    
    model_config = ConfigDict(from_attributes=True)

class DocumentListItem(DocumentBase):
    id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)

class DocumentUploadResponse(BaseModel):
    id: uuid.UUID
    filename: str
    status: DocumentStatus

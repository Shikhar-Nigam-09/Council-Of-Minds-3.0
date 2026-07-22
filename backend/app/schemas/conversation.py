from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.message import MessageRole, MessageStatus

class MessageBase(BaseModel):
    role: MessageRole
    content: str

class MessageRead(MessageBase):
    id: UUID
    conversation_id: UUID
    graph_thread_id: Optional[str] = None
    status: Optional[MessageStatus] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ConversationBase(BaseModel):
    title: Optional[str] = None

class ConversationRead(ConversationBase):
    id: UUID
    user_id: UUID
    document_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

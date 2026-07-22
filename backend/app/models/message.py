import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Enum, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"

class MessageStatus(str, enum.Enum):
    awaiting_confirmation = "awaiting_confirmation"
    confirmed = "confirmed"
    completed = "completed"

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    graph_thread_id: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[MessageStatus | None] = mapped_column(Enum(MessageStatus), nullable=True)
    
    final_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    synthesis_model: Mapped[str | None] = mapped_column(String, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_messages_conversation_id", "conversation_id"),
    )

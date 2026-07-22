import uuid
import enum
from datetime import datetime
from sqlalchemy import Enum, DateTime, ForeignKey, Index, Text, Integer, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base_class import Base

class AgentName(str, enum.Enum):
    logical = "logical"
    practical = "practical"
    analytical = "analytical"
    skeptical = "skeptical"
    ethics = "ethics"

class AgentStatus(str, enum.Enum):
    success = "success"
    failed = "failed"

class AgentOutput(Base):
    __tablename__ = "agent_outputs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    agent_name: Mapped[AgentName] = mapped_column(Enum(AgentName), nullable=False)
    status: Mapped[AgentStatus] = mapped_column(Enum(AgentStatus), nullable=False)
    
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_points: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    weight_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    included_in_synthesis: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_agent_outputs_message_id_agent_name", "message_id", "agent_name"),
    )

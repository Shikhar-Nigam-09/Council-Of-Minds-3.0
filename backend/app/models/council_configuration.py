import uuid
import enum
from datetime import datetime
from sqlalchemy import Enum, DateTime, ForeignKey, Integer, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class ConfigurationSource(str, enum.Enum):
    ai_recommendation = "ai_recommendation"
    balanced_fallback = "balanced_fallback"
    user_confirmed = "user_confirmed"

class CouncilConfiguration(Base):
    __tablename__ = "council_configurations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, unique=True)
    source: Mapped[ConfigurationSource] = mapped_column(Enum(ConfigurationSource), nullable=False)
    
    logical_weight: Mapped[int] = mapped_column(Integer, default=20)
    practical_weight: Mapped[int] = mapped_column(Integer, default=20)
    analytical_weight: Mapped[int] = mapped_column(Integer, default=20)
    skeptical_weight: Mapped[int] = mapped_column(Integer, default=20)
    ethics_weight: Mapped[int] = mapped_column(Integer, default=20)
    
    logical_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    practical_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    analytical_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    skeptical_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    ethics_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    
    model_name: Mapped[str] = mapped_column(String, nullable=False, server_default="unknown")
    prompt_version: Mapped[str] = mapped_column(String, nullable=False, server_default="unknown")
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

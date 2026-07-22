import uuid
import enum
from sqlalchemy import Column, ForeignKey, Integer, Numeric, Text, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base_class import Base
from sqlalchemy.sql import func

class JudgeStatus(str, enum.Enum):
    success = "success"
    failed = "failed"

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    
    single_agent_answer = Column(Text)
    single_agent_citations = Column(JSONB)
    single_agent_latency_ms = Column(Integer)
    single_agent_cost_estimate = Column(Numeric)
    
    council_answer = Column(Text)
    council_citations = Column(JSONB)
    council_latency_ms = Column(Integer)
    council_cost_estimate = Column(Numeric)
    
    judge_status = Column(Enum(JudgeStatus))
    judge_verdict = Column(JSONB, nullable=True)
    judge_latency_ms = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

from pydantic import BaseModel, UUID4
from typing import Dict, Any, Optional
from datetime import datetime
from app.models.evaluation_run import JudgeStatus

class EvaluationRunCreate(BaseModel):
    document_id: UUID4
    question: str
    single_agent_answer: str
    single_agent_citations: Optional[Dict[str, Any]] = None
    single_agent_latency_ms: int
    single_agent_cost_estimate: float
    council_answer: str
    council_citations: Optional[Dict[str, Any]] = None
    council_latency_ms: int
    council_cost_estimate: float
    judge_status: JudgeStatus
    judge_verdict: Optional[Dict[str, Any]] = None
    judge_latency_ms: Optional[int] = None

class EvaluationRunRead(EvaluationRunCreate):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    
    class Config:
        from_attributes = True

class JudgeScores(BaseModel):
    quality_score: int
    completeness_score: int
    citation_quality_score: int
    reasoning: str

class JudgeVerdict(BaseModel):
    single_agent: JudgeScores
    council: JudgeScores
    comparative_verdict: str

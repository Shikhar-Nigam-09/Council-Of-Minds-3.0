import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.evaluation_run import EvaluationRunRead
from app.services.evaluation_service import EvaluationService
from app.repositories.evaluation_run_repository import EvaluationRunRepository
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import logging
from app.core.rate_limiter import rate_limit_llm, rate_limit_general
from app.core.cost_guardrail import check_and_reserve
from app.core.pricing import get_estimated_run_cost

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/evaluation", tags=["evaluation"], dependencies=[Depends(rate_limit_general)])

class EvaluationRequest(BaseModel):
    document_id: uuid.UUID
    question: str

@router.post("/run", response_model=EvaluationRunRead, dependencies=[Depends(rate_limit_llm)])
async def run_evaluation(
    request: EvaluationRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        await check_and_reserve(current_user.id, get_estimated_run_cost())
        run = await EvaluationService.run_evaluation(request.document_id, request.question, current_user.id)
        return run
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/runs", response_model=List[EvaluationRunRead])
async def list_runs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = EvaluationRunRepository(db)
    runs = await repo.list_for_user(current_user.id, skip, limit)
    return runs

@router.get("/runs/{run_id}", response_model=EvaluationRunRead)
async def get_run(
    run_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = EvaluationRunRepository(db)
    run = await repo.get_by_id_for_user(run_id, current_user.id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run

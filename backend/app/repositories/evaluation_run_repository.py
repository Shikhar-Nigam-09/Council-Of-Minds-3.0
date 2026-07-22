import uuid
from typing import List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.evaluation_run import EvaluationRun

class EvaluationRunRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: uuid.UUID, data: dict) -> EvaluationRun:
        run = EvaluationRun(user_id=user_id, **data)
        self.session.add(run)
        await self.session.commit()
        await self.session.refresh(run)
        return run
        
    async def get_by_id_for_user(self, run_id: uuid.UUID, user_id: uuid.UUID) -> EvaluationRun:
        stmt = select(EvaluationRun).where(
            EvaluationRun.id == run_id, 
            EvaluationRun.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
        
    async def list_for_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[EvaluationRun]:
        stmt = select(EvaluationRun).where(
            EvaluationRun.user_id == user_id
        ).order_by(desc(EvaluationRun.created_at)).offset(skip).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

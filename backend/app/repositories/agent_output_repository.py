import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.agent_output import AgentOutput

class AgentOutputRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, output: AgentOutput) -> AgentOutput:
        self.session.add(output)
        await self.session.commit()
        await self.session.refresh(output)
        return output

    async def get_by_message_id(self, message_id: uuid.UUID) -> list[AgentOutput]:
        stmt = select(AgentOutput).where(AgentOutput.message_id == message_id).order_by(AgentOutput.created_at.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

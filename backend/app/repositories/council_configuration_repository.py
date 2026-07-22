import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.council_configuration import CouncilConfiguration

class CouncilConfigurationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, config: CouncilConfiguration) -> CouncilConfiguration:
        self.session.add(config)
        await self.session.flush()
        return config

    async def get_by_message_id(self, message_id: uuid.UUID) -> Optional[CouncilConfiguration]:
        stmt = select(CouncilConfiguration).where(CouncilConfiguration.message_id == message_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

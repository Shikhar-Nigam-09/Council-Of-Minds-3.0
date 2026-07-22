import uuid
from typing import List, Sequence
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chunk import Chunk

class ChunkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_create(self, chunks: List[Chunk]) -> List[Chunk]:
        self.session.add_all(chunks)
        await self.session.flush()
        return chunks

    async def list_by_document(self, document_id: uuid.UUID) -> Sequence[Chunk]:
        stmt = select(Chunk).where(Chunk.document_id == document_id).order_by(Chunk.chunk_index.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_by_document(self, document_id: uuid.UUID) -> None:
        stmt = delete(Chunk).where(Chunk.document_id == document_id)
        await self.session.execute(stmt)
        await self.session.commit()

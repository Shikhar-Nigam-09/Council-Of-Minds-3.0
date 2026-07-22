import uuid
from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document, DocumentStatus

class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, document: Document) -> Document:
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def get_by_id(self, document_id: uuid.UUID) -> Optional[Document]:
        stmt = select(Document).where(Document.id == document_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_for_user(self, document_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Document]:
        stmt = select(Document).where(Document.id == document_id, Document.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: uuid.UUID) -> List[Document]:
        stmt = select(Document).where(Document.user_id == user_id).order_by(Document.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(self, document_id: uuid.UUID, status: DocumentStatus, error_message: str = None) -> None:
        stmt = update(Document).where(Document.id == document_id).values(
            status=status, 
            error_message=error_message
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete(self, document_id: uuid.UUID) -> None:
        stmt = delete(Document).where(Document.id == document_id)
        await self.session.execute(stmt)
        await self.session.commit()

import uuid
from typing import Sequence, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole

class ConversationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_conversation(self, user_id: uuid.UUID, document_id: uuid.UUID) -> Conversation:
        conv = Conversation(user_id=user_id, document_id=document_id)
        self.session.add(conv)
        await self.session.commit()
        return conv

    async def get_by_id_for_user(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Conversation]:
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_message(self, conversation_id: uuid.UUID, role: MessageRole, content: str) -> Message:
        msg = Message(conversation_id=conversation_id, role=role, content=content)
        self.session.add(msg)
        await self.session.flush()
        return msg

    async def get_message_by_id(self, message_id: uuid.UUID) -> Optional[Message]:
        stmt = select(Message).where(Message.id == message_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
        
    async def get_messages_for_conversation(self, conversation_id: uuid.UUID) -> Sequence[Message]:
        stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_user_conversations(self, user_id: uuid.UUID) -> Sequence[Conversation]:
        stmt = select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_conversation(self, conversation_id: uuid.UUID) -> bool:
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await self.session.execute(stmt)
        conv = result.scalar_one_or_none()
        if conv:
            await self.session.delete(conv)
            await self.session.commit()
            return True
        return False

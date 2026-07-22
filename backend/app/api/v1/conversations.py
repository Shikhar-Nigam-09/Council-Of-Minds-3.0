import uuid
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.services.conversation_service import ConversationService
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.council_configuration_repository import CouncilConfigurationRepository
from app.schemas.conversation import ConversationRead, MessageRead
from app.schemas.council_configuration import CouncilConfigurationRead
from app.core.exceptions import AppError
from app.core.rate_limiter import rate_limit_llm, rate_limit_general
from app.core.cost_guardrail import check_and_reserve
from app.core.pricing import get_estimated_run_cost

router = APIRouter(tags=["Conversations"], dependencies=[Depends(rate_limit_general)])

@router.post("", response_model=ConversationRead)
async def create_conversation(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = ConversationRepository(db)
    conv = await repo.create_conversation(current_user.id, document_id)
    return conv

@router.get("", response_model=List[ConversationRead])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = ConversationRepository(db)
    convs = await repo.get_user_conversations(current_user.id)
    return convs

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = ConversationRepository(db)
    conv = await repo.get_by_id_for_user(conversation_id, current_user.id)
    if not conv:
        raise AppError("NOT_FOUND", "Conversation not found", status_code=404)
        
    await repo.delete_conversation(conversation_id)
    return {"status": "deleted"}

@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = ConversationRepository(db)
    conv = await repo.get_by_id_for_user(conversation_id, current_user.id)
    if not conv:
        raise AppError("NOT_FOUND", "Conversation not found", status_code=404)
        
    messages = await repo.get_messages_for_conversation(conversation_id)
    return {
        "conversation": conv,
        "messages": messages
    }

@router.post("/{conversation_id}/messages", dependencies=[Depends(rate_limit_llm)])
async def start_turn(
    conversation_id: uuid.UUID,
    payload: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    question = payload.get("question")
    if not question:
        raise AppError("VALIDATION_ERROR", "Question is required", status_code=400)
        
    return await ConversationService.start_turn(current_user.id, conversation_id, question)

@router.get("/{conversation_id}/messages/{message_id}/configuration", response_model=CouncilConfigurationRead)
async def get_configuration(
    conversation_id: uuid.UUID,
    message_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    conv_repo = ConversationRepository(db)
    config_repo = CouncilConfigurationRepository(db)
    
    conv = await conv_repo.get_by_id_for_user(conversation_id, current_user.id)
    if not conv:
        raise AppError("NOT_FOUND", "Conversation not found", status_code=404)
        
    msg = await conv_repo.get_message_by_id(message_id)
    if not msg or msg.conversation_id != conversation_id:
        raise AppError("NOT_FOUND", "Message not found", status_code=404)
        
    config = await config_repo.get_by_message_id(message_id)
    if not config:
        raise AppError("NOT_FOUND", "Configuration not found", status_code=404)
        
    return config

@router.post("/{conversation_id}/messages/{message_id}/confirm")
async def confirm_turn(
    conversation_id: uuid.UUID,
    message_id: uuid.UUID,
    payload: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    return await ConversationService.confirm_turn(current_user.id, conversation_id, message_id, payload)

import asyncio
from fastapi.responses import StreamingResponse
import json
from app.graph.graph_builder import get_compiled_graph
from app.graph.checkpointer import get_checkpointer
from app.repositories.agent_output_repository import AgentOutputRepository

@router.get("/{conversation_id}/messages/{message_id}/stream", dependencies=[Depends(rate_limit_llm)])
async def stream_turn(
    conversation_id: uuid.UUID,
    message_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    conv_repo = ConversationRepository(db)
    conv = await conv_repo.get_by_id_for_user(conversation_id, current_user.id)
    if not conv:
        raise AppError("NOT_FOUND", "Conversation not found", status_code=404)
        
    msg = await conv_repo.get_message_by_id(message_id)
    if not msg or msg.conversation_id != conversation_id:
        raise AppError("NOT_FOUND", "Message not found", status_code=404)

    await check_and_reserve(current_user.id, get_estimated_run_cost())

    queue = asyncio.Queue()
    cp = await get_checkpointer()
    graph = get_compiled_graph(cp)
    config = {
        "configurable": {
            "thread_id": msg.graph_thread_id,
            "stream_queue": queue
        }
    }

    async def graph_runner():
        try:
            await graph.ainvoke(None, config)
        except Exception as e:
            await queue.put({"type": "error", "message": f"Graph execution failed: {str(e)}"})
        finally:
            await queue.put({"type": "done"})

    async def event_generator():
        task = asyncio.create_task(graph_runner())
        try:
            while True:
                event = await queue.get()
                if event.get("type") == "done":
                    break
                yield f"data: {json.dumps(event)}\n\n"
        finally:
            task.cancel()

    return StreamingResponse(event_generator(), media_type="text/event-stream")

from pydantic import BaseModel
from typing import Optional
from app.llm import get_council_llm

class GeneralChatRequest(BaseModel):
    question: str
    history: List[Dict[str, str]] = []

@router.post("/general-stream", dependencies=[Depends(rate_limit_llm)])
async def general_stream(
    request: GeneralChatRequest,
    current_user: User = Depends(get_current_user)
):
    await check_and_reserve(current_user.id, get_estimated_run_cost())
    
    llm = get_council_llm()
    
    prompt = "System: You are a helpful AI assistant in the Council of Minds platform. You are currently in General Chat mode. Provide helpful, accurate, and concise answers based on your general knowledge.\n\n"
    
    for msg in request.history:
        role = "User" if msg.get("role") == "user" else "Assistant"
        prompt += f"{role}: {msg.get('content', '')}\n\n"
            
    prompt += f"User: {request.question}\nAssistant:"

    async def event_generator():
        try:
            async for chunk in llm.astream(prompt):
                event = {
                    "type": "token",
                    "content": chunk
                }
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        finally:
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/{conversation_id}/messages/{message_id}/agent-outputs")
async def get_agent_outputs(
    conversation_id: uuid.UUID,
    message_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    conv_repo = ConversationRepository(db)
    conv = await conv_repo.get_by_id_for_user(conversation_id, current_user.id)
    if not conv:
        raise AppError("NOT_FOUND", "Conversation not found", status_code=404)
        
    msg = await conv_repo.get_message_by_id(message_id)
    if not msg or msg.conversation_id != conversation_id:
        raise AppError("NOT_FOUND", "Message not found", status_code=404)
        
    repo = AgentOutputRepository(db)
    outputs = await repo.get_by_message_id(message_id)
    return outputs

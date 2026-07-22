import uuid
import logging
from typing import Dict, Any
from app.db.session import async_session_maker
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.council_configuration_repository import CouncilConfigurationRepository
from app.repositories.document_repository import DocumentRepository
from app.models.message import MessageRole, MessageStatus
from app.models.council_configuration import CouncilConfiguration, ConfigurationSource
from app.graph.graph_builder import get_compiled_graph
from app.graph.checkpointer import get_checkpointer
from app.core.exceptions import AppError

logger = logging.getLogger(__name__)

class ConversationService:
    @staticmethod
    async def start_turn(user_id: uuid.UUID, conversation_id: uuid.UUID, question: str) -> Dict[str, Any]:
        async with async_session_maker() as session:
            conv_repo = ConversationRepository(session)
            doc_repo = DocumentRepository(session)
            config_repo = CouncilConfigurationRepository(session)
            
            conv = await conv_repo.get_by_id_for_user(conversation_id, user_id)
            if not conv:
                raise AppError("NOT_FOUND", "Conversation not found", status_code=404)
                
            doc = await doc_repo.get_by_id_for_user(conv.document_id, user_id)
            if not doc:
                raise AppError("NOT_FOUND", "Document not found", status_code=404)
                
            msg = await conv_repo.add_message(conversation_id, MessageRole.user, question)
            
            graph_thread_id = str(uuid.uuid4())
            msg.graph_thread_id = graph_thread_id
            msg.status = MessageStatus.awaiting_confirmation
            await session.commit()  # Commit message so plan_node can create the config linked to it
            
            cp = await get_checkpointer()
            graph = get_compiled_graph(cp)
            config = {"configurable": {"thread_id": graph_thread_id}}
            
            document_context = {
                "title": doc.filename,
                "status": doc.status.value
            }
            
            inputs = {
                "conversation_id": str(conversation_id),
                "message_id": str(msg.id),
                "question": question,
                "document_context": document_context,
                "document_id": str(conv.document_id)
            }
            
            final_state = await graph.ainvoke(inputs, config)
            
            planner_recommendation = final_state.get("planner_recommendation")
            planner_source = final_state.get("planner_source")
            
            if not planner_recommendation:
                raise AppError("GRAPH_ERROR", "Planner failed to return a recommendation", status_code=500)
                
            return {
                "message_id": str(msg.id),
                "graph_thread_id": graph_thread_id,
                "planner_recommendation": planner_recommendation,
                "source": planner_source
            }
            
    @staticmethod
    async def confirm_turn(user_id: uuid.UUID, conversation_id: uuid.UUID, message_id: uuid.UUID, payload: Dict[str, Any]) -> Dict[str, Any]:
        async with async_session_maker() as session:
            conv_repo = ConversationRepository(session)
            config_repo = CouncilConfigurationRepository(session)
            
            conv = await conv_repo.get_by_id_for_user(conversation_id, user_id)
            if not conv:
                raise AppError("NOT_FOUND", "Conversation not found", status_code=404)
                
            msg = await conv_repo.get_message_by_id(message_id)
            if not msg or msg.conversation_id != conversation_id:
                raise AppError("NOT_FOUND", "Message not found", status_code=404)
                
            if msg.status != MessageStatus.awaiting_confirmation:
                raise AppError("INVALID_STATE", "Message is not awaiting confirmation", status_code=400)
                
            weights = payload.get("weights", {})
            enabled = payload.get("enabled", {})
            
            if not any(enabled.values()):
                raise AppError("VALIDATION_ERROR", "At least one agent must be enabled.", status_code=400)
                
            for v in weights.values():
                if int(v) < 0:
                    raise AppError("VALIDATION_ERROR", "Weights must be non-negative.", status_code=400)
            
            final_weights = {}
            for agent in ["logical", "practical", "analytical", "skeptical", "ethics"]:
                is_enabled = enabled.get(agent, True)
                weight = int(weights.get(agent, 0)) if is_enabled else 0
                final_weights[agent] = weight
            
            c_config = await config_repo.get_by_message_id(message_id)
            if not c_config:
                raise AppError("NOT_FOUND", "Configuration not found", status_code=404)
                
            c_config.source = ConfigurationSource.user_confirmed
            c_config.logical_weight = final_weights["logical"]
            c_config.practical_weight = final_weights["practical"]
            c_config.analytical_weight = final_weights["analytical"]
            c_config.skeptical_weight = final_weights["skeptical"]
            c_config.ethics_weight = final_weights["ethics"]
            
            c_config.logical_enabled = enabled.get("logical", True)
            c_config.practical_enabled = enabled.get("practical", True)
            c_config.analytical_enabled = enabled.get("analytical", True)
            c_config.skeptical_enabled = enabled.get("skeptical", True)
            c_config.ethics_enabled = enabled.get("ethics", True)
            
            msg.status = MessageStatus.confirmed
            
            cp = await get_checkpointer()
            graph = get_compiled_graph(cp)
            config = {"configurable": {"thread_id": msg.graph_thread_id}}
            
            resume_state = {
                "confirmed_configuration": {
                    "weights": final_weights,
                    "enabled": enabled
                }
            }
            
            await graph.aupdate_state(config, resume_state)
            await graph.ainvoke(None, config)
            
            await session.commit()
            
            return {
                "message_id": str(msg.id),
                "status": "confirmed",
                "message": "Configuration confirmed — council execution coming in the next phase",
                "final_weights": final_weights
            }

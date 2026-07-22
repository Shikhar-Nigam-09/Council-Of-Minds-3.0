import logging
import uuid
import asyncio
from typing import Dict, Any, List
from app.council.agent_runner import run_agents_concurrently
from app.db.session import async_session_maker
from app.repositories.agent_output_repository import AgentOutputRepository
from sqlalchemy import select
from app.models.chunk import Chunk
from app.models.agent_output import AgentOutput, AgentName, AgentStatus

logger = logging.getLogger(__name__)

class CouncilService:
    @staticmethod
    async def get_chunks_by_ids(chunk_ids: List[str]) -> List[Dict[str, Any]]:
        if not chunk_ids:
            return []
            
        async with async_session_maker() as session:
            stmt = select(Chunk).where(Chunk.vector_id.in_(chunk_ids))
            result = await session.execute(stmt)
            chunks = result.scalars().all()
            return [
                {"id": str(c.vector_id), "text": c.content, "chunk_type": c.chunk_type.value if c.chunk_type else "text"}
                for c in chunks
            ]

    @staticmethod
    async def run_council(chunk_ids: List[str], question: str, configuration: Dict[str, Any], message_id: uuid.UUID, stream_queue: asyncio.Queue = None) -> List[str]:
        enabled_agents_dict = configuration.get("enabled", {})
        enabled_agents = [agent for agent, is_enabled in enabled_agents_dict.items() if is_enabled]
        
        if not enabled_agents:
            logger.warning("No agents enabled.")
            return []
            
        for agent in enabled_agents:
            if stream_queue:
                await stream_queue.put({"type": "agent_status", "agent": agent, "status": "running"})
                
        retrieved_chunks = await CouncilService.get_chunks_by_ids(chunk_ids)
        
        agent_results = await run_agents_concurrently(enabled_agents, question, retrieved_chunks)
        
        agent_output_ids = []
        
        async with async_session_maker() as session:
            repo = AgentOutputRepository(session)
            for agent_name, result in agent_results.items():
                status = AgentStatus.success if result.get("status") == "success" else AgentStatus.failed
                
                output = AgentOutput(
                    message_id=message_id,
                    agent_name=AgentName(agent_name),
                    status=status,
                    summary=result.get("summary"),
                    evidence_points=result.get("evidence_points"),
                    error_message=result.get("error_message"),
                    weight_used=configuration.get("weights", {}).get(agent_name, 0),
                    included_in_synthesis=False
                )
                saved_output = await repo.save(output)
                agent_output_ids.append(str(saved_output.id))
                
                if stream_queue:
                    stream_status = "complete" if status == AgentStatus.success else "failed"
                    await stream_queue.put({"type": "agent_status", "agent": agent_name, "status": stream_status})
                    
        return agent_output_ids

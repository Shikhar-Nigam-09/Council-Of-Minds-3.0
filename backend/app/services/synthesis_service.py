import logging
import uuid
from typing import Dict, Any, List
from app.db.session import async_session_maker
from sqlalchemy import select
from app.models.agent_output import AgentOutput
from app.models.message import Message, MessageStatus
from app.council.weight_filter import filter_evidence
from app.services.council_service import CouncilService
from app.llm import get_council_llm
from datetime import datetime
import json
import asyncio

logger = logging.getLogger(__name__)

class SynthesisService:
    @staticmethod
    async def get_agent_outputs_by_ids(output_ids: List[str]) -> List[AgentOutput]:
        if not output_ids:
            return []
        async with async_session_maker() as session:
            stmt = select(AgentOutput).where(AgentOutput.id.in_(output_ids))
            result = await session.execute(stmt)
            return list(result.scalars().all())

    @staticmethod
    async def synthesize(agent_output_ids: List[str], question: str, weights: Dict[str, int], message_id: uuid.UUID, stream_queue: asyncio.Queue = None) -> Dict[str, Any]:
        outputs = await SynthesisService.get_agent_outputs_by_ids(agent_output_ids)
        
        agent_outputs_dict = {}
        for out in outputs:
            agent_outputs_dict[out.agent_name.value] = {
                "status": out.status.value,
                "summary": out.summary,
                "evidence_points": out.evidence_points
            }
            
        filtered_bundle = filter_evidence(agent_outputs_dict, weights)
        
        async with async_session_maker() as session:
            for out in outputs:
                included = filtered_bundle.get(out.agent_name.value, {}).get("included_in_synthesis", False)
                
                stmt = select(AgentOutput).where(AgentOutput.id == out.id)
                res = await session.execute(stmt)
                db_out = res.scalar_one_or_none()
                if db_out:
                    db_out.included_in_synthesis = included
            await session.commit()
            
        # Collect chunk IDs approved by the council
        approved_chunk_ids = set()
        for agent_data in filtered_bundle.values():
            if agent_data.get("included_in_synthesis"):
                for ep in agent_data.get("evidence_points", []):
                    if ep.get("supporting_chunk_id"):
                        approved_chunk_ids.add(ep.get("supporting_chunk_id"))
                        
        # Fetch the raw chunk text
        retrieved_chunks = await CouncilService.get_chunks_by_ids(list(approved_chunk_ids))
        
        # Construct the context block
        context_text = "<context>\n"
        for idx, chunk in enumerate(retrieved_chunks):
            context_text += f"[Excerpt {idx + 1}]\n{chunk.get('text', '')}\n\n"
        context_text += "</context>\n"
            
        is_summary = any(k in question.lower() for k in ["summarize", "summary", "overview", "explain", "report", "everything"])
        
        prompt = f"You are the Council Synthesizer. Synthesize a final answer to the user's question based on the provided document excerpts. Do not mention internal systems.\n\n"
        
        if is_summary:
            prompt += (
                "The user is asking for a summary of the document. "
                "You MUST format your response as a structured Markdown report using the following exact headers (if the information is available):\n"
                "# Executive Summary\n"
                "## Project Objective\n"
                "## Technologies Used\n"
                "## System Architecture\n"
                "## Major Features\n"
                "## Challenges\n"
                "## Outcomes / Conclusion\n\n"
            )
        prompt += f"{context_text}\n"
        prompt += f"Question: {question}\n\n"
        prompt += "Answer:\n"
        
        llm = get_council_llm()
        
        final_answer = ""
        try:
            if stream_queue:
                await stream_queue.put({"type": "answer_start"})
            
            chunk_idx = 1
            async for chunk in llm.astream(prompt):
                final_answer += chunk
                if stream_queue:
                    logger.info(f"Chunk {chunk_idx}: {repr(chunk)}")
                    await stream_queue.put({"type": "answer_chunk", "content": chunk})
                    chunk_idx += 1
                    
            if stream_queue:
                await stream_queue.put({"type": "answer_complete"})
                
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            if stream_queue:
                await stream_queue.put({"type": "error", "message": "Synthesis failed."})
            return {"status": "synthesis_failed"}
            
        async with async_session_maker() as session:
            stmt = select(Message).where(Message.id == message_id)
            result = await session.execute(stmt)
            msg = result.scalar_one_or_none()
            if msg:
                msg.final_answer = final_answer
                msg.synthesis_model = getattr(llm, "model", "mock-synthesizer")
                msg.completed_at = datetime.utcnow()
                msg.status = MessageStatus.completed
                await session.commit()
                
        return {"status": "completed", "final_answer": final_answer}

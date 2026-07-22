import asyncio
import logging
import json
from typing import Dict, Any, List
from app.llm import get_council_llm
from app.council.agent_definitions import get_agent_prompt

logger = logging.getLogger(__name__)

async def run_single_agent(agent_name: str, question: str, chunks_text: str) -> Dict[str, Any]:
    llm = get_council_llm()
    prompt = get_agent_prompt(agent_name, question, chunks_text)
    
    try:
        response = await asyncio.to_thread(llm.complete, prompt, "json")
        data = json.loads(response)
        
        # Lightweight groundedness check
        valid_chunk_ids = [c.split("ID: ")[1].split("\n")[0] for c in chunks_text.split("\n\n---\n\n") if "ID: " in c]
        
        for ep in data.get("evidence_points", []):
            if ep.get("supporting_chunk_id") not in valid_chunk_ids:
                logger.warning(f"Agent {agent_name} hallucinated chunk id: {ep.get('supporting_chunk_id')}")
                
        return {
            "status": "success",
            "summary": data.get("summary", ""),
            "evidence_points": data.get("evidence_points", [])
        }
    except Exception as e:
        logger.error(f"Agent {agent_name} failed: {e}")
        return {
            "status": "failed",
            "error_message": str(e)
        }

async def run_agents_concurrently(enabled_agents: List[str], question: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    chunks_text_parts = []
    for c in retrieved_chunks:
        chunks_text_parts.append(f"ID: {c['id']}\nType: {c.get('chunk_type', 'unknown')}\nContent: {c['text']}")
    chunks_text = "\n\n---\n\n".join(chunks_text_parts)
    
    tasks = []
    for agent in enabled_agents:
        tasks.append(run_single_agent(agent, question, chunks_text))
        
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    final_results = {}
    for agent, result in zip(enabled_agents, results):
        if isinstance(result, Exception):
            logger.error(f"Agent {agent} raised unhandled exception: {result}")
            final_results[agent] = {"status": "failed", "error_message": str(result)}
        else:
            final_results[agent] = result
            
    return final_results

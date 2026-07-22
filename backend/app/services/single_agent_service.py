import logging
import time
from typing import Dict, Any, Tuple
from app.services.retrieval_service import RetrievalService
from app.llm import get_council_llm
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

class SingleAgentService:
    @staticmethod
    async def answer_single_agent(document_id: str, question: str) -> Tuple[str, Dict[str, Any], int, int, int]:
        start_time = time.time()
        
        chunk_ids = await RetrievalService.retrieve_chunks(document_id, question)
        
        from app.services.council_service import CouncilService
        retrieved_chunks = await CouncilService.get_chunks_by_ids(chunk_ids)
        
        context_text = "\n\n".join([
            f"[Chunk ID: {c['id']}]\n{c['text']}" for c in retrieved_chunks
        ])
        
        system_prompt = (
            "You are a helpful assistant answering questions about a document.\n"
            "Use the provided context to answer the question.\n"
            "Use inline citations like [chunk-id] when referencing the context."
        )
        
        human_prompt = f"Question: {question}\n\nContext:\n{context_text}"
        
        llm = get_council_llm()
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = await llm.ainvoke(messages)
        answer = response.content
        
        token_usage = response.response_metadata.get("token_usage", {}) if hasattr(response, 'response_metadata') else {}
        input_tokens = token_usage.get("prompt_tokens", 0)
        output_tokens = token_usage.get("completion_tokens", 0)
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        import re
        citations = {}
        matches = re.findall(r'\[([a-fA-F0-9-]{36})\]', answer)
        for m in matches:
            citations[m] = True
            
        return answer, citations, latency_ms, input_tokens, output_tokens

import logging
import uuid
import time
import asyncio
from app.services.single_agent_service import SingleAgentService
from app.services.council_service import CouncilService
from app.services.synthesis_service import SynthesisService
from app.services.judge_service import JudgeService
from app.repositories.evaluation_run_repository import EvaluationRunRepository
from app.db.session import async_session_maker
from app.core.pricing import calculate_cost
from app.core.config import settings

logger = logging.getLogger(__name__)

class EvaluationService:
    @staticmethod
    async def run_evaluation(document_id: uuid.UUID, question: str, user_id: uuid.UUID) -> dict:
        
        async def run_sa():
            try:
                return await SingleAgentService.answer_single_agent(str(document_id), question)
            except Exception as e:
                logger.error(f"Single agent failed: {e}")
                return "", {}, 0, 0, 0
                
        async def run_council_pipeline():
            start_time = time.time()
            config = {
                "enabled": {
                    "logical": True,
                    "practical": True,
                    "analytical": True,
                    "skeptical": True,
                    "ethics": True
                },
                "weights": {
                    "logical": 20,
                    "practical": 20,
                    "analytical": 20,
                    "skeptical": 20,
                    "ethics": 20
                }
            }
            msg_id = uuid.uuid4()
            
            try:
                from app.services.retrieval_service import RetrievalService
                chunk_ids = await RetrievalService.retrieve_chunks(str(document_id), question)
                agent_output_ids = await CouncilService.run_council(chunk_ids, question, config, msg_id)
                
                if not agent_output_ids:
                    return "", {}, int((time.time() - start_time)*1000)
                    
                result = await SynthesisService.synthesize(agent_output_ids, question, config["weights"], msg_id)
                
                import re
                answer = result.get("final_answer", "")
                citations = {}
                matches = re.findall(r'\[([a-fA-F0-9-]{36})\]', answer)
                for m in matches:
                    citations[m] = True
                    
                return answer, citations, int((time.time() - start_time)*1000)
            except Exception as e:
                logger.error(f"Council pipeline failed: {e}")
                return "", {}, int((time.time() - start_time)*1000)
                
        sa_task = asyncio.create_task(run_sa())
        council_task = asyncio.create_task(run_council_pipeline())
        
        (sa_answer, sa_citations, sa_latency, sa_input, sa_output), (council_answer, council_citations, council_latency) = await asyncio.gather(sa_task, council_task)
        
        sa_cost = calculate_cost(settings.GROQ_COUNCIL_MODEL, sa_input, sa_output)
        
        council_cost = 0.0
        
        judge_status = "failed"
        judge_verdict = None
        judge_latency = 0
        
        if sa_answer and council_answer:
            judge_start = time.time()
            try:
                judge_verdict = await JudgeService.judge_answers(question, sa_answer, council_answer)
                judge_status = "success"
            except Exception as e:
                logger.error(f"Judge failed: {e}")
            judge_latency = int((time.time() - judge_start) * 1000)
            
        async with async_session_maker() as session:
            repo = EvaluationRunRepository(session)
            run = await repo.create(user_id, {
                "document_id": document_id,
                "question": question,
                "single_agent_answer": sa_answer,
                "single_agent_citations": sa_citations,
                "single_agent_latency_ms": sa_latency,
                "single_agent_cost_estimate": sa_cost,
                "council_answer": council_answer,
                "council_citations": council_citations,
                "council_latency_ms": council_latency,
                "council_cost_estimate": council_cost,
                "judge_status": judge_status,
                "judge_verdict": judge_verdict,
                "judge_latency_ms": judge_latency
            })
            return run

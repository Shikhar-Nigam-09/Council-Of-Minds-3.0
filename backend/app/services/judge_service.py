import logging
import json
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import settings

logger = logging.getLogger(__name__)

class JudgeService:
    @staticmethod
    async def judge_answers(question: str, single_agent_answer: str, council_answer: str) -> Dict[str, Any]:
        system_prompt = """You are an impartial Judge evaluating two AI answers to a user question.
You must output YOUR ENTIRE RESPONSE as a valid JSON object matching this schema exactly:
{
  "single_agent": {
    "quality_score": 5,
    "completeness_score": 5,
    "citation_quality_score": 5,
    "reasoning": "brief explanation"
  },
  "council": {
    "quality_score": 5,
    "completeness_score": 5,
    "citation_quality_score": 5,
    "reasoning": "brief explanation"
  },
  "comparative_verdict": "brief overall comparison"
}
Do not include markdown blocks or any other text outside the JSON object.
"""
        
        human_prompt = f"""Question: {question}

--- SINGLE AGENT ANSWER ---
{single_agent_answer}

--- COUNCIL ANSWER ---
{council_answer}
"""
        
        if settings.is_mock_mode:
            from app.llm.mock_provider import MockLLMProvider
            llm = MockLLMProvider("mock-judge")
        else:
            from langchain_groq import ChatGroq
            llm = ChatGroq(model=settings.GROQ_JUDGE_MODEL, api_key=settings.GROQ_API_KEY)
            
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        for attempt in range(2):
            try:
                response = await llm.ainvoke(messages)
                content = response.content
                
                if content.startswith("```json"):
                    content = content[7:-3]
                elif content.startswith("```"):
                    content = content[3:-3]
                    
                verdict = json.loads(content.strip())
                
                if "single_agent" in verdict and "council" in verdict:
                    return verdict
            except Exception as e:
                logger.warning(f"Judge parsing failed on attempt {attempt+1}: {e}")
                
        raise ValueError("Judge failed to return valid JSON.")

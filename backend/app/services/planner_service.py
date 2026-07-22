import json
import logging
import asyncio
import time
from typing import Dict, Any
from app.llm import get_planner_llm
from app.core.config import settings

logger = logging.getLogger(__name__)

PLANNER_PROMPT_VERSION = "planner_v1"

class PlannerService:
    @staticmethod
    def _normalize_weights(weights: Dict[str, Any], enabled: Dict[str, bool]) -> Dict[str, int]:
        agents = ["logical", "practical", "analytical", "skeptical", "ethics"]
        
        clamped = {}
        for agent in agents:
            if not enabled.get(agent, True):
                clamped[agent] = 0
            else:
                raw_weight = int(weights.get(agent, 0))
                clamped[agent] = max(0, min(100, raw_weight))
                
        total = sum(clamped.values())
        if total == 0:
            raise ValueError("All agents disabled or all weights are zero.")
            
        normalized = {}
        for agent in agents:
            normalized[agent] = round((clamped[agent] / total) * 100)
            
        norm_total = sum(normalized.values())
        diff = 100 - norm_total
        if diff != 0:
            largest_agent = max([a for a in agents if enabled.get(a, True)], key=lambda x: normalized[x])
            normalized[largest_agent] += diff
            
        return normalized

    @staticmethod
    async def generate_plan(question: str, document_context: Dict[str, Any]) -> Dict[str, Any]:
        llm = get_planner_llm()
        model_name = getattr(llm, 'model', 'mock-planner')
        
        prompt = f"""You are a planner agent for the Council of Minds.
Given the user's question and document context, recommend a weight (0-100) for each of the 5 council agents and whether they should be enabled.

Agents:
- logical: Focuses on pure logic and structure.
- practical: Focuses on actionable, real-world application.
- analytical: Focuses on data and deep analysis.
- skeptical: Focuses on questioning assumptions.
- ethics: Focuses on morality and fairness.

Document Context: {json.dumps(document_context)}
User Question: {question}

Return ONLY a JSON object with the agents as keys. Each value must be an object with 'weight' (integer) and 'enabled' (boolean).
Example: {{"logical": {{"weight": 20, "enabled": true}}, "practical": {{"weight": 30, "enabled": true}}, "analytical": {{"weight": 0, "enabled": false}}, "skeptical": {{"weight": 25, "enabled": true}}, "ethics": {{"weight": 25, "enabled": true}}}}
"""
        
        retries = settings.PLANNER_MAX_RETRIES
        for attempt in range(retries):
            start_time = time.time()
            try:
                response_text = await asyncio.to_thread(llm.complete, prompt, "json")
                latency_ms = int((time.time() - start_time) * 1000)
                
                data = json.loads(response_text)
                
                raw_weights = {}
                raw_enabled = {}
                expected_keys = {"logical", "practical", "analytical", "skeptical", "ethics"}
                
                if not expected_keys.issubset(set(data.keys())):
                    raise ValueError(f"Missing expected keys in response: {data}")
                    
                for k in expected_keys:
                    if isinstance(data[k], dict):
                        raw_weights[k] = data[k].get("weight", 0)
                        raw_enabled[k] = data[k].get("enabled", True)
                    else:
                        raw_weights[k] = data[k]
                        raw_enabled[k] = True
                
                final_weights = PlannerService._normalize_weights(raw_weights, raw_enabled)
                
                logger.info("Planner generated AI recommendation successfully.")
                return {
                    "source": "ai_recommendation",
                    "weights": final_weights,
                    "enabled": raw_enabled,
                    "model_name": model_name,
                    "prompt_version": PLANNER_PROMPT_VERSION,
                    "latency_ms": latency_ms,
                    "retry_count": attempt
                }
            except Exception as e:
                logger.warning(f"Planner attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
        
        logger.warning("Planner exhausted retries. Using balanced fallback.")
        return {
            "source": "balanced_fallback",
            "weights": {"logical": 20, "practical": 20, "analytical": 20, "skeptical": 20, "ethics": 20},
            "enabled": {"logical": True, "practical": True, "analytical": True, "skeptical": True, "ethics": True},
            "model_name": "balanced_fallback",
            "prompt_version": PLANNER_PROMPT_VERSION,
            "latency_ms": None,
            "retry_count": retries
        }

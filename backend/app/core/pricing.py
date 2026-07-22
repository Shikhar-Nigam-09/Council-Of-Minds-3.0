import json
import logging
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

DEFAULT_PRICING = {
    "llama-3.1-8b-instant": {"input": 0.00005, "output": 0.00008},
    "llama-3.3-70b-versatile": {"input": 0.00059, "output": 0.00079},
    "default": {"input": 0.0001, "output": 0.0002}
}

def get_pricing_table() -> Dict[str, Dict[str, float]]:
    if settings.PRICING_TABLE_PATH:
        try:
            with open(settings.PRICING_TABLE_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load pricing table from {settings.PRICING_TABLE_PATH}: {e}")
    return DEFAULT_PRICING

def calculate_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    pricing = get_pricing_table()
    model_pricing = pricing.get(model_name, pricing.get("default"))
    
    input_cost = (input_tokens / 1000.0) * model_pricing["input"]
    output_cost = (output_tokens / 1000.0) * model_pricing["output"]
    
    return input_cost + output_cost

def get_estimated_run_cost() -> float:
    planner_cost = calculate_cost(settings.GROQ_PLANNER_MODEL, 1000, 200)
    agent_cost = calculate_cost(settings.GROQ_COUNCIL_MODEL, 3000, 500) * 5
    synth_cost = calculate_cost(settings.GROQ_COUNCIL_MODEL, 5000, 1000)
    return planner_cost + agent_cost + synth_cost

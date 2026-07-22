from app.core.config import settings
from .base import LLMProvider
from .groq_provider import GroqLLMProvider
from .mock_provider import MockLLMProvider

from functools import lru_cache

@lru_cache(maxsize=1)
def get_planner_llm() -> LLMProvider:
    if settings.GROQ_API_KEY:
        return GroqLLMProvider(
            api_key=settings.GROQ_API_KEY, 
            model=settings.GROQ_PLANNER_MODEL
        )
    return MockLLMProvider()

@lru_cache(maxsize=1)
def get_council_llm() -> LLMProvider:
    if settings.GROQ_API_KEY:
        return GroqLLMProvider(
            api_key=settings.GROQ_API_KEY, 
            model=settings.GROQ_COUNCIL_MODEL
        )
    return MockLLMProvider()

@lru_cache(maxsize=1)
def get_judge_llm() -> LLMProvider:
    if settings.GROQ_API_KEY:
        return GroqLLMProvider(
            api_key=settings.GROQ_API_KEY, 
            model=settings.GROQ_JUDGE_MODEL
        )
    return MockLLMProvider()

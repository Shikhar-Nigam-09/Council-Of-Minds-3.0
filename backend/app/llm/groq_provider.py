import logging
from typing import Literal, AsyncGenerator
from groq import Groq, AsyncGroq
from app.llm.base import LLMProvider
from app.core.exceptions import AppError
from app.core.observability import trace_llm_call
from app.core.circuit_breaker import with_circuit_breaker

logger = logging.getLogger(__name__)

class GroqLLMProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.client = Groq(api_key=self.api_key)
        self.async_client = AsyncGroq(api_key=self.api_key)

    @trace_llm_call(name="groq_complete")
    @with_circuit_breaker("groq")
    def complete(self, prompt: str, response_format: Literal["text", "json"] = "text") -> str:
        try:
            kwargs = {
                "messages": [{"role": "user", "content": prompt}],
                "model": self.model,
                "temperature": 0.0,
                "timeout": 30.0
            }
            if response_format == "json":
                kwargs["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise AppError("LLM_FAILED", f"Groq API call failed: {str(e)}", status_code=500)

    @trace_llm_call(name="groq_astream")
    @with_circuit_breaker("groq")
    async def astream(self, prompt: str, response_format: Literal["text", "json"] = "text") -> AsyncGenerator[str, None]:
        try:
            kwargs = {
                "messages": [{"role": "user", "content": prompt}],
                "model": self.model,
                "temperature": 0.0,
                "timeout": 30.0,
                "stream": True
            }
            if response_format == "json":
                kwargs["response_format"] = {"type": "json_object"}

            stream = await self.async_client.chat.completions.create(**kwargs)
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Groq async stream error: {e}")
            raise AppError("LLM_FAILED", f"Groq async API call failed: {str(e)}", status_code=500)

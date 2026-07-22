import json
import hashlib
import asyncio
from typing import Literal, AsyncGenerator
from app.llm.base import LLMProvider

class MockLLMProvider(LLMProvider):
    def complete(self, prompt: str, response_format: Literal["text", "json"] = "text") -> str:
        if response_format == "json":
            if "recommend a weight" in prompt:
                h = int(hashlib.md5(prompt.encode('utf-8')).hexdigest(), 16)
                weights = {"logical": 20, "practical": 20, "analytical": 20, "skeptical": 20, "ethics": 20}
                mod = h % 5
                agents = list(weights.keys())
                weights[agents[mod]] += 10
                weights[agents[(mod + 1) % 5]] -= 10
                return json.dumps(weights)
            else:
                return json.dumps({
                    "summary": "This is a mock agent summary based on its perspective.",
                    "evidence_points": [
                        {"claim": "Mock claim 1", "supporting_chunk_id": "mock-chunk-1", "confidence": "high"},
                        {"claim": "Mock claim 2", "supporting_chunk_id": "mock-chunk-2", "confidence": "medium"}
                    ]
                })
        return "This is a mock text response."

    async def astream(self, prompt: str, response_format: Literal["text", "json"] = "text") -> AsyncGenerator[str, None]:
        if response_format == "json":
            yield self.complete(prompt, response_format)
            return
            
        words = "This is a streamed mock answer with inline citations. Here is a citation [chunk-1234]. Another one [chunk-5678].".split(' ')
        for i, word in enumerate(words):
            yield word + (" " if i < len(words)-1 else "")
            await asyncio.sleep(0.05)

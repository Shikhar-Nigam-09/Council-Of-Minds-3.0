from abc import ABC, abstractmethod
from typing import Literal, AsyncGenerator

class LLMProvider(ABC):
    @abstractmethod
    def complete(self, prompt: str, response_format: Literal["text", "json"] = "text") -> str:
        pass

    @abstractmethod
    async def astream(self, prompt: str, response_format: Literal["text", "json"] = "text") -> AsyncGenerator[str, None]:
        pass

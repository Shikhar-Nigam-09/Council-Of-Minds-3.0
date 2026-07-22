from abc import ABC, abstractmethod
from typing import Optional

class VisionCaptionProvider(ABC):
    @abstractmethod
    def caption(self, image_bytes: bytes) -> Optional[str]:
        pass

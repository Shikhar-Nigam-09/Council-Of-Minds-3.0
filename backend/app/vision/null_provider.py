from typing import Optional
from app.vision.base import VisionCaptionProvider

class NullVisionCaptionProvider(VisionCaptionProvider):
    def caption(self, image_bytes: bytes) -> Optional[str]:
        # Return None so that chunking service treats the caption as pending
        return None

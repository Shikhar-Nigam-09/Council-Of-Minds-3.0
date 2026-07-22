from .base import VisionCaptionProvider
from .null_provider import NullVisionCaptionProvider

def get_vision_caption_provider() -> VisionCaptionProvider:
    return NullVisionCaptionProvider()

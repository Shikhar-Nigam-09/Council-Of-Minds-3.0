import fitz
import logging
from typing import List, Dict, Any
from app.vision import get_vision_caption_provider

logger = logging.getLogger(__name__)

class ImageExtractor:
    @staticmethod
    def extract(doc: fitz.Document, page: fitz.Page) -> List[Dict[str, Any]]:
        results = []
        try:
            image_list = page.get_images(full=True)
            caption_provider = get_vision_caption_provider()
            
            for img_info in image_list:
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                caption = caption_provider.caption(image_bytes)
                caption_pending = caption is None
                
                content = caption if caption else "Image caption pending."
                
                results.append({
                    "type": "image_caption",
                    "page_number": page.number + 1,
                    "content": content,
                    "caption_pending": caption_pending,
                    "source_type": "vision"
                })
        except Exception as e:
            logger.error(f"Image extraction failed on page {page.number}: {e}")
        return results

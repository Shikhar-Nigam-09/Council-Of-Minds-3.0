import fitz
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DocumentClassifier:
    @staticmethod
    def classify_page(page: fitz.Page) -> Dict[str, Any]:
        has_text = False
        has_tables_likely = False
        is_scanned = False
        
        try:
            text = page.get_text("text")
            has_text = len(text.strip()) > 20
            
            has_tables_likely = has_text
            
            image_list = page.get_images(full=True)
            has_images = len(image_list) > 0
            
            is_scanned = has_images and not has_text

            return {
                "has_text": has_text,
                "has_tables_likely": has_tables_likely,
                "is_scanned": is_scanned
            }
        except Exception as e:
            logger.warning(f"Classification failed for page {page.number}: {e}")
            return {"has_text": False, "has_tables_likely": False, "is_scanned": False}

import fitz
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class TextExtractor:
    @staticmethod
    def extract(page: fitz.Page) -> List[Dict[str, Any]]:
        results = []
        try:
            blocks = page.get_text("blocks")
            for b in blocks:
                if b[6] == 0:  # Text block
                    text = b[4].strip()
                    if text:
                        is_heading = len(text) < 100 and text.istitle()
                        is_list = "\n-" in text or "\n•" in text or "\n1." in text
                        
                        chunk_type = "heading" if is_heading else ("list" if is_list else "text")
                        
                        results.append({
                            "type": chunk_type,
                            "page_number": page.number + 1,
                            "content": text,
                            "source_type": "pymupdf"
                        })
        except Exception as e:
            logger.error(f"Text extraction failed on page {page.number}: {e}")
        return results

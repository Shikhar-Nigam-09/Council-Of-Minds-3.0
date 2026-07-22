import fitz
import pytesseract
from PIL import Image
import io
import logging
from typing import List, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

if settings.TESSERACT_CMD_PATH:
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD_PATH

class OCRExtractor:
    @staticmethod
    def extract(page: fitz.Page) -> List[Dict[str, Any]]:
        results = []
        try:
            try:
                pytesseract.get_tesseract_version()
            except Exception:
                logger.warning(f"Tesseract is not available. Skipping OCR on page {page.number}.")
                raise Exception("Tesseract not installed")

            pix = page.get_pixmap(dpi=150)
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            
            text = pytesseract.image_to_string(image)
            text = text.strip()
            
            if text:
                results.append({
                    "type": "text",
                    "page_number": page.number + 1,
                    "content": text,
                    "source_type": "ocr"
                })
        except Exception as e:
            logger.error(f"OCR extraction failed on page {page.number}: {e}")
            raise e
        return results

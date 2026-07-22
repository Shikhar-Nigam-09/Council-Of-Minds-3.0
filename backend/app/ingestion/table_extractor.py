import pdfplumber
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class TableExtractor:
    @staticmethod
    def extract(pdf_path: str, page_number: int) -> List[Dict[str, Any]]:
        results = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                page = pdf.pages[page_number]
                tables = page.extract_tables()
                for table in tables:
                    if not table:
                        continue
                    
                    md_rows = []
                    for row in table:
                        clean_row = [str(cell).replace('\n', ' ') if cell else "" for cell in row]
                        md_rows.append("| " + " | ".join(clean_row) + " |")
                    
                    if len(md_rows) > 1:
                        header_sep = "| " + " | ".join(["---"] * len(table[0])) + " |"
                        md_rows.insert(1, header_sep)
                        
                    content = "\n".join(md_rows)
                    
                    results.append({
                        "type": "table",
                        "page_number": page_number + 1,
                        "content": content,
                        "source_type": "pdfplumber"
                    })
        except Exception as e:
            logger.error(f"Table extraction failed on page {page_number}: {e}")
        return results

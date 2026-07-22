import asyncio
import logging
import os
import tempfile
import fitz
from app.db.session import async_session_maker
from app.repositories.document_repository import DocumentRepository
from app.repositories.chunk_repository import ChunkRepository
from app.models.document import DocumentStatus

from app.ingestion.classifier import DocumentClassifier
from app.ingestion.text_extractor import TextExtractor
from app.ingestion.table_extractor import TableExtractor
from app.ingestion.ocr_extractor import OCRExtractor
from app.ingestion.image_extractor import ImageExtractor
from app.ingestion.chunking_service import ChunkingService
from app.embeddings import get_embedding_provider
from app.vectorstore import get_vectorstore_provider
import requests

logger = logging.getLogger(__name__)

async def process_document_service(document_id: str):
    """
    Core document processing logic that can be invoked by Celery, FastAPI BackgroundTasks, or directly.
    """
    async with async_session_maker() as session:
        doc_repo = DocumentRepository(session)
        chunk_repo = ChunkRepository(session)
        doc = await doc_repo.get_by_id(document_id)
        
        if not doc:
            logger.error(f"Document {document_id} not found for ingestion.")
            return

        try:
            await doc_repo.update_status(document_id, DocumentStatus.processing)
            
            file_path = ""
            if doc.storage_url.startswith("http://localhost:8000/mock_storage/"):
                filename = doc.storage_url.split("/")[-1]
                # Fallback path if mock_storage is somehow local
                file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mock_storage", filename)
            else:
                response = requests.get(doc.storage_url)
                response.raise_for_status()
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                tmp.write(response.content)
                tmp.close()
                file_path = tmp.name

            # Perform synchronous processing operations in a thread to avoid blocking the event loop
            def extract_and_chunk():
                pdf_doc = fitz.open(file_path)
                page_count = len(pdf_doc)
                
                processing_report = {
                    "text": "skipped",
                    "tables": "skipped",
                    "ocr": "skipped",
                    "images": "skipped"
                }
                
                all_extractions = []
                
                for i in range(page_count):
                    page = pdf_doc[i]
                    classification = DocumentClassifier.classify_page(page)
                    
                    if classification["has_text"]:
                        try:
                            text_res = TextExtractor.extract(page)
                            all_extractions.extend(text_res)
                            if processing_report["text"] != "failed":
                                processing_report["text"] = "success"
                        except Exception:
                            processing_report["text"] = "failed"
                    
                    if classification["has_tables_likely"]:
                        try:
                            table_res = TableExtractor.extract(file_path, i)
                            all_extractions.extend(table_res)
                            if processing_report["tables"] != "failed":
                                processing_report["tables"] = "success"
                        except Exception:
                            processing_report["tables"] = "failed"
                            
                    try:
                        img_res = ImageExtractor.extract(pdf_doc, page)
                        if img_res:
                            all_extractions.extend(img_res)
                            if processing_report["images"] != "failed":
                                processing_report["images"] = "success"
                    except Exception:
                        processing_report["images"] = "failed"
                        
                    if classification["is_scanned"]:
                        try:
                            ocr_res = OCRExtractor.extract(page)
                            all_extractions.extend(ocr_res)
                            if processing_report["ocr"] != "failed":
                                processing_report["ocr"] = "success"
                        except Exception:
                            processing_report["ocr"] = "failed"

                pdf_doc.close()
                
                if not doc.storage_url.startswith("http://localhost:8000/mock_storage/"):
                    os.remove(file_path)
                    
                chunks = ChunkingService.chunk_extractions(str(doc.id), all_extractions)
                
                if not chunks:
                    if any(v == "failed" for v in processing_report.values()):
                        raise Exception("All attempted extractions failed or yielded no chunks.")
                    else:
                        raise Exception("Document contained no extractable content.")

                embedding_provider = get_embedding_provider()
                texts_to_embed = [c.content for c in chunks]
                vectors = embedding_provider.embed_texts(texts_to_embed)
                
                vectorstore = get_vectorstore_provider()
                vectorstore.ensure_collection(embedding_provider.dimension)
                
                chunks_with_vectors = []
                for i, chunk in enumerate(chunks):
                    chunk_dict = {
                        "document_id": str(chunk.document_id),
                        "chunk_index": chunk.chunk_index,
                        "chunk_type": chunk.chunk_type.value,
                        "source_type": chunk.source_type.value,
                        "page_number": chunk.page_number,
                        "section_title": chunk.section_title,
                        "content": chunk.content,
                        "caption_pending": chunk.caption_pending,
                        "vector_id": chunk.vector_id,
                        "vector": vectors[i]
                    }
                    chunks_with_vectors.append(chunk_dict)
                    
                vectorstore.upsert_chunks(str(doc.id), chunks_with_vectors)
                
                return chunks, page_count, processing_report

            # Run the heavy synchronous work in a separate thread so it doesn't block the async event loop
            import anyio
            chunks, page_count, processing_report = await anyio.to_thread.run_sync(extract_and_chunk)
            
            # Reattach and save chunks and metadata to the database
            await chunk_repo.bulk_create(chunks)
            
            doc.page_count = page_count
            doc.processing_report = processing_report
            
            has_failures = any(v == "failed" for v in processing_report.values())
            final_status = DocumentStatus.partial if has_failures else DocumentStatus.completed
            
            doc.status = final_status
            session.add(doc)
            await session.commit()
            
            logger.info(f"Document {document_id} ingestion {final_status}.")

        except Exception as e:
            logger.exception(f"Error processing document {document_id}: {str(e)}")
            await doc_repo.update_status(document_id, DocumentStatus.failed, error_message=str(e))
            # No re-raise to ensure the task finishes cleanly and status remains failed

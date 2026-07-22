import asyncio
import logging
import os
import fitz
from celery import shared_task
from app.db.session import async_session_maker
from app.repositories.document_repository import DocumentRepository
from app.repositories.chunk_repository import ChunkRepository
from app.models.document import DocumentStatus

from app.services.ingestion_service import process_document_service

@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def process_document_ingestion(self, document_id: str):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
        
        asyncio.run(process_document_service(document_id))
    except Exception as exc:
        logger.error(f"Task failed for document {document_id}")

import uuid
import os
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document, DocumentStatus
from app.schemas.document import DocumentUploadResponse
from app.repositories.document_repository import DocumentRepository
from app.services.storage_service import StorageService
from app.tasks.ingestion_tasks import process_document_ingestion
from app.core.exceptions import AppError

class DocumentService:
    def __init__(self, db: AsyncSession, storage_service: StorageService):
        self.db = db
        self.repo = DocumentRepository(db)
        self.storage = storage_service

    async def _validate_file(self, file: UploadFile, user_id: uuid.UUID):
        # Check limit
        from app.core.config import settings
        docs = await self.repo.list_by_user(user_id)
        if len(docs) >= settings.MAX_DOCUMENTS_PER_USER:
            raise AppError("LIMIT_EXCEEDED", f"Maximum of {settings.MAX_DOCUMENTS_PER_USER} documents per user allowed.")
            
        # Check size
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)
        
        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if size > max_size:
            raise AppError("FILE_TOO_LARGE", f"File size exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB limit.")
            
        # Check type (magic bytes for PDF)
        header = file.file.read(1024)
        file.file.seek(0)
        
        try:
            import magic
            mime_type = magic.from_buffer(header, mime=True)
            if mime_type != 'application/pdf':
                raise AppError("INVALID_FILE_TYPE", "File must be a valid PDF document.")
        except ImportError:
            # Fallback if python-magic is not properly installed with libmagic
            if not header.startswith(b'%PDF-'):
                raise AppError("INVALID_FILE_TYPE", "File must be a valid PDF document.")
                
        return size

    async def upload_document(self, file: UploadFile, user_id: uuid.UUID, background_tasks=None) -> DocumentUploadResponse:
        size = await self._validate_file(file, user_id)
        
        storage_url, public_id = await self.storage.upload(file)
        
        doc = Document(
            user_id=user_id,
            filename=file.filename or "unknown.pdf",
            storage_url=storage_url,
            storage_public_id=public_id,
            file_size_bytes=size,
            status=DocumentStatus.uploaded
        )
        
        created_doc = await self.repo.create(doc)
        
        # Enqueue Celery task
        # Transition to queued right away to reflect in UI
        await self.repo.update_status(created_doc.id, DocumentStatus.queued)
        try:
            process_document_ingestion.delay(str(created_doc.id))
        except Exception as e:
            if background_tasks:
                # Use FastAPI BackgroundTasks for synchronous fallback processing
                import logging
                logging.warning(f"Celery broker unavailable, falling back to background tasks: {e}")
                
                from app.services.ingestion_service import process_document_service
                background_tasks.add_task(process_document_service, str(created_doc.id))
            else:
                await self.repo.update_status(created_doc.id, DocumentStatus.failed, error_message="Failed to queue ingestion task (Broker unreachable)")
                created_doc.status = DocumentStatus.failed
            
        return DocumentUploadResponse(
            id=created_doc.id,
            filename=created_doc.filename,
            status=created_doc.status
        )

    async def delete_document(self, document_id: uuid.UUID, user_id: uuid.UUID) -> None:
        doc = await self.repo.get_by_id_for_user(document_id, user_id)
        if not doc:
            raise AppError("NOT_FOUND", "Document not found.", status_code=404)
            
        # Delete from storage
        try:
            await self.storage.delete(doc.storage_public_id)
        except Exception:
            pass # We still want to delete the DB record even if storage fails
            
        # Delete from vector store
        try:
            from app.vectorstore import get_vectorstore_provider
            vs = get_vectorstore_provider()
            vs.delete_document(str(document_id))
        except Exception:
            pass
            
        # Delete from DB
        await self.repo.delete(document_id)

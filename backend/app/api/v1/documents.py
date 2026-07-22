import uuid
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.document import DocumentRead, DocumentListItem, DocumentUploadResponse
from app.services.document_service import DocumentService
from app.services.storage_service import get_storage_service
from app.core.exceptions import AppError
from app.core.rate_limiter import rate_limit_general, rate_limit_upload

router = APIRouter(tags=["Documents"], dependencies=[Depends(rate_limit_general)])

def get_document_service(db: AsyncSession = Depends(get_db)) -> DocumentService:
    return DocumentService(db, get_storage_service())

from fastapi import BackgroundTasks
@router.post("", response_model=dict, dependencies=[Depends(rate_limit_upload)])
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
):
    result = await document_service.upload_document(file, current_user.id, background_tasks)
    return {"success": True, "data": result.model_dump(mode="json")}

@router.get("", response_model=dict)
async def list_documents(
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
):
    docs = await document_service.repo.list_by_user(current_user.id)
    # Serialize to schemas
    data = [DocumentListItem.model_validate(doc).model_dump(mode="json") for doc in docs]
    return {"success": True, "data": data}

@router.get("/{document_id}", response_model=dict)
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
):
    doc = await document_service.repo.get_by_id_for_user(document_id, current_user.id)
    if not doc:
        from app.core.exceptions import AppError
        raise AppError("NOT_FOUND", "Document not found.", status_code=404)
        
    # include page count and processing report in the output
    data = DocumentRead.model_validate(doc).model_dump(mode="json")
    data["page_count"] = doc.page_count
    data["processing_report"] = doc.processing_report
    
    return {"success": True, "data": data}

@router.get("/{document_id}/chunks", response_model=dict)
async def get_document_chunks(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    document_service: DocumentService = Depends(get_document_service)
):
    # Ensure ownership
    doc = await document_service.repo.get_by_id_for_user(document_id, current_user.id)
    if not doc:
        from app.core.exceptions import AppError
        raise AppError("NOT_FOUND", "Document not found.", status_code=404)
        
    from app.repositories.chunk_repository import ChunkRepository
    chunk_repo = ChunkRepository(db)
    chunks = await chunk_repo.list_by_document(document_id)
    
    from app.schemas.chunk import ChunkRead
    data = [ChunkRead.model_validate(c).model_dump(mode="json") for c in chunks]
    return {"success": True, "data": data}

@router.delete("/{document_id}", response_model=dict)
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
):
    await document_service.delete_document(document_id, current_user.id)
    return {"success": True, "data": {"message": "Document deleted successfully."}}

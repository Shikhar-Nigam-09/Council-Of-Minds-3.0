import os
import uuid
import shutil
from typing import Tuple
from abc import ABC, abstractmethod
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
from app.core.config import settings
from app.core.circuit_breaker import with_circuit_breaker

class StorageService(ABC):
    @abstractmethod
    async def upload(self, file: UploadFile) -> Tuple[str, str]:
        pass

    @abstractmethod
    async def delete(self, public_id: str) -> None:
        pass

class LocalMockStorageService(StorageService):
    def __init__(self):
        self.storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mock_storage")
        os.makedirs(self.storage_dir, exist_ok=True)

    async def upload(self, file: UploadFile) -> Tuple[str, str]:
        public_id = str(uuid.uuid4())
        extension = os.path.splitext(file.filename)[1] if file.filename else ".pdf"
        filename = f"{public_id}{extension}"
        file_path = os.path.join(self.storage_dir, filename)
        
        await file.seek(0)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        url = f"http://localhost:8000/mock_storage/{filename}"
        return url, public_id

    async def delete(self, public_id: str) -> None:
        for filename in os.listdir(self.storage_dir):
            if filename.startswith(public_id):
                os.remove(os.path.join(self.storage_dir, filename))
                break

class CloudinaryStorageService(StorageService):
    def __init__(self):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET
        )

    @with_circuit_breaker("cloudinary")
    async def upload(self, file: UploadFile) -> Tuple[str, str]:
        await file.seek(0)
        result = cloudinary.uploader.upload(
            file.file,
            resource_type="raw",
            folder="council_of_minds/documents"
        )
        return result["secure_url"], result["public_id"]

    @with_circuit_breaker("cloudinary")
    async def delete(self, public_id: str) -> None:
        cloudinary.uploader.destroy(public_id, resource_type="raw")

def get_storage_service() -> StorageService:
    if settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET:
        return CloudinaryStorageService()
    return LocalMockStorageService()

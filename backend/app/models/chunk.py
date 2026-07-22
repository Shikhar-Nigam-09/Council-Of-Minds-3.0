import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Integer, Enum, DateTime, ForeignKey, Index, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class ChunkType(str, enum.Enum):
    text = "text"
    heading = "heading"
    table = "table"
    image_caption = "image_caption"
    list = "list"

class SourceType(str, enum.Enum):
    pymupdf = "pymupdf"
    pdfplumber = "pdfplumber"
    ocr = "ocr"
    vision = "vision"

class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_type: Mapped[ChunkType] = mapped_column(Enum(ChunkType), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    section_title: Mapped[str | None] = mapped_column(String, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    caption_pending: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    vector_id: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index('ix_chunks_document_id_chunk_index', 'document_id', 'chunk_index'),
    )

"""add processing report and chunks table

Revision ID: 50bd4a3692bd
Revises: 9191f863414c
Create Date: 2026-07-21 13:06:58.104013

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50bd4a3692bd'
down_revision: Union[str, None] = '9191f863414c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from sqlalchemy.dialects.postgresql import ENUM
    # Add processing_report to documents
    from sqlalchemy.dialects import postgresql
    op.add_column('documents', sa.Column('processing_report', postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    # Create chunk enums
    chunk_type_enum = ENUM('text', 'heading', 'table', 'image_caption', 'list', name='chunktype', create_type=False)
    chunk_type_enum.create(op.get_bind(), checkfirst=True)
    
    source_type_enum = ENUM('pymupdf', 'pdfplumber', 'ocr', 'vision', name='sourcetype', create_type=False)
    source_type_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'chunks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('document_id', sa.UUID(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('chunk_type', chunk_type_enum, nullable=False),
        sa.Column('source_type', source_type_enum, nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=False),
        sa.Column('section_title', sa.String(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('caption_pending', sa.Boolean(), nullable=False, default=False),
        sa.Column('vector_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_chunks_document_id_chunk_index', 'chunks', ['document_id', 'chunk_index'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_chunks_document_id_chunk_index', table_name='chunks')
    op.drop_table('chunks')
    
    source_type_enum = sa.Enum('pymupdf', 'pdfplumber', 'ocr', 'vision', name='sourcetype')
    source_type_enum.drop(op.get_bind(), checkfirst=True)
    
    chunk_type_enum = sa.Enum('text', 'heading', 'table', 'image_caption', 'list', name='chunktype')
    chunk_type_enum.drop(op.get_bind(), checkfirst=True)
    
    op.drop_column('documents', 'processing_report')

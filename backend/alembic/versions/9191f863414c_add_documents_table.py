"""add documents table

Revision ID: 9191f863414c
Revises: 6e8a9d1f638a
Create Date: 2026-07-21 12:57:05.438904

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9191f863414c'
down_revision: Union[str, None] = '6e8a9d1f638a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from sqlalchemy.dialects.postgresql import ENUM
    # Use postgresql.ENUM with create_type=False to prevent Alembic from emitting a duplicate CREATE TYPE
    status_enum = ENUM('uploaded', 'queued', 'processing', 'partial', 'completed', 'failed', name='documentstatus', create_type=False)
    status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'documents',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('storage_url', sa.String(), nullable=False),
        sa.Column('storage_public_id', sa.String(), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('status', status_enum, nullable=False, default='uploaded'),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_documents_user_id_created_at', 'documents', ['user_id', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_documents_user_id_created_at', table_name='documents')
    op.drop_table('documents')
    status_enum = sa.Enum('uploaded', 'queued', 'processing', 'partial', 'completed', 'failed', name='documentstatus')
    status_enum.drop(op.get_bind(), checkfirst=True)

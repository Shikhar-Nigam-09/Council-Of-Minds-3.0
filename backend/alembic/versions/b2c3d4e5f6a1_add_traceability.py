"""add traceability columns to council configurations

Revision ID: b2c3d4e5f6a1
Revises: a1b2c3d4e5f6
Create Date: 2026-07-21 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'b2c3d4e5f6a1'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('council_configurations', sa.Column('model_name', sa.String(), server_default='unknown', nullable=False))
    op.add_column('council_configurations', sa.Column('prompt_version', sa.String(), server_default='unknown', nullable=False))
    op.add_column('council_configurations', sa.Column('latency_ms', sa.Integer(), nullable=True))
    op.add_column('council_configurations', sa.Column('retry_count', sa.Integer(), server_default='0', nullable=False))


def downgrade() -> None:
    op.drop_column('council_configurations', 'retry_count')
    op.drop_column('council_configurations', 'latency_ms')
    op.drop_column('council_configurations', 'prompt_version')
    op.drop_column('council_configurations', 'model_name')

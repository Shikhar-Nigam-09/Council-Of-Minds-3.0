"""Add evaluation_runs table

Revision ID: d4e5f6a1b2c3
Revises: c3d4e5f6a1b2
Create Date: 2026-07-21 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a1b2c3'
down_revision: Union[str, None] = 'c3d4e5f6a1b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('evaluation_runs',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('single_agent_answer', sa.Text(), nullable=True),
    sa.Column('single_agent_citations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('single_agent_latency_ms', sa.Integer(), nullable=True),
    sa.Column('single_agent_cost_estimate', sa.Numeric(), nullable=True),
    sa.Column('council_answer', sa.Text(), nullable=True),
    sa.Column('council_citations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('council_latency_ms', sa.Integer(), nullable=True),
    sa.Column('council_cost_estimate', sa.Numeric(), nullable=True),
    sa.Column('judge_status', sa.Enum('success', 'failed', name='judgestatus'), nullable=True),
    sa.Column('judge_verdict', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('judge_latency_ms', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_evaluation_runs_id'), 'evaluation_runs', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_evaluation_runs_id'), table_name='evaluation_runs')
    op.drop_table('evaluation_runs')
    op.execute('DROP TYPE judgestatus')

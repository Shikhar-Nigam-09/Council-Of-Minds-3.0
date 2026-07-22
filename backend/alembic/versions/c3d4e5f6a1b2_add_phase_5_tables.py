"""add phase 5 tables

Revision ID: c3d4e5f6a1b2
Revises: b2c3d4e5f6a1
Create Date: 2026-07-21 15:05:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'c3d4e5f6a1b2'
down_revision: Union[str, None] = 'b2c3d4e5f6a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns to messages
    op.add_column('messages', sa.Column('final_answer', sa.Text(), nullable=True))
    op.add_column('messages', sa.Column('synthesis_model', sa.String(), nullable=True))
    op.add_column('messages', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))

    # Create agent_outputs table
    op.create_table('agent_outputs',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('message_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('agent_name', sa.Enum('logical', 'practical', 'analytical', 'skeptical', 'ethics', name='agentname'), nullable=False),
    sa.Column('status', sa.Enum('success', 'failed', name='agentstatus'), nullable=False),
    sa.Column('summary', sa.Text(), nullable=True),
    sa.Column('evidence_points', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('weight_used', sa.Integer(), nullable=False),
    sa.Column('included_in_synthesis', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_agent_outputs_message_id_agent_name', 'agent_outputs', ['message_id', 'agent_name'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_agent_outputs_message_id_agent_name', table_name='agent_outputs')
    op.drop_table('agent_outputs')
    op.execute('DROP TYPE agentname')
    op.execute('DROP TYPE agentstatus')
    
    op.drop_column('messages', 'completed_at')
    op.drop_column('messages', 'synthesis_model')
    op.drop_column('messages', 'final_answer')

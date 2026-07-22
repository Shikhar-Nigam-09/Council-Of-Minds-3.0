"""add conversations

Revision ID: a1b2c3d4e5f6
Revises: 50bd4a3692bd
Create Date: 2026-07-21 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '50bd4a3692bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from sqlalchemy.dialects.postgresql import ENUM
    # conversations
    op.create_table('conversations',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('document_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_conversations_document_id', 'conversations', ['document_id'], unique=False)
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'], unique=False)
    
    # messages
    message_role_enum = ENUM('user', 'assistant', name='messagerole', create_type=False)
    message_role_enum.create(op.get_bind(), checkfirst=True)
    message_status_enum = ENUM('awaiting_confirmation', 'confirmed', 'completed', name='messagestatus', create_type=False)
    message_status_enum.create(op.get_bind(), checkfirst=True)
    
    op.create_table('messages',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('conversation_id', sa.UUID(), nullable=False),
    sa.Column('role', message_role_enum, nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('graph_thread_id', sa.String(), nullable=True),
    sa.Column('status', message_status_enum, nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'], unique=False)
    
    # council_configurations
    config_source_enum = ENUM('ai_recommendation', 'balanced_fallback', 'user_confirmed', name='configurationsource', create_type=False)
    config_source_enum.create(op.get_bind(), checkfirst=True)
    
    op.create_table('council_configurations',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('message_id', sa.UUID(), nullable=False),
    sa.Column('source', config_source_enum, nullable=False),
    sa.Column('logical_weight', sa.Integer(), nullable=False),
    sa.Column('practical_weight', sa.Integer(), nullable=False),
    sa.Column('analytical_weight', sa.Integer(), nullable=False),
    sa.Column('skeptical_weight', sa.Integer(), nullable=False),
    sa.Column('ethics_weight', sa.Integer(), nullable=False),
    sa.Column('logical_enabled', sa.Boolean(), nullable=False),
    sa.Column('practical_enabled', sa.Boolean(), nullable=False),
    sa.Column('analytical_enabled', sa.Boolean(), nullable=False),
    sa.Column('skeptical_enabled', sa.Boolean(), nullable=False),
    sa.Column('ethics_enabled', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('message_id')
    )


def downgrade() -> None:
    op.drop_table('council_configurations')
    op.drop_index('ix_messages_conversation_id', table_name='messages')
    op.drop_table('messages')
    op.drop_index('ix_conversations_user_id', table_name='conversations')
    op.drop_index('ix_conversations_document_id', table_name='conversations')
    op.drop_table('conversations')
    
    sa.Enum(name='configurationsource').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='messagestatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='messagerole').drop(op.get_bind(), checkfirst=True)

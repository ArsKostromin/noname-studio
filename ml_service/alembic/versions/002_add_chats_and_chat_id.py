"""add chats table and chat_id to chat_messages

Revision ID: 002_add_chats_and_chat_id
Revises: 001_create_chat_messages
Create Date: 2024-01-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_chats_and_chat_id'
down_revision = '001_create_chat_messages'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создаем таблицу chats
    op.create_table(
        'chats',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('external_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_chats_external_user_id', 'chats', ['external_user_id'])
    op.create_index('ix_chats_created_at', 'chats', ['created_at'])
    
    # Добавляем chat_id в chat_messages
    op.add_column('chat_messages', sa.Column('chat_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index('ix_chat_messages_chat_id', 'chat_messages', ['chat_id'])
    
    # Для существующих сообщений создаем дефолтный чат или удаляем их
    # Сначала удаляем существующие сообщения без чата (так как они не имеют смысла без чата)
    op.execute("DELETE FROM chat_messages")
    
    # Теперь делаем chat_id обязательным
    op.alter_column('chat_messages', 'chat_id', nullable=False)
    
    # Добавляем внешний ключ
    op.create_foreign_key(
        'fk_chat_messages_chat_id',
        'chat_messages', 'chats',
        ['chat_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Удаляем внешний ключ
    op.drop_constraint('fk_chat_messages_chat_id', 'chat_messages', type_='foreignkey')
    
    # Удаляем chat_id из chat_messages
    op.drop_index('ix_chat_messages_chat_id', table_name='chat_messages')
    op.drop_column('chat_messages', 'chat_id')
    
    # Удаляем таблицу chats
    op.drop_index('ix_chats_created_at', table_name='chats')
    op.drop_index('ix_chats_external_user_id', table_name='chats')
    op.drop_table('chats')

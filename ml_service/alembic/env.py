import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from db.base import Base
from db.models.user import User
from db.models.chat_message import ChatMessage
from db.models.chat import Chat
from config import settings

config = context.config

# Используем URL базы данных из настроек, если он не указан в alembic.ini
if config.get_main_option("sqlalchemy.url") == "postgresql+asyncpg://user:password@db:5432/dbname":
    # Заменяем на реальный URL из настроек (Alembic использует синхронный драйвер)
    db_url = settings.DATABASE_URL.replace("+asyncpg", "+psycopg2")
    config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

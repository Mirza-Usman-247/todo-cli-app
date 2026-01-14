"""
Alembic Environment Configuration

Configures Alembic for SQLModel migrations with async support.
"""

import asyncio
import os
import ssl
from logging.config import fileConfig
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlmodel import SQLModel

# Load environment variables
load_dotenv()

# Import all models to ensure they are registered with SQLModel.metadata
from src.models import Todo, User  # noqa: F401, E402

# Alembic Config object
config = context.config

# Set the database URL from environment
database_url = os.getenv("DATABASE_URL", "")
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Remove URL params that asyncpg doesn't support (handles SSL via connect_args)
parsed = urlparse(database_url)
if parsed.query:
    params = parse_qs(parsed.query)
    # Remove params not supported by asyncpg
    for param in ["sslmode", "channel_binding"]:
        params.pop(param, None)
    new_query = urlencode(params, doseq=True)
    database_url = urlunparse(parsed._replace(query=new_query))

config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# SQLModel metadata for 'autogenerate' support
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    Configures the context with just a URL and not an Engine.
    Calls to context.execute() emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the given connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations in 'online' mode with async engine.

    Creates an Engine and associates a connection with the context.
    """
    # Create SSL context for Neon PostgreSQL
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={"ssl": ssl_context},
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

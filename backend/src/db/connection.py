"""
Database Connection Module

Provides async database connection to Neon PostgreSQL using SQLModel/SQLAlchemy.
"""

import os
import ssl
from functools import lru_cache
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool


@lru_cache
def get_database_url() -> str:
    """
    Get the database URL from environment variables.

    Returns:
        The database connection string configured for async operation.
    """
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    # Ensure the URL uses asyncpg driver for async support
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://", "postgresql+asyncpg://", 1
        )
    elif not database_url.startswith("postgresql+asyncpg://"):
        # Handle sqlite for testing
        if database_url.startswith("sqlite"):
            pass  # Keep as-is for test databases
        else:
            raise ValueError(
                "DATABASE_URL must start with 'postgresql://' or 'postgresql+asyncpg://'"
            )

    # Remove URL params that asyncpg doesn't support (handles SSL via connect_args)
    parsed = urlparse(database_url)
    if parsed.query:
        params = parse_qs(parsed.query)
        # Remove params not supported by asyncpg
        for param in ["sslmode", "channel_binding"]:
            params.pop(param, None)
        new_query = urlencode(params, doseq=True)
        database_url = urlunparse(parsed._replace(query=new_query))

    return database_url


def get_engine() -> AsyncEngine:
    """
    Create and return an async database engine.

    Uses NullPool for serverless environments like Neon to avoid
    connection pooling issues with serverless cold starts.

    Returns:
        AsyncEngine configured for Neon PostgreSQL.
    """
    database_url = get_database_url()

    # For SQLite (testing), use different settings
    if "sqlite" in database_url:
        return create_async_engine(
            database_url,
            echo=os.getenv("DEBUG", "false").lower() == "true",
            future=True,
        )

    # For PostgreSQL (production with SSL or local without SSL)
    # Check if SSL is required (default: False for local development)
    use_ssl = os.getenv("DATABASE_SSL", "false").lower() == "true"

    connect_args = {}
    if use_ssl:
        # Create SSL context for secure connection (Neon, production)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ssl_context

    return create_async_engine(
        database_url,
        echo=os.getenv("DEBUG", "false").lower() == "true",
        future=True,
        # Use NullPool for serverless - each request gets fresh connection
        poolclass=NullPool,
        # Connection arguments
        connect_args=connect_args,
    )


# Global engine instance (lazy initialization)
_engine: AsyncEngine | None = None


def get_async_engine() -> AsyncEngine:
    """
    Get or create the global async engine instance.

    Returns:
        The global AsyncEngine instance.
    """
    global _engine
    if _engine is None:
        _engine = get_engine()
    return _engine

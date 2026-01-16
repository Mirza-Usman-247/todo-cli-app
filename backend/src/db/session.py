"""
Database Session Management

Provides async session management for FastAPI dependency injection.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.db.connection import get_async_engine


def get_session_factory() -> sessionmaker:
    """
    Create a session factory for async sessions.

    Returns:
        A sessionmaker configured for async operations.
    """
    engine = get_async_engine()
    return sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.

    Yields an async session that is properly closed after the request.

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()

    Yields:
        AsyncSession: An async database session.
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_session():
    """
    Context manager for database sessions (non-FastAPI context).

    Used by MCP tools and background tasks.

    Usage:
        async with get_session() as session:
            result = await session.execute(select(Item))
            return result.scalars().all()

    Returns:
        AsyncSession context manager.
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

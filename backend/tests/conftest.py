"""
Pytest Configuration and Fixtures

This module provides test fixtures for the Todo API backend tests.
"""

import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Set test environment before importing app
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from src.main import app
from src.db.session import get_db
from src.models import User, Todo  # noqa: F401 - Import models to register them


@pytest.fixture
def anyio_backend():
    """Specify the async backend for pytest-asyncio."""
    return "asyncio"


@pytest.fixture
async def test_engine():
    """Create a test database engine with tables."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """Create a test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.fixture
def test_app(test_engine):
    """Provide the FastAPI application instance for testing."""
    return app


@pytest.fixture
async def client(test_engine):
    """
    Provide an async HTTP client for testing API endpoints.

    Usage:
        async def test_example(client):
            response = await client.get("/")
            assert response.status_code == 200
    """
    # Create session factory using test engine
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with async_session() as session:
            yield session

    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Clean up override
    app.dependency_overrides.clear()


@pytest.fixture
def mock_user_id():
    """Provide a mock user ID for testing user-specific operations."""
    return "00000000-0000-0000-0000-000000000001"


@pytest.fixture
def mock_todo_data():
    """Provide mock todo data for testing."""
    return {
        "title": "Test Todo",
        "description": "This is a test todo item",
    }

"""
Database Initialization Script

Creates all database tables based on SQLModel models.
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

# Import all models to ensure they're registered with SQLModel
from src.models.user import User
from src.models.todo import Todo
from src.models.conversation import Conversation
from src.models.message import Message
try:
    from src.models.task import Task
    from src.models.event import Event
except ImportError:
    print("⚠️  Task and Event models not available")

from src.db.connection import get_database_url


async def init_db():
    """Initialize the database by creating all tables."""
    database_url = get_database_url()
    print(f"🔧 Initializing database at {database_url.split('@')[1] if '@' in database_url else database_url}")

    # Create engine
    engine = create_async_engine(database_url, echo=True)

    # Create all tables
    async with engine.begin() as conn:
        print("📋 Creating database tables...")
        await conn.run_sync(SQLModel.metadata.create_all)
        print("✅ Database tables created successfully!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())

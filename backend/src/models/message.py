"""
Message model for storing individual chat messages within a conversation.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship, Column, JSON

if TYPE_CHECKING:
    from src.models.conversation import Conversation


class Message(SQLModel, table=True):
    """
    Represents a single message in a conversation.

    Stores both user and assistant messages with metadata for tool calls.
    Supports conversation history loading (FR-022b: last 100 messages).

    Attributes:
        id: Primary key (UUID)
        conversation_id: Foreign key to conversations table
        role: Message role ('user' or 'assistant')
        content: Message text content
        metadata: Optional JSON metadata (tool calls, timestamps, etc.)
        timestamp: When message was created (indexed for efficient ordering)
    """
    __tablename__ = "message"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique message identifier"
    )
    conversation_id: UUID = Field(
        foreign_key="conversation.id",
        index=True,
        nullable=False,
        description="Parent conversation ID"
    )
    role: str = Field(
        max_length=20,
        nullable=False,
        description="Message role: 'user' or 'assistant'"
    )
    content: str = Field(
        nullable=False,
        description="Message text content"
    )
    tool_metadata: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Optional JSON metadata (tool calls, etc.)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Message creation timestamp (indexed for ordering)"
    )

    # Relationship to conversation
    # conversation: Optional["Conversation"] = Relationship(back_populates="messages")

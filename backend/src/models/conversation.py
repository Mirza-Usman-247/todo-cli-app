"""
Conversation model for storing user chat sessions.
Each user has one persistent conversation.
"""
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.message import Message


class Conversation(SQLModel, table=True):
    """
    Represents a persistent chat session for a user.

    One persistent conversation per user for all their chatbot interactions.
    Supports stateless backend architecture (FR-021, FR-022).

    Attributes:
        id: Primary key (UUID)
        user_id: Foreign key to users table (from Phase II)
        created_at: Timestamp when conversation was created
        updated_at: Timestamp of last message in conversation
    """
    __tablename__ = "conversation"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique conversation identifier"
    )
    user_id: UUID = Field(
        foreign_key="user.id",
        index=True,
        nullable=False,
        description="Owner user ID (one conversation per user)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Conversation creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last message timestamp"
    )

    # Relationships
    user: "User" = Relationship(back_populates="conversation")
    # messages: list["Message"] = Relationship(back_populates="conversation")

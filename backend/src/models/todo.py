"""
Todo SQLModel Entity

Represents a task owned by a user with title, description, and completion status.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.user import User


class TodoBase(SQLModel):
    """Base todo model with shared fields."""

    title: str = Field(
        max_length=255,
        description="Todo title (required, max 255 characters)",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Todo description (optional, max 1000 characters)",
    )
    is_completed: bool = Field(
        default=False,
        description="Completion status",
    )


class Todo(TodoBase, table=True):
    """
    Todo database model.

    Represents a task owned by a user with:
    - Title (required)
    - Description (optional)
    - Completion status
    - User isolation via foreign key
    - Timestamps for audit trail
    """

    __tablename__ = "todo"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique todo identifier",
    )
    user_id: UUID = Field(
        foreign_key="user.id",
        index=True,
        description="Owner user ID (foreign key to user.id)",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp",
    )

    # Relationships
    user: "User" = Relationship(back_populates="todos")


class TodoCreate(SQLModel):
    """Schema for creating a new todo."""

    title: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1000)


class TodoUpdate(SQLModel):
    """Schema for updating a todo (all fields optional)."""

    title: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    is_completed: bool | None = None


class TodoPublic(TodoBase):
    """Public todo response schema."""

    id: UUID
    created_at: datetime
    updated_at: datetime


class TodoListResponse(SQLModel):
    """Paginated todo list response."""

    todos: list[TodoPublic]
    total: int
    page: int

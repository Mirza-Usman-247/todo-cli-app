"""
User SQLModel Entity

Represents an authenticated user account with email/password credentials.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.todo import Todo


class UserBase(SQLModel):
    """Base user model with shared fields."""

    email: str = Field(
        max_length=255,
        index=True,
        unique=True,
        description="User email address (case-insensitive, normalized to lowercase)",
    )


class User(UserBase, table=True):
    """
    User database model.

    Represents an authenticated user in the system with:
    - Unique email (case-insensitive)
    - Hashed password
    - Soft delete support (deleted_at timestamp)
    - Timestamps for audit trail
    """

    __tablename__ = "user"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique user identifier",
    )
    password_hash: str = Field(
        max_length=255,
        description="Bcrypt hashed password",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Account creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp",
    )
    deleted_at: datetime | None = Field(
        default=None,
        description="Soft delete timestamp (30-day retention before purge)",
    )

    # Relationships
    todos: list["Todo"] = Relationship(back_populates="user")


class UserCreate(SQLModel):
    """Schema for creating a new user."""

    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)


class UserPublic(UserBase):
    """Public user response schema (excludes sensitive data)."""

    id: UUID


class UserInDB(UserBase):
    """User schema with database fields for internal use."""

    id: UUID
    password_hash: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

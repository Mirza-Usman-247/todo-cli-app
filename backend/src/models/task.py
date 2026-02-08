"""
Task Domain Model - Phase 3 Model
Represents a task with additional fields for Phase 3 implementation:
priority, tags, dueDate, completedAt, etc.

This model serves as the domain model for State Store persistence
"""
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import uuid

class Task(BaseModel):
    """Task entity for Phase 3 implementation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    isCompleted: bool = False

    # Phase 3 fields
    priority: str = Field("medium", pattern=r"^(low|medium|high|urgent)$")
    tags: List[str] = Field(default_factory=list, max_items=10)
    dueDate: Optional[str] = None  # ISO 8601 format
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    completedAt: Optional[str] = None

    # ETag for optimistic concurrency control
    etag: Optional[str] = None

    @field_validator("dueDate")
    @classmethod
    def validate_due_date(cls, v):
        """Validate that dueDate is in the future (with 2 minute grace period for clock skew)"""
        if v is None:
            return v
        try:
            due = datetime.fromisoformat(v.replace("Z", "+00:00"))
            now = datetime.utcnow().replace(tzinfo=None)
            # Allow dates within the last 2 minutes to handle processing delays and clock skew
            grace_period = timedelta(minutes=2)
            if due.replace(tzinfo=None) < (now - grace_period):
                raise ValueError("Due date must be in the future")
            return v
        except ValueError as e:
            if "Due date must be in the future" in str(e):
                raise
            raise ValueError("Invalid date format")

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        """Validate tag format"""
        for tag in v:
            if not tag.strip():
                raise ValueError("Tags cannot be empty")
            if len(tag) > 50:
                raise ValueError("Tag cannot exceed 50 characters")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "userId": "user-123",
                "title": "Complete project documentation",
                "description": "Finish writing the API documentation",
                "isCompleted": False,
                "priority": "high",
                "tags": ["urgent", "documentation"],
                "dueDate": "2026-12-31T23:59:59Z",
                "createdAt": "2026-01-01T00:00:00Z",
                "updatedAt": "2026-01-01T00:00:00Z",
                "completedAt": None,
                "etag": None
            }
        }


class TaskUpdate(BaseModel):
    """Model for task updates"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[str] = Field(None, pattern=r"^(low|medium|high|urgent)$")
    tags: Optional[List[str]] = Field(None, max_items=10)
    dueDate: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated title",
                "priority": "high",
                "tags": ["updated", "important"],
                "dueDate": "2026-12-31T23:59:59Z"
            }
        }

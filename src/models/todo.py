"""Todo data model"""
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Todo:
    """Represents a single todo item.

    Attributes:
        id: Unique identifier (positive integer, auto-incremented)
        title: Short description (1-500 characters, required)
        description: Detailed description (0-2000 characters, optional)
        completed: Completion status (default False)
        created_at: Creation timestamp (ISO 8601 format, UTC)
        updated_at: Last modification timestamp (ISO 8601 format, UTC)
    """
    id: int
    title: str
    description: str
    completed: bool
    created_at: str
    updated_at: str

    def __post_init__(self):
        """Validate todo fields after initialization.

        Raises:
            ValueError: If validation fails
        """
        # Validate ID
        if not isinstance(self.id, int) or self.id < 1:
            raise ValueError(f"ID must be a positive integer, got: {self.id}")

        # Validate title
        if not isinstance(self.title, str):
            raise ValueError(f"Title must be a string, got: {type(self.title).__name__}")

        title_stripped = self.title.strip()
        if not title_stripped:
            raise ValueError("Title cannot be empty")

        if len(self.title) > 500:
            raise ValueError(f"Title exceeds 500 character limit (got {len(self.title)})")

        # Validate description
        if not isinstance(self.description, str):
            raise ValueError(f"Description must be a string, got: {type(self.description).__name__}")

        if len(self.description) > 2000:
            raise ValueError(f"Description exceeds 2000 character limit (got {len(self.description)})")

        # Validate completed
        if not isinstance(self.completed, bool):
            raise ValueError(f"Completed must be a boolean, got: {type(self.completed).__name__}")

        # Validate timestamps (basic check for ISO 8601 format)
        if not isinstance(self.created_at, str):
            raise ValueError(f"created_at must be a string, got: {type(self.created_at).__name__}")

        if not isinstance(self.updated_at, str):
            raise ValueError(f"updated_at must be a string, got: {type(self.updated_at).__name__}")

        # Attempt to parse timestamps to validate format
        try:
            datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
        except ValueError as e:
            raise ValueError(f"created_at must be valid ISO 8601 format: {e}")

        try:
            datetime.fromisoformat(self.updated_at.replace('Z', '+00:00'))
        except ValueError as e:
            raise ValueError(f"updated_at must be valid ISO 8601 format: {e}")

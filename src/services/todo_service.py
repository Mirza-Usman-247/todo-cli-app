"""Todo service layer - business logic and file I/O"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from src.models.todo import Todo


class TodoService:
    """Service for managing todos with file-based persistence.

    Attributes:
        file_path: Path to the JSON storage file
        todos: In-memory list of Todo objects
        next_id: Next available ID for new todos
    """

    def __init__(self, file_path: str = "db/todos.json"):
        """Initialize TodoService.

        Args:
            file_path: Path to JSON file for storing todos (default: db/todos.json)
        """
        self.file_path = Path(file_path)
        self.todos: List[Todo] = []
        self.next_id: int = 1
        self.load()

    def load(self) -> None:
        """Load todos from JSON file into memory.

        Creates empty file if it doesn't exist.
        Creates timestamped backup if file is corrupted.
        Initializes with empty list on corruption.
        """
        # Ensure directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Create empty file if doesn't exist
        if not self.file_path.exists():
            self._save_raw({"todos": [], "next_id": 1})
            return

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate structure
            if not isinstance(data, dict) or "todos" not in data or "next_id" not in data:
                raise ValueError("Invalid JSON structure")

            # Load todos
            self.todos = []
            for todo_dict in data["todos"]:
                todo = Todo(
                    id=todo_dict["id"],
                    title=todo_dict["title"],
                    description=todo_dict["description"],
                    completed=todo_dict["completed"],
                    created_at=todo_dict["created_at"],
                    updated_at=todo_dict["updated_at"]
                )
                self.todos.append(todo)

            self.next_id = data["next_id"]

        except (json.JSONDecodeError, ValueError, KeyError, TypeError) as e:
            # File is corrupted - create backup and start fresh
            print(f"Warning: Data file corrupted. Error: {e}")
            self._create_timestamped_backup()
            self.todos = []
            self.next_id = 1
            self.save()

    def save(self) -> None:
        """Save current todos to JSON file atomically.

        Uses temp file + rename pattern for atomicity.
        """
        data = {
            "todos": [
                {
                    "id": todo.id,
                    "title": todo.title,
                    "description": todo.description,
                    "completed": todo.completed,
                    "created_at": todo.created_at,
                    "updated_at": todo.updated_at
                }
                for todo in self.todos
            ],
            "next_id": self.next_id
        }
        self._save_raw(data)

    def _save_raw(self, data: dict) -> None:
        """Save data to file atomically using temp file + rename.

        Args:
            data: Dictionary to save as JSON
        """
        # Ensure directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to temp file
        temp_path = self.file_path.with_suffix('.tmp')
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Atomic rename
        temp_path.replace(self.file_path)

    def _create_timestamped_backup(self) -> None:
        """Create timestamped backup of corrupted file.

        Backup format: todos.json.backup.YYYY-MM-DD-HHMMSS
        """
        if not self.file_path.exists():
            return

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
        backup_path = self.file_path.with_suffix(f'.json.backup.{timestamp}')

        try:
            import shutil
            shutil.copy2(self.file_path, backup_path)
            print(f"Created backup at {backup_path}")
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")

    def create_todo(self, title: str, description: str = "") -> Todo:
        """Create a new todo and persist to file.

        Args:
            title: Todo title (1-500 characters, required)
            description: Todo description (0-2000 characters, optional)

        Returns:
            Created Todo object

        Raises:
            ValueError: If validation fails
        """
        # Validate inputs
        title_stripped = title.strip()
        if not title_stripped:
            raise ValueError("Title cannot be empty")

        if len(title) > 500:
            raise ValueError(f"Title exceeds 500 character limit (got {len(title)})")

        if len(description) > 2000:
            raise ValueError(f"Description exceeds 2000 character limit (got {len(description)})")

        # Create timestamps
        now = datetime.now(timezone.utc).isoformat()

        # Create todo
        todo = Todo(
            id=self.next_id,
            title=title,
            description=description,
            completed=False,
            created_at=now,
            updated_at=now
        )

        # Add to list and increment ID
        self.todos.append(todo)
        self.next_id += 1

        # Persist
        self.save()

        return todo

    def get_all_todos(self) -> List[Todo]:
        """Get all todos.

        Returns:
            List of all Todo objects (may be empty)
        """
        return self.todos.copy()

    def get_todo_by_id(self, todo_id: int) -> Todo:
        """Get todo by ID.

        Args:
            todo_id: ID of todo to retrieve

        Returns:
            Todo object

        Raises:
            KeyError: If todo with given ID not found
        """
        for todo in self.todos:
            if todo.id == todo_id:
                return todo
        raise KeyError(f"Todo with ID {todo_id} not found")

    def toggle_todo(self, todo_id: int) -> Todo:
        """Toggle completion status of a todo.

        Args:
            todo_id: ID of todo to toggle

        Returns:
            Updated Todo object

        Raises:
            KeyError: If todo with given ID not found
        """
        todo = self.get_todo_by_id(todo_id)

        # Toggle completed status
        todo.completed = not todo.completed

        # Update timestamp
        todo.updated_at = datetime.now(timezone.utc).isoformat()

        # Persist
        self.save()

        return todo

    def update_todo(self, todo_id: int, new_title: Optional[str] = None,
                   new_description: Optional[str] = None) -> Todo:
        """Update todo title and/or description (partial updates supported).

        Args:
            todo_id: ID of todo to update
            new_title: New title (None = keep current)
            new_description: New description (None = keep current)

        Returns:
            Updated Todo object

        Raises:
            KeyError: If todo with given ID not found
            ValueError: If validation fails
        """
        todo = self.get_todo_by_id(todo_id)

        # Update title if provided
        if new_title is not None:
            title_stripped = new_title.strip()
            if not title_stripped:
                raise ValueError("Title cannot be empty")

            if len(new_title) > 500:
                raise ValueError(f"Title exceeds 500 character limit (got {len(new_title)})")

            todo.title = new_title

        # Update description if provided
        if new_description is not None:
            if len(new_description) > 2000:
                raise ValueError(f"Description exceeds 2000 character limit (got {len(new_description)})")

            todo.description = new_description

        # Update timestamp
        todo.updated_at = datetime.now(timezone.utc).isoformat()

        # Persist
        self.save()

        return todo

    def delete_todo(self, todo_id: int) -> Todo:
        """Delete a todo by ID.

        Note: Deleted IDs are never reused (next_id continues incrementing).

        Args:
            todo_id: ID of todo to delete

        Returns:
            Deleted Todo object (for confirmation message)

        Raises:
            KeyError: If todo with given ID not found
        """
        todo = self.get_todo_by_id(todo_id)

        # Remove from list
        self.todos.remove(todo)

        # Persist
        self.save()

        return todo

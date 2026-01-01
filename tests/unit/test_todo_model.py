"""Unit tests for Todo model validation"""
import pytest
from datetime import datetime, timezone

from src.models.todo import Todo


class TestTodoValidation:
    """Test Todo dataclass validation rules"""

    def test_valid_todo_creation(self):
        """Test creating a valid todo"""
        now = datetime.now(timezone.utc).isoformat()
        todo = Todo(
            id=1,
            title="Buy groceries",
            description="Milk, eggs, bread",
            completed=False,
            created_at=now,
            updated_at=now
        )
        assert todo.id == 1
        assert todo.title == "Buy groceries"
        assert todo.description == "Milk, eggs, bread"
        assert todo.completed is False
        assert todo.created_at == now
        assert todo.updated_at == now

    def test_empty_title_rejection(self):
        """Test that empty title is rejected"""
        now = datetime.now(timezone.utc).isoformat()
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Todo(
                id=1,
                title="",
                description="Test",
                completed=False,
                created_at=now,
                updated_at=now
            )

    def test_whitespace_only_title_rejection(self):
        """Test that whitespace-only title is rejected"""
        now = datetime.now(timezone.utc).isoformat()
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Todo(
                id=1,
                title="   ",
                description="Test",
                completed=False,
                created_at=now,
                updated_at=now
            )

    def test_title_length_limit_500(self):
        """Test that title exceeding 500 characters is rejected"""
        now = datetime.now(timezone.utc).isoformat()
        long_title = "x" * 501
        with pytest.raises(ValueError, match="Title exceeds 500 character limit"):
            Todo(
                id=1,
                title=long_title,
                description="Test",
                completed=False,
                created_at=now,
                updated_at=now
            )

    def test_title_exactly_500_chars_accepted(self):
        """Test that title with exactly 500 characters is accepted"""
        now = datetime.now(timezone.utc).isoformat()
        title_500 = "x" * 500
        todo = Todo(
            id=1,
            title=title_500,
            description="Test",
            completed=False,
            created_at=now,
            updated_at=now
        )
        assert len(todo.title) == 500

    def test_description_length_limit_2000(self):
        """Test that description exceeding 2000 characters is rejected"""
        now = datetime.now(timezone.utc).isoformat()
        long_desc = "x" * 2001
        with pytest.raises(ValueError, match="Description exceeds 2000 character limit"):
            Todo(
                id=1,
                title="Test",
                description=long_desc,
                completed=False,
                created_at=now,
                updated_at=now
            )

    def test_description_exactly_2000_chars_accepted(self):
        """Test that description with exactly 2000 characters is accepted"""
        now = datetime.now(timezone.utc).isoformat()
        desc_2000 = "x" * 2000
        todo = Todo(
            id=1,
            title="Test",
            description=desc_2000,
            completed=False,
            created_at=now,
            updated_at=now
        )
        assert len(todo.description) == 2000

    def test_empty_description_accepted(self):
        """Test that empty description is accepted"""
        now = datetime.now(timezone.utc).isoformat()
        todo = Todo(
            id=1,
            title="Test",
            description="",
            completed=False,
            created_at=now,
            updated_at=now
        )
        assert todo.description == ""

    def test_invalid_id_zero(self):
        """Test that ID of 0 is rejected"""
        now = datetime.now(timezone.utc).isoformat()
        with pytest.raises(ValueError, match="ID must be a positive integer"):
            Todo(
                id=0,
                title="Test",
                description="",
                completed=False,
                created_at=now,
                updated_at=now
            )

    def test_invalid_id_negative(self):
        """Test that negative ID is rejected"""
        now = datetime.now(timezone.utc).isoformat()
        with pytest.raises(ValueError, match="ID must be a positive integer"):
            Todo(
                id=-1,
                title="Test",
                description="",
                completed=False,
                created_at=now,
                updated_at=now
            )

    def test_invalid_timestamp_format(self):
        """Test that invalid timestamp format is rejected"""
        with pytest.raises(ValueError, match="must be valid ISO 8601 format"):
            Todo(
                id=1,
                title="Test",
                description="",
                completed=False,
                created_at="invalid-timestamp",
                updated_at="2026-01-01T10:00:00+00:00"
            )

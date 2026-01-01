"""Unit tests for TodoService"""
import pytest
import tempfile
import os
from pathlib import Path

from src.services.todo_service import TodoService
from src.models.todo import Todo


class TestTodoServiceCreate:
    """Test TodoService.create_todo() method"""

    @pytest.fixture
    def temp_db_file(self):
        """Create a temporary database file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_create_todo_basic(self, temp_db_file):
        """Test creating a basic todo"""
        service = TodoService(temp_db_file)
        todo = service.create_todo("Buy groceries", "Milk, eggs, bread")

        assert todo.id == 1
        assert todo.title == "Buy groceries"
        assert todo.description == "Milk, eggs, bread"
        assert todo.completed is False
        assert todo.created_at is not None
        assert todo.updated_at is not None

    def test_create_todo_without_description(self, temp_db_file):
        """Test creating a todo without description"""
        service = TodoService(temp_db_file)
        todo = service.create_todo("Call dentist")

        assert todo.id == 1
        assert todo.title == "Call dentist"
        assert todo.description == ""
        assert todo.completed is False

    def test_create_todo_id_increment(self, temp_db_file):
        """Test that IDs auto-increment"""
        service = TodoService(temp_db_file)

        todo1 = service.create_todo("First todo")
        todo2 = service.create_todo("Second todo")
        todo3 = service.create_todo("Third todo")

        assert todo1.id == 1
        assert todo2.id == 2
        assert todo3.id == 3

    def test_create_todo_persists_to_file(self, temp_db_file):
        """Test that created todo is persisted to file"""
        service = TodoService(temp_db_file)
        service.create_todo("Test todo", "Test description")

        # Create new service instance to reload from file
        service2 = TodoService(temp_db_file)
        todos = service2.get_all_todos()

        assert len(todos) == 1
        assert todos[0].title == "Test todo"
        assert todos[0].description == "Test description"

    def test_create_todo_empty_title_rejected(self, temp_db_file):
        """Test that empty title is rejected"""
        service = TodoService(temp_db_file)

        with pytest.raises(ValueError, match="Title cannot be empty"):
            service.create_todo("", "Description")

    def test_create_todo_whitespace_title_rejected(self, temp_db_file):
        """Test that whitespace-only title is rejected"""
        service = TodoService(temp_db_file)

        with pytest.raises(ValueError, match="Title cannot be empty"):
            service.create_todo("   ", "Description")

    def test_create_todo_title_too_long(self, temp_db_file):
        """Test that title exceeding 500 characters is rejected"""
        service = TodoService(temp_db_file)
        long_title = "x" * 501

        with pytest.raises(ValueError, match="Title exceeds 500 character limit"):
            service.create_todo(long_title)

    def test_create_todo_description_too_long(self, temp_db_file):
        """Test that description exceeding 2000 characters is rejected"""
        service = TodoService(temp_db_file)
        long_desc = "x" * 2001

        with pytest.raises(ValueError, match="Description exceeds 2000 character limit"):
            service.create_todo("Title", long_desc)

    def test_create_todo_added_to_in_memory_list(self, temp_db_file):
        """Test that created todo is added to in-memory list"""
        service = TodoService(temp_db_file)

        assert len(service.todos) == 0

        service.create_todo("Test todo")

        assert len(service.todos) == 1
        assert service.todos[0].title == "Test todo"


class TestTodoServiceGetAll:
    """Test TodoService.get_all_todos() method"""

    @pytest.fixture
    def temp_db_file(self):
        """Create a temporary database file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_get_all_todos_empty(self, temp_db_file):
        """Test getting all todos when list is empty"""
        service = TodoService(temp_db_file)
        todos = service.get_all_todos()

        assert todos == []
        assert len(todos) == 0

    def test_get_all_todos_with_data(self, temp_db_file):
        """Test getting all todos with multiple items"""
        service = TodoService(temp_db_file)

        service.create_todo("Todo 1", "Description 1")
        service.create_todo("Todo 2", "Description 2")
        service.create_todo("Todo 3", "Description 3")

        todos = service.get_all_todos()

        assert len(todos) == 3
        assert todos[0].title == "Todo 1"
        assert todos[1].title == "Todo 2"
        assert todos[2].title == "Todo 3"

    def test_get_all_todos_returns_copy(self, temp_db_file):
        """Test that get_all_todos returns a copy, not reference"""
        service = TodoService(temp_db_file)
        service.create_todo("Test todo")

        todos1 = service.get_all_todos()
        todos2 = service.get_all_todos()

        assert todos1 is not todos2
        assert todos1 == todos2


class TestTodoServiceToggle:
    """Test TodoService.toggle_todo() method"""

    @pytest.fixture
    def temp_db_file(self):
        """Create a temporary database file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_toggle_todo_incomplete_to_complete(self, temp_db_file):
        """Test toggling todo from incomplete to complete"""
        service = TodoService(temp_db_file)
        todo = service.create_todo("Test todo")

        assert todo.completed is False

        toggled = service.toggle_todo(1)

        assert toggled.completed is True
        assert toggled.id == 1

    def test_toggle_todo_complete_to_incomplete(self, temp_db_file):
        """Test toggling todo from complete back to incomplete"""
        service = TodoService(temp_db_file)
        todo = service.create_todo("Test todo")

        # Toggle to complete
        service.toggle_todo(1)
        # Toggle back to incomplete
        toggled = service.toggle_todo(1)

        assert toggled.completed is False

    def test_toggle_todo_invalid_id(self, temp_db_file):
        """Test toggling todo with invalid ID"""
        service = TodoService(temp_db_file)

        with pytest.raises(KeyError, match="Todo with ID 999 not found"):
            service.toggle_todo(999)

    def test_toggle_todo_persists(self, temp_db_file):
        """Test that toggle persists to file"""
        service = TodoService(temp_db_file)
        service.create_todo("Test todo")
        service.toggle_todo(1)

        # Reload from file
        service2 = TodoService(temp_db_file)
        todos = service2.get_all_todos()

        assert todos[0].completed is True


class TestTodoServiceUpdate:
    """Test TodoService.update_todo() method"""

    @pytest.fixture
    def temp_db_file(self):
        """Create a temporary database file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_update_todo_both_fields(self, temp_db_file):
        """Test updating both title and description"""
        service = TodoService(temp_db_file)
        todo = service.create_todo("Old title", "Old description")

        updated = service.update_todo(1, "New title", "New description")

        assert updated.title == "New title"
        assert updated.description == "New description"

    def test_update_todo_title_only(self, temp_db_file):
        """Test partial update - title only"""
        service = TodoService(temp_db_file)
        todo = service.create_todo("Old title", "Keep this description")

        updated = service.update_todo(1, new_title="New title")

        assert updated.title == "New title"
        assert updated.description == "Keep this description"

    def test_update_todo_description_only(self, temp_db_file):
        """Test partial update - description only"""
        service = TodoService(temp_db_file)
        todo = service.create_todo("Keep this title", "Old description")

        updated = service.update_todo(1, new_description="New description")

        assert updated.title == "Keep this title"
        assert updated.description == "New description"

    def test_update_todo_empty_title_rejected(self, temp_db_file):
        """Test that updating to empty title is rejected"""
        service = TodoService(temp_db_file)
        service.create_todo("Original title")

        with pytest.raises(ValueError, match="Title cannot be empty"):
            service.update_todo(1, new_title="")

    def test_update_todo_title_too_long(self, temp_db_file):
        """Test that updating to title >500 chars is rejected"""
        service = TodoService(temp_db_file)
        service.create_todo("Original title")

        with pytest.raises(ValueError, match="Title exceeds 500 character limit"):
            service.update_todo(1, new_title="x" * 501)

    def test_update_todo_description_too_long(self, temp_db_file):
        """Test that updating to description >2000 chars is rejected"""
        service = TodoService(temp_db_file)
        service.create_todo("Title")

        with pytest.raises(ValueError, match="Description exceeds 2000 character limit"):
            service.update_todo(1, new_description="x" * 2001)

    def test_update_todo_invalid_id(self, temp_db_file):
        """Test updating todo with invalid ID"""
        service = TodoService(temp_db_file)

        with pytest.raises(KeyError, match="Todo with ID 999 not found"):
            service.update_todo(999, new_title="New title")


class TestTodoServiceDelete:
    """Test TodoService.delete_todo() method"""

    @pytest.fixture
    def temp_db_file(self):
        """Create a temporary database file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_delete_todo_basic(self, temp_db_file):
        """Test deleting a todo"""
        service = TodoService(temp_db_file)
        todo = service.create_todo("Test todo")

        deleted = service.delete_todo(1)

        assert deleted.id == 1
        assert deleted.title == "Test todo"
        assert len(service.get_all_todos()) == 0

    def test_delete_todo_id_not_reused(self, temp_db_file):
        """Test that deleted IDs are never reused"""
        service = TodoService(temp_db_file)

        service.create_todo("Todo 1")
        service.create_todo("Todo 2")
        service.create_todo("Todo 3")

        # Delete todo 2
        service.delete_todo(2)

        # Create new todo - should get ID 4, not 2
        new_todo = service.create_todo("Todo 4")

        assert new_todo.id == 4
        assert service.next_id == 5

    def test_delete_todo_persists(self, temp_db_file):
        """Test that deletion persists to file"""
        service = TodoService(temp_db_file)
        service.create_todo("Todo 1")
        service.create_todo("Todo 2")

        service.delete_todo(1)

        # Reload from file
        service2 = TodoService(temp_db_file)
        todos = service2.get_all_todos()

        assert len(todos) == 1
        assert todos[0].id == 2

    def test_delete_todo_invalid_id(self, temp_db_file):
        """Test deleting todo with invalid ID"""
        service = TodoService(temp_db_file)

        with pytest.raises(KeyError, match="Todo with ID 999 not found"):
            service.delete_todo(999)

"""Integration tests for CLI workflows"""
import pytest
import tempfile
import os
from pathlib import Path
from io import StringIO
import sys

from src.services.todo_service import TodoService


class TestAddTodoWorkflow:
    """Integration tests for 'Add Todo' CLI workflow"""

    @pytest.fixture
    def temp_db_file(self):
        """Create a temporary database file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_add_todo_full_workflow(self, temp_db_file):
        """Test complete workflow: add todo → verify in memory → verify persistence"""
        service = TodoService(temp_db_file)

        # Simulate CLI adding a todo
        todo = service.create_todo("Buy groceries", "Milk, eggs, bread")

        # Verify todo in memory
        assert todo.id == 1
        assert todo.title == "Buy groceries"
        assert todo.description == "Milk, eggs, bread"
        assert todo.completed is False

        # Verify persistence by creating new service instance
        service2 = TodoService(temp_db_file)
        todos = service2.get_all_todos()

        assert len(todos) == 1
        assert todos[0].id == 1
        assert todos[0].title == "Buy groceries"
        assert todos[0].description == "Milk, eggs, bread"

    def test_add_multiple_todos_workflow(self, temp_db_file):
        """Test adding multiple todos in sequence"""
        service = TodoService(temp_db_file)

        # Add multiple todos
        todo1 = service.create_todo("Todo 1", "Description 1")
        todo2 = service.create_todo("Todo 2", "Description 2")
        todo3 = service.create_todo("Todo 3", "Description 3")

        # Verify all are persisted
        service2 = TodoService(temp_db_file)
        todos = service2.get_all_todos()

        assert len(todos) == 3
        assert [t.id for t in todos] == [1, 2, 3]
        assert [t.title for t in todos] == ["Todo 1", "Todo 2", "Todo 3"]

    def test_add_todo_restart_persistence(self, temp_db_file):
        """Test that todo persists after 'app restart' (simulated)"""
        # Session 1: Add todo
        service1 = TodoService(temp_db_file)
        service1.create_todo("Buy groceries", "Milk, eggs, bread")
        del service1  # Simulate app exit

        # Session 2: Restart app and verify todo exists
        service2 = TodoService(temp_db_file)
        todos = service2.get_all_todos()

        assert len(todos) == 1
        assert todos[0].title == "Buy groceries"
        assert todos[0].completed is False


class TestViewAllTodosWorkflow:
    """Integration tests for 'View All Todos' CLI workflow"""

    @pytest.fixture
    def temp_db_file(self):
        """Create a temporary database file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_view_all_empty_list(self, temp_db_file):
        """Test viewing todos when list is empty"""
        service = TodoService(temp_db_file)
        todos = service.get_all_todos()

        assert len(todos) == 0

    def test_view_all_with_todos(self, temp_db_file):
        """Test viewing multiple todos with different statuses"""
        service = TodoService(temp_db_file)

        # Create todos
        service.create_todo("Todo 1", "Incomplete")
        service.create_todo("Todo 2", "Will be complete")
        service.create_todo("Todo 3", "Also incomplete")

        # Toggle second todo to complete
        service.toggle_todo(2)

        # Verify view shows all todos with correct statuses
        todos = service.get_all_todos()

        assert len(todos) == 3
        assert todos[0].completed is False
        assert todos[1].completed is True
        assert todos[2].completed is False


class TestToggleStatusWorkflow:
    """Integration tests for 'Toggle Status' CLI workflow"""

    @pytest.fixture
    def temp_db_file(self):
        """Create a temporary database file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_toggle_workflow_incomplete_to_complete_to_incomplete(self, temp_db_file):
        """Test complete toggle workflow: create → complete → incomplete"""
        service = TodoService(temp_db_file)

        # Create todo (starts incomplete)
        todo = service.create_todo("Test todo")
        assert todo.completed is False

        # Toggle to complete
        toggled1 = service.toggle_todo(1)
        assert toggled1.completed is True

        # Toggle back to incomplete
        toggled2 = service.toggle_todo(1)
        assert toggled2.completed is False

    def test_toggle_invalid_id_error(self, temp_db_file):
        """Test toggle with invalid ID raises error"""
        service = TodoService(temp_db_file)

        with pytest.raises(KeyError):
            service.toggle_todo(999)


class TestUpdateTodoWorkflow:
    """Integration tests for 'Update Todo' CLI workflow"""

    @pytest.fixture
    def temp_db_file(self):
        """Create a temporary database file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_update_both_fields_workflow(self, temp_db_file):
        """Test updating both title and description"""
        service = TodoService(temp_db_file)

        # Create todo
        todo = service.create_todo("Old title", "Old description")

        # Update both fields
        updated = service.update_todo(1, "New title", "New description")

        assert updated.title == "New title"
        assert updated.description == "New description"

        # Verify persistence
        service2 = TodoService(temp_db_file)
        todos = service2.get_all_todos()
        assert todos[0].title == "New title"
        assert todos[0].description == "New description"

    def test_update_title_only_workflow(self, temp_db_file):
        """Test partial update: title only (press Enter for description)"""
        service = TodoService(temp_db_file)

        # Create todo
        service.create_todo("Old title", "Keep this description")

        # Update title only (None for description = keep current)
        updated = service.update_todo(1, new_title="New title")

        assert updated.title == "New title"
        assert updated.description == "Keep this description"

    def test_update_description_only_workflow(self, temp_db_file):
        """Test partial update: description only (press Enter for title)"""
        service = TodoService(temp_db_file)

        # Create todo
        service.create_todo("Keep this title", "Old description")

        # Update description only (None for title = keep current)
        updated = service.update_todo(1, new_description="New description")

        assert updated.title == "Keep this title"
        assert updated.description == "New description"


class TestDeleteTodoWorkflow:
    """Integration tests for 'Delete Todo' CLI workflow"""

    @pytest.fixture
    def temp_db_file(self):
        """Create a temporary database file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_delete_workflow_and_persistence(self, temp_db_file):
        """Test delete workflow with persistence verification"""
        service = TodoService(temp_db_file)

        # Create 5 todos
        for i in range(1, 6):
            service.create_todo(f"Todo {i}", f"Description {i}")

        # Delete todo #3
        deleted = service.delete_todo(3)
        assert deleted.id == 3

        # Verify 4 remain
        todos = service.get_all_todos()
        assert len(todos) == 4
        assert 3 not in [t.id for t in todos]

        # Create new todo - should get ID 6 (not 3)
        new_todo = service.create_todo("Todo 6")
        assert new_todo.id == 6

        # Verify persistence
        service2 = TodoService(temp_db_file)
        todos2 = service2.get_all_todos()
        assert len(todos2) == 5
        assert [t.id for t in todos2] == [1, 2, 4, 5, 6]

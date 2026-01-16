"""
Todo Service

Business logic for todo CRUD operations with user isolation.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.todo import Todo, TodoCreate, TodoUpdate, TodoPublic, TodoListResponse


class TodoService:
    """Service for todo operations with user isolation."""

    def __init__(self, db: AsyncSession):
        """Initialize todo service with database session."""
        self.db = db

    async def create_todo(self, user_id: UUID, data: TodoCreate) -> Todo:
        """
        Create a new todo for a user.

        Args:
            user_id: Owner user's UUID.
            data: Todo creation data.

        Returns:
            Created Todo instance.
        """
        todo = Todo(
            user_id=user_id,
            title=data.title,
            description=data.description,
        )

        self.db.add(todo)
        await self.db.commit()
        await self.db.refresh(todo)

        return todo

    async def get_todos(
        self, user_id: UUID, page: int = 1, limit: int = 20
    ) -> TodoListResponse:
        """
        Get paginated list of todos for a user.

        Args:
            user_id: Owner user's UUID.
            page: Page number (1-indexed).
            limit: Items per page (max 20).

        Returns:
            TodoListResponse with paginated todos.
        """
        # Ensure limit doesn't exceed 20
        limit = min(limit, 20)
        offset = (page - 1) * limit

        # Get total count
        count_query = select(func.count()).select_from(Todo).where(
            Todo.user_id == user_id
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Get todos with pagination, sorted by created_at DESC (newest first)
        query = (
            select(Todo)
            .where(Todo.user_id == user_id)
            .order_by(Todo.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(query)
        todos = result.scalars().all()

        # Convert to public schema
        todos_public = [
            TodoPublic(
                id=todo.id,
                title=todo.title,
                description=todo.description,
                is_completed=todo.is_completed,
                created_at=todo.created_at,
                updated_at=todo.updated_at,
            )
            for todo in todos
        ]

        return TodoListResponse(
            todos=todos_public,
            total=total,
            page=page,
        )

    async def get_todo(self, user_id: UUID, todo_id: UUID) -> Todo | None:
        """
        Get a single todo by ID.

        Args:
            user_id: Owner user's UUID (for isolation check).
            todo_id: Todo's UUID.

        Returns:
            Todo if found and owned by user, None otherwise.
        """
        query = select(Todo).where(
            Todo.id == todo_id,
            Todo.user_id == user_id,  # User isolation
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_todo(
        self, user_id: UUID, todo_id: UUID, data: TodoUpdate
    ) -> Todo | None:
        """
        Update a todo.

        Args:
            user_id: Owner user's UUID (for isolation check).
            todo_id: Todo's UUID.
            data: Update data (partial update supported).

        Returns:
            Updated Todo if found and owned by user, None otherwise.
        """
        todo = await self.get_todo(user_id, todo_id)
        if not todo:
            return None

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(todo, field, value)

        todo.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(todo)

        return todo

    async def delete_todo(self, user_id: UUID, todo_id: UUID) -> bool:
        """
        Delete a todo.

        Args:
            user_id: Owner user's UUID (for isolation check).
            todo_id: Todo's UUID.

        Returns:
            True if deleted, False if not found or not owned by user.
        """
        todo = await self.get_todo(user_id, todo_id)
        if not todo:
            return False

        await self.db.delete(todo)
        await self.db.commit()

        return True

    async def toggle_completion(self, user_id: UUID, todo_id: UUID) -> Todo | None:
        """
        Toggle a todo's completion status.

        Args:
            user_id: Owner user's UUID.
            todo_id: Todo's UUID.

        Returns:
            Updated Todo if found, None otherwise.
        """
        todo = await self.get_todo(user_id, todo_id)
        if not todo:
            return None

        todo.is_completed = not todo.is_completed
        todo.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(todo)

        return todo

    async def find_tasks_by_title(
        self, user_id: UUID, search_term: str
    ) -> list[Todo]:
        """
        Find tasks by case-insensitive substring match on title (FR-007).

        Used by MCP tools to resolve task references from natural language.

        Args:
            user_id: Owner user's UUID (for isolation).
            search_term: Search string (case-insensitive substring match).

        Returns:
            List of matching todos.
        """
        # Case-insensitive substring match using LOWER and LIKE
        query = (
            select(Todo)
            .where(
                Todo.user_id == user_id,
                func.lower(Todo.title).contains(search_term.lower())
            )
            .order_by(Todo.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

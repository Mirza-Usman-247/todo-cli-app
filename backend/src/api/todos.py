"""
Todo API Endpoints

REST API endpoints for todo CRUD operations.
All endpoints require authentication and enforce user isolation.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import AuthenticatedUser, require_auth
from src.db import get_db
from src.models.todo import TodoCreate, TodoListResponse, TodoPublic, TodoUpdate
from src.services.todo_service import TodoService

router = APIRouter(prefix="/todos", tags=["Todos"])


@router.get("", response_model=TodoListResponse)
async def list_todos(
    current_user: AuthenticatedUser,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=20, description="Items per page (max 20)"),
    db: AsyncSession = Depends(get_db),
):
    """
    List user's todos with pagination.

    - Requires authentication
    - Returns only the authenticated user's todos
    - Sorted by created_at DESC (newest first)
    - Paginated with max 20 items per page
    """
    todo_service = TodoService(db)
    return await todo_service.get_todos(current_user.id, page, limit)


@router.post("", response_model=TodoPublic, status_code=status.HTTP_201_CREATED)
async def create_todo(
    data: TodoCreate,
    current_user: AuthenticatedUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new todo.

    - Requires authentication
    - Associates todo with authenticated user
    - Title is required (max 255 chars)
    - Description is optional (max 1000 chars)
    """
    todo_service = TodoService(db)
    todo = await todo_service.create_todo(current_user.id, data)

    return TodoPublic(
        id=todo.id,
        title=todo.title,
        description=todo.description,
        is_completed=todo.is_completed,
        created_at=todo.created_at,
        updated_at=todo.updated_at,
    )


@router.get("/{todo_id}", response_model=TodoPublic)
async def get_todo(
    todo_id: UUID,
    current_user: AuthenticatedUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single todo by ID.

    - Requires authentication
    - Returns 404 if todo not found or not owned by user
    """
    todo_service = TodoService(db)
    todo = await todo_service.get_todo(current_user.id, todo_id)

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    return TodoPublic(
        id=todo.id,
        title=todo.title,
        description=todo.description,
        is_completed=todo.is_completed,
        created_at=todo.created_at,
        updated_at=todo.updated_at,
    )


@router.put("/{todo_id}", response_model=TodoPublic)
async def update_todo(
    todo_id: UUID,
    data: TodoUpdate,
    current_user: AuthenticatedUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a todo.

    - Requires authentication
    - Supports partial updates (only provided fields are updated)
    - Returns 404 if todo not found or not owned by user
    """
    todo_service = TodoService(db)
    todo = await todo_service.update_todo(current_user.id, todo_id, data)

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    return TodoPublic(
        id=todo.id,
        title=todo.title,
        description=todo.description,
        is_completed=todo.is_completed,
        created_at=todo.created_at,
        updated_at=todo.updated_at,
    )


@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: UUID,
    current_user: AuthenticatedUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a todo.

    - Requires authentication
    - Returns 404 if todo not found or not owned by user
    - Permanently removes the todo from database
    """
    todo_service = TodoService(db)
    deleted = await todo_service.delete_todo(current_user.id, todo_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    return {"success": True, "message": "Todo deleted successfully"}

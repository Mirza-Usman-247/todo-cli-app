"""
MCP Tool: add_task

Creates a new task for the user (FR-012, FR-005).
"""
from uuid import UUID

from src.mcp.server import mcp
from src.mcp.schemas import TaskResult
from src.models.todo import TodoCreate
from src.services.todo_service import TodoService
from src.db.session import get_session


@mcp.tool()
async def add_task(
    user_id: str,
    title: str,
    description: str = ""
) -> dict:
    """
    Create a new task for the user.

    Args:
        user_id: User UUID as string
        title: Task title (required)
        description: Task description (optional)

    Returns:
        TaskResult with success status and task ID
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return TaskResult(
            success=False,
            message="Invalid user_id format"
        ).model_dump()

    async with get_session() as session:
        service = TodoService(session)
        todo_data = TodoCreate(title=title, description=description or None)

        try:
            todo = await service.create_todo(user_uuid, todo_data)
            return TaskResult(
                success=True,
                message=f"Task created: {todo.title}",
                task_id=todo.id
            ).model_dump()
        except Exception as e:
            return TaskResult(
                success=False,
                message=f"Failed to create task: {str(e)}"
            ).model_dump()

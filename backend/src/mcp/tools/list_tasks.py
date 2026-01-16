"""
MCP Tool: list_tasks

Lists user's tasks with optional filtering (FR-012, FR-006).
"""
from uuid import UUID
from typing import Optional

from src.mcp.server import mcp
from src.mcp.schemas import TaskInfo
from src.services.todo_service import TodoService
from src.db.session import get_session


@mcp.tool()
async def list_tasks(
    user_id: str,
    filter: Optional[str] = None
) -> dict:
    """
    List user's tasks with optional title filtering.

    Args:
        user_id: User UUID as string
        filter: Optional search term for case-insensitive title filtering

    Returns:
        Dictionary with task list and count
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return {
            "error": "Invalid user_id format",
            "tasks": [],
            "count": 0
        }

    async with get_session() as session:
        service = TodoService(session)

        if filter:
            # Case-insensitive substring match (FR-007)
            todos = await service.find_tasks_by_title(user_uuid, filter)
        else:
            # Get all tasks (paginated)
            response = await service.get_todos(user_uuid, page=1, limit=20)
            todos = [
                await service.get_todo(user_uuid, todo.id)
                for todo in response.todos
            ]
            todos = [t for t in todos if t is not None]

        # Convert to TaskInfo schema
        tasks = [
            TaskInfo(
                id=todo.id,
                title=todo.title,
                description=todo.description,
                is_completed=todo.is_completed
            ).model_dump()
            for todo in todos
        ]

        return {
            "tasks": tasks,
            "count": len(tasks)
        }

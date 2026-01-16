"""
MCP Tool: update_task

Updates a task's title or description (FR-012, FR-008).
"""
from uuid import UUID
from typing import Optional

from src.mcp.server import mcp
from src.mcp.schemas import TaskResult
from src.models.todo import TodoUpdate
from src.services.todo_service import TodoService
from src.db.session import get_session


@mcp.tool()
async def update_task(
    user_id: str,
    task_ref: str,
    new_title: Optional[str] = None,
    new_description: Optional[str] = None
) -> dict:
    """
    Update a task's title or description.

    Args:
        user_id: User UUID as string
        task_ref: Task UUID or title substring for matching
        new_title: New title (optional)
        new_description: New description (optional)

    Returns:
        TaskResult with success status
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return TaskResult(
            success=False,
            message="Invalid user_id format"
        ).model_dump()

    if not new_title and not new_description:
        return TaskResult(
            success=False,
            message="At least one of new_title or new_description must be provided"
        ).model_dump()

    async with get_session() as session:
        service = TodoService(session)

        # Try UUID first
        try:
            task_uuid = UUID(task_ref)
            todo = await service.get_todo(user_uuid, task_uuid)
        except ValueError:
            # Fallback to title substring match (FR-007)
            matches = await service.find_tasks_by_title(user_uuid, task_ref)
            if not matches:
                return TaskResult(
                    success=False,
                    message=f"No task found matching '{task_ref}'"
                ).model_dump()
            if len(matches) > 1:
                titles = [f"'{t.title}'" for t in matches]
                return TaskResult(
                    success=False,
                    message=f"Multiple tasks match '{task_ref}': {', '.join(titles)}. Please be more specific."
                ).model_dump()
            todo = matches[0]

        if not todo:
            return TaskResult(
                success=False,
                message="Task not found"
            ).model_dump()

        update_data = TodoUpdate(
            title=new_title,
            description=new_description
        )
        updated_todo = await service.update_todo(user_uuid, todo.id, update_data)

        if updated_todo:
            return TaskResult(
                success=True,
                message=f"Task updated: {updated_todo.title}",
                task_id=updated_todo.id
            ).model_dump()
        else:
            return TaskResult(
                success=False,
                message="Failed to update task"
            ).model_dump()

"""
MCP Tool: complete_task

Marks a task as completed (FR-012, FR-007).
"""
from uuid import UUID

from src.mcp.server import mcp
from src.mcp.schemas import TaskResult
from src.services.todo_service import TodoService
from src.db.session import get_session


@mcp.tool()
async def complete_task(
    user_id: str,
    task_ref: str
) -> dict:
    """
    Mark a task as completed.

    Args:
        user_id: User UUID as string
        task_ref: Task UUID or title substring for matching

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

        if todo.is_completed:
            return TaskResult(
                success=True,
                message=f"Task '{todo.title}' was already completed",
                task_id=todo.id
            ).model_dump()

        await service.toggle_completion(user_uuid, todo.id)
        return TaskResult(
            success=True,
            message=f"Task completed: {todo.title}",
            task_id=todo.id
        ).model_dump()

"""
Event-Driven Tasks API - Phase 5
HTTP endpoints for task management using Dapr State Store and Pub/Sub
Implements T048-T056 from tasks.md
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

from src.services.task_state_service import TaskStateService
from src.services.search_service import SearchService
from src.services.reminder_service import ReminderService
from src.services.recurring_service import RecurringService
from src.models.task import Task, TaskUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events/tasks", tags=["Tasks (Event-Driven)"])


# Request/Response Models
class TaskCreateRequest(BaseModel):
    """Request model for creating a task"""
    userId: str
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: str = Field(default="medium", pattern=r"^(low|medium|high|urgent)$")
    tags: Optional[List[str]] = Field(default_factory=list, max_items=10)
    dueDate: Optional[str] = None
    recurring: Optional[str] = None  # e.g., "daily", "weekly", "monthly", "custom:48"


class TaskResponse(BaseModel):
    """Response model for task operations"""
    success: bool
    task: Optional[Task] = None
    error: Optional[str] = None


class SearchQuery(BaseModel):
    """Query parameters for search"""
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    keyword: Optional[str] = None
    sortBy: str = "createdAt"
    ascending: bool = False


# Health Check (must be before parameterized routes)

@router.get("/health")
async def health_check():
    """
    Health check endpoint (T056)
    """
    return {
        "status": "healthy",
        "service": "tasks-event-driven-api",
        "dapr_components": ["pubsub-kafka", "statestore-redis", "scheduler"]
    }


# Task CRUD Endpoints

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(request: TaskCreateRequest):
    """
    Create a new task (T048)
    Publishes todo-created event to Kafka
    """
    try:
        # Check if recurring task
        if request.recurring:
            task_id, error = await RecurringService.create_recurring_task(
                user_id=request.userId,
                title=request.title,
                description=request.description,
                priority=request.priority,
                tags=request.tags,
                due_date=request.dueDate,
                recurrence_pattern=request.recurring
            )

            if error:
                raise HTTPException(status_code=400, detail=error)

            # Fetch the created task
            task = await TaskStateService.get_task(task_id)
            return TaskResponse(success=True, task=task)

        else:
            # Regular task
            task, error = await TaskStateService.create_task(
                user_id=request.userId,
                title=request.title,
                description=request.description,
                priority=request.priority,
                tags=request.tags,
                due_date=request.dueDate
            )

            if error:
                raise HTTPException(status_code=400, detail=error)

            return TaskResponse(success=True, task=task)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """
    Get a single task by ID (T050)
    """
    try:
        task = await TaskStateService.get_task(task_id)

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        return TaskResponse(success=True, task=task)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, user_id: str, update_data: TaskUpdate):
    """
    Update a task (T051)
    Publishes todo-updated event to Kafka
    """
    try:
        task, error = await TaskStateService.update_task(
            task_id=task_id,
            user_id=user_id,
            update_data=update_data
        )

        if error:
            if "not found" in error.lower():
                raise HTTPException(status_code=404, detail=error)
            elif "Unauthorized" in error:
                raise HTTPException(status_code=403, detail=error)
            elif "Concurrent update" in error:
                raise HTTPException(status_code=409, detail=error)
            else:
                raise HTTPException(status_code=400, detail=error)

        return TaskResponse(success=True, task=task)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str, user_id: str):
    """
    Delete a task (T052)
    Publishes todo-deleted event to Kafka
    """
    try:
        success, error = await TaskStateService.delete_task(
            task_id=task_id,
            user_id=user_id
        )

        if not success:
            if error and "not found" in error.lower():
                raise HTTPException(status_code=404, detail=error)
            elif error and "Unauthorized" in error:
                raise HTTPException(status_code=403, detail=error)
            else:
                raise HTTPException(status_code=400, detail=error or "Failed to delete task")

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_completion(task_id: str, user_id: str, completed: Optional[bool] = None):
    """
    Toggle task completion status (T053)
    Publishes todo-updated event to Kafka
    """
    try:
        task, error = await TaskStateService.mark_complete(
            task_id=task_id,
            user_id=user_id,
            completed=completed
        )

        if error:
            if "not found" in error.lower():
                raise HTTPException(status_code=404, detail=error)
            elif "Unauthorized" in error:
                raise HTTPException(status_code=403, detail=error)
            else:
                raise HTTPException(status_code=400, detail=error)

        # Handle recurring task completion
        if task and task.isCompleted:
            is_recurring, pattern = RecurringService.is_recurring_task(task.tags)

            if is_recurring and pattern:
                logger.info(f"Task {task_id} is recurring ({pattern}), creating next instance...")
                new_task_id, rec_error = await RecurringService.handle_recurring_completion(
                    task_id=task_id,
                    user_id=user_id,
                    title=task.title,
                    description=task.description,
                    priority=task.priority,
                    tags=task.tags,
                    recurrence_pattern=pattern
                )

                if rec_error:
                    logger.warning(f"⚠️  Failed to create next recurring instance: {rec_error}")

        return TaskResponse(success=True, task=task)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to toggle completion for task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Search and Filter Endpoint

@router.get("/", response_model=List[Task])
async def list_tasks(user_id: str, limit: int = 100):
    """
    List all tasks for a user (T049)
    """
    try:
        tasks = await TaskStateService.list_tasks(user_id, limit)
        return tasks

    except Exception as e:
        logger.error(f"❌ Failed to list tasks for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=List[Task])
async def search_tasks(user_id: str, query: SearchQuery):
    """
    Search and filter tasks (T054)
    Fetches all user tasks, then applies filters and sorting in-memory.
    """
    try:
        # Get all tasks for the user
        all_tasks = await TaskStateService.list_tasks(user_id, limit=1000)

        if not all_tasks:
            return []

        # Apply filters and sorting
        filtered_tasks = SearchService.apply_filters(
            tasks=all_tasks,
            priority=query.priority,
            tags=query.tags,
            keyword=query.keyword,
            sort_by=query.sortBy,
            ascending=query.ascending
        )

        return filtered_tasks

    except Exception as e:
        logger.error(f"❌ Failed to search tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Reminder Management

@router.post("/reminders/{task_id}", response_model=TaskResponse)
async def trigger_reminder(task_id: str, user_id: str, minutes_before: int = 1440):
    """
    Manually trigger/schedule a reminder for a task (T055)
    """
    try:
        # Get task
        task = await TaskStateService.get_task(task_id)

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if task.userId != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")

        if not task.dueDate:
            raise HTTPException(status_code=400, detail="Task does not have a due date")

        # Schedule reminder
        success, error = await ReminderService.schedule_reminder(
            todo_id=task_id,
            user_id=user_id,
            title=task.title,
            due_date=task.dueDate,
            minutes_before=minutes_before
        )

        if not success:
            raise HTTPException(status_code=400, detail=error or "Failed to schedule reminder")

        return TaskResponse(success=True, task=task)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to trigger reminder for task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Job Callback Endpoint (for Dapr Jobs API)

@router.post("/jobs/callback")
async def handle_job_callback(job_data: Dict[str, Any]):
    """
    Callback endpoint for Dapr Jobs API
    When a scheduled job fires, Dapr calls this endpoint with the job payload
    This publishes the reminder event to Kafka
    """
    try:
        logger.info(f"📞 Received job callback: {job_data}")

        # Extract payload from job data
        payload = job_data.get("data", {})
        event_type = payload.get("eventType", "todo-reminder")

        if event_type == "todo-reminder":
            # Publish reminder event to Kafka
            from src.events.publishers import TodoReminderPublisher

            success, error = await TodoReminderPublisher.publish(
                todo_id=payload.get("todoId"),
                user_id=payload.get("userId"),
                title=payload.get("title"),
                due_date=payload.get("dueDate"),
                minutes_before=payload.get("minutesBefore", 1440)
            )

            if success:
                logger.info(f"✅ Published reminder event for job callback")
                return {"status": "success", "message": "Reminder event published"}
            else:
                logger.error(f"❌ Failed to publish reminder: {error}")
                raise HTTPException(status_code=500, detail=error)
        else:
            logger.warning(f"⚠️  Unknown event type in job callback: {event_type}")
            return {"status": "ignored", "message": f"Unknown event type: {event_type}"}

    except Exception as e:
        logger.error(f"❌ Failed to handle job callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Test Endpoint - Manually trigger reminder notification

@router.post("/test-reminder/{task_id}")
async def test_reminder_notification(task_id: str, user_id: str):
    """
    TEST ENDPOINT: Manually trigger a reminder notification
    This demonstrates the reminder notification system without scheduling
    """
    try:
        # Get task details
        task = await TaskStateService.get_task(task_id)

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if task.userId != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")

        # Publish reminder event to Kafka
        from src.events.publishers import TodoReminderPublisher

        success, error = await TodoReminderPublisher.publish(
            todo_id=task_id,
            user_id=user_id,
            title=task.title,
            due_date=task.dueDate or "",
            minutes_before=0  # Immediate reminder
        )

        if success:
            return {
                "status": "success",
                "message": f"✅ Reminder notification triggered! Check backend logs for: '📧 REMINDER: Task '{task.title}' (ID: {task_id})'"
            }
        else:
            raise HTTPException(status_code=500, detail=error)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to test reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))

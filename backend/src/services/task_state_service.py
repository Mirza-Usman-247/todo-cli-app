"""
Task Service Layer - Phase 5 Event-Driven Architecture
Uses Dapr State Store (Redis) instead of database
Publishes events to Kafka via Dapr Pub/Sub
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
import logging
import uuid

from src.dapr.state import state_client
from src.dapr.jobs import DaprJobsClient
from src.models.task import Task, TaskUpdate
from src.events.publishers import (
    TodoCreatedPublisher,
    TodoUpdatedPublisher,
    TodoDeletedPublisher
)

logger = logging.getLogger(__name__)

# Initialize Dapr Jobs client
jobs_client = DaprJobsClient()


class TaskStateService:
    """
    Task CRUD service using Dapr State Store with event publishing
    Implements T033-T038 from tasks.md
    """

    @staticmethod
    async def create_task(
        user_id: str,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        tags: Optional[List[str]] = None,
        due_date: Optional[str] = None
    ) -> Tuple[Optional[Task], Optional[str]]:
        """
        Create a new task (T033)

        Args:
            user_id: ID of the user creating the task
            title: Task title
            description: Task description
            priority: Task priority (low/medium/high/urgent)
            tags: List of tags
            due_date: Due date in ISO format

        Returns:
            Tuple of (Task, error_message)
        """
        try:
            # Validate due date is in future if provided
            if due_date:
                try:
                    due_dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                    now = datetime.utcnow().replace(tzinfo=None)
                    if due_dt.replace(tzinfo=None) < now:
                        return None, "Due date must be in the future"
                except ValueError:
                    return None, "Invalid date format"

            # Create task instance
            task = Task(
                userId=user_id,
                title=title,
                description=description,
                priority=priority,
                tags=tags or [],
                dueDate=due_date
            )

            # Save to State Store
            success = await state_client.set(f"task:{task.id}", task.dict())

            if not success:
                return None, "Failed to save task to state store"

            # Add task ID to user's index
            await TaskStateService._add_to_user_index(user_id, task.id)

            # Publish todo-created event
            await TodoCreatedPublisher.publish(
                todo_id=task.id,
                user_id=user_id,
                title=title,
                description=description,
                priority=priority,
                tags=tags,
                due_date=due_date
            )

            # Schedule reminder if due date is set
            if due_date:
                due_dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                await jobs_client.schedule_reminder(
                    todo_id=task.id,
                    user_id=user_id,
                    title=title,
                    due_date=due_dt.replace(tzinfo=None)
                )

            logger.info(f"✅ Created task {task.id} for user {user_id}")
            return task, None

        except Exception as e:
            logger.error(f"❌ Failed to create task: {e}")
            return None, str(e)

    @staticmethod
    async def get_task(task_id: str) -> Optional[Task]:
        """
        Get a task by ID (T036)

        Args:
            task_id: Task ID

        Returns:
            Task if found, None otherwise
        """
        try:
            task_data, etag = await state_client.get(f"task:{task_id}")

            if not task_data:
                return None

            task_data["etag"] = etag
            return Task(**task_data)

        except Exception as e:
            logger.error(f"❌ Failed to get task {task_id}: {e}")
            return None

    @staticmethod
    async def _add_to_user_index(user_id: str, task_id: str) -> bool:
        """
        Add task ID to user's index

        Args:
            user_id: User ID
            task_id: Task ID to add

        Returns:
            True if successful
        """
        try:
            index_key = f"user:{user_id}:tasks"
            task_ids, etag = await state_client.get(index_key)

            if not task_ids:
                task_ids = []

            # Add task ID if not already present
            if task_id not in task_ids:
                task_ids.append(task_id)
                await state_client.set(index_key, task_ids, etag=etag)

            return True

        except Exception as e:
            logger.error(f"❌ Failed to add task {task_id} to user index: {e}")
            return False

    @staticmethod
    async def _remove_from_user_index(user_id: str, task_id: str) -> bool:
        """
        Remove task ID from user's index

        Args:
            user_id: User ID
            task_id: Task ID to remove

        Returns:
            True if successful
        """
        try:
            index_key = f"user:{user_id}:tasks"
            task_ids, etag = await state_client.get(index_key)

            if not task_ids:
                return True

            # Remove task ID if present
            if task_id in task_ids:
                task_ids.remove(task_id)
                await state_client.set(index_key, task_ids, etag=etag)

            return True

        except Exception as e:
            logger.error(f"❌ Failed to remove task {task_id} from user index: {e}")
            return False

    @staticmethod
    async def list_tasks(user_id: str, limit: int = 100) -> List[Task]:
        """
        List all tasks for a user (T037)

        Uses user index to efficiently retrieve all tasks for a user.

        Args:
            user_id: User ID
            limit: Maximum number of tasks to return

        Returns:
            List of tasks
        """
        try:
            # Get user's task IDs from index
            index_key = f"user:{user_id}:tasks"
            task_ids, _ = await state_client.get(index_key)

            if not task_ids:
                logger.info(f"No tasks found for user {user_id}")
                return []

            # Bulk fetch tasks (respecting limit)
            tasks = []
            for task_id in task_ids[:limit]:
                task_data, _ = await state_client.get(f"task:{task_id}")
                if task_data:
                    try:
                        task = Task(**task_data)
                        tasks.append(task)
                    except Exception as e:
                        logger.warning(f"⚠️  Failed to parse task {task_id}: {e}")
                        continue

            logger.info(f"✅ Retrieved {len(tasks)} tasks for user {user_id}")
            return tasks

        except Exception as e:
            logger.error(f"❌ Failed to list tasks for user {user_id}: {e}")
            return []

    @staticmethod
    async def update_task(
        task_id: str,
        user_id: str,
        update_data: TaskUpdate
    ) -> Tuple[Optional[Task], Optional[str]]:
        """
        Update a task (T034)

        Args:
            task_id: Task ID
            user_id: User ID (for authorization)
            update_data: Fields to update

        Returns:
            Tuple of (updated Task, error_message)
        """
        try:
            # Get existing task with ETag
            task_data, etag = await state_client.get(f"task:{task_id}")

            if not task_data:
                return None, "Task not found"

            # Check user ownership
            if task_data.get("userId") != user_id:
                return None, "Unauthorized: Task belongs to another user"

            # Track changed fields
            changed_fields = []
            update_dict = update_data.dict(exclude_unset=True)

            for field, value in update_dict.items():
                if field in task_data and task_data[field] != value:
                    changed_fields.append(field)
                    task_data[field] = value

            # Update timestamp
            task_data["updatedAt"] = datetime.utcnow().isoformat() + "Z"
            changed_fields.append("updatedAt")

            # Create updated task
            updated_task = Task(**task_data)

            # Save with ETag for concurrency control
            try:
                await state_client.set(f"task:{task_id}", updated_task.dict(), etag=etag)
            except ValueError as e:
                if "Concurrent update" in str(e):
                    return None, "Concurrent update detected. Please retry."
                raise

            # Publish todo-updated event
            await TodoUpdatedPublisher.publish(
                todo_id=task_id,
                user_id=user_id,
                changed_fields=changed_fields,
                current_state=updated_task.dict()
            )

            # Reschedule reminder if dueDate changed
            if "dueDate" in changed_fields and updated_task.dueDate:
                await jobs_client.cancel_reminder(todo_id=task_id)
                due_dt = datetime.fromisoformat(updated_task.dueDate.replace("Z", "+00:00"))
                await jobs_client.schedule_reminder(
                    todo_id=task_id,
                    user_id=user_id,
                    title=updated_task.title,
                    due_date=due_dt.replace(tzinfo=None)
                )

            logger.info(f"✅ Updated task {task_id}, changed fields: {changed_fields}")
            return updated_task, None

        except Exception as e:
            logger.error(f"❌ Failed to update task {task_id}: {e}")
            return None, str(e)

    @staticmethod
    async def delete_task(
        task_id: str,
        user_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Delete a task (T035)

        Args:
            task_id: Task ID
            user_id: User ID (for authorization)

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Get existing task
            task_data, etag = await state_client.get(f"task:{task_id}")

            if not task_data:
                return False, "Task not found"

            # Check user ownership
            if task_data.get("userId") != user_id:
                return False, "Unauthorized: Task belongs to another user"

            # Cancel reminder if exists
            await jobs_client.cancel_reminder(todo_id=task_id)

            # Remove from user's index
            await TaskStateService._remove_from_user_index(user_id, task_id)

            # Delete from State Store
            await state_client.delete(f"task:{task_id}", etag=etag)

            # Publish todo-deleted event
            await TodoDeletedPublisher.publish(
                todo_id=task_id,
                user_id=user_id,
                was_completed=task_data.get("isCompleted", False),
                had_due_date=task_data.get("dueDate") is not None
            )

            logger.info(f"✅ Deleted task {task_id}")
            return True, None

        except Exception as e:
            logger.error(f"❌ Failed to delete task {task_id}: {e}")
            return False, str(e)

    @staticmethod
    async def mark_complete(
        task_id: str,
        user_id: str,
        completed: Optional[bool] = None
    ) -> Tuple[Optional[Task], Optional[str]]:
        """
        Mark task as complete or toggle completion (T038)

        Args:
            task_id: Task ID
            user_id: User ID (for authorization)
            completed: If provided, set to this value. If None, toggle current value.

        Returns:
            Tuple of (updated Task, error_message)
        """
        try:
            # Get existing task with ETag
            task_data, etag = await state_client.get(f"task:{task_id}")

            if not task_data:
                return None, "Task not found"

            # Check user ownership
            if task_data.get("userId") != user_id:
                return None, "Unauthorized: Task belongs to another user"

            # Toggle or set completion status
            if completed is None:
                task_data["isCompleted"] = not task_data.get("isCompleted", False)
            else:
                task_data["isCompleted"] = completed

            # Set completedAt timestamp if marking as complete
            if task_data["isCompleted"]:
                task_data["completedAt"] = datetime.utcnow().isoformat() + "Z"
            else:
                task_data["completedAt"] = None

            # Update timestamp
            task_data["updatedAt"] = datetime.utcnow().isoformat() + "Z"

            # Create updated task
            updated_task = Task(**task_data)

            # Save with ETag
            await state_client.set(f"task:{task_id}", updated_task.dict(), etag=etag)

            # Publish todo-updated event
            await TodoUpdatedPublisher.publish(
                todo_id=task_id,
                user_id=user_id,
                changed_fields=["isCompleted", "completedAt", "updatedAt"],
                current_state=updated_task.dict()
            )

            # Cancel reminder if task is completed
            if updated_task.isCompleted:
                await jobs_client.cancel_reminder(todo_id=task_id)

            logger.info(f"✅ Marked task {task_id} as {'completed' if updated_task.isCompleted else 'incomplete'}")
            return updated_task, None

        except Exception as e:
            logger.error(f"❌ Failed to mark task {task_id} complete: {e}")
            return None, str(e)


# Convenience export
__all__ = ['TaskStateService']

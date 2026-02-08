"""
Event Publishers
Publish events to Kafka via Dapr Pub/Sub with proper formatting and validation
"""
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

# Phase 5: Event publishing (optional)
try:
    from src.dapr.pubsub import pubsub_client
    EVENTS_ENABLED = True
except ImportError:
    EVENTS_ENABLED = False
    pubsub_client = None

logger = logging.getLogger(__name__)

class EventPublisher:
    """Base class for event publishers"""

    @staticmethod
    def _get_current_timestamp() -> str:
        """Get current timestamp in ISO format"""
        return datetime.utcnow().isoformat() + "Z"


class TodoCreatedPublisher(EventPublisher):
    """Publisher for todo-created events"""

    @staticmethod
    async def publish(
        todo_id: str,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        tags: Optional[List[str]] = None,
        due_date: Optional[str] = None
    ) -> bool:
        """
        Publish todo-created event

        Args:
            todo_id: ID of the created todo
            user_id: ID of the user who created the todo
            title: Todo title
            description: Todo description
            priority: Todo priority (low/medium/high/urgent)
            tags: List of tags
            due_date: Due date in ISO format

        Returns:
            True if event published successfully
        """
        if not EVENTS_ENABLED or not pubsub_client:
            logger.debug("Events not enabled, skipping todo-created publication")
            return False

        try:
            event_id = str(uuid.uuid4())
            timestamp = TodoCreatedPublisher._get_current_timestamp()

            payload = {
                "title": title,
                "description": description,
                "priority": priority,
                "tags": tags or [],
                "dueDate": due_date,
                "completed": False,
                "createdAt": timestamp,
                "updatedAt": timestamp
            }

            return await pubsub_client.publish_todo_created(
                event_id=event_id,
                todo_id=todo_id,
                user_id=user_id,
                payload=payload
            )

        except Exception as e:
            logger.error(f"❌ Failed to publish todo-created event: {e}")
            return False


class TodoUpdatedPublisher(EventPublisher):
    """Publisher for todo-updated events"""

    @staticmethod
    async def publish(
        todo_id: str,
        user_id: str,
        changed_fields: List[str],
        current_state: Dict[str, Any]
    ) -> bool:
        """
        Publish todo-updated event

        Args:
            todo_id: ID of the updated todo
            user_id: ID of the user who updated the todo
            changed_fields: List of fields that changed
            current_state: Complete current state of the todo

        Returns:
            True if event published successfully
        """
        if not EVENTS_ENABLED or not pubsub_client:
            logger.debug("Events not enabled, skipping todo-updated publication")
            return False

        try:
            event_id = str(uuid.uuid4())
            timestamp = TodoUpdatedPublisher._get_current_timestamp()

            return await pubsub_client.publish_todo_updated(
                event_id=event_id,
                todo_id=todo_id,
                user_id=user_id,
                payload=current_state,
                changed_fields=changed_fields
            )

        except Exception as e:
            logger.error(f"❌ Failed to publish todo-updated event: {e}")
            return False


class TodoDeletedPublisher(EventPublisher):
    """Publisher for todo-deleted events"""

    @staticmethod
    async def publish(
        todo_id: str,
        user_id: str,
        was_completed: bool = False,
        had_due_date: bool = False
    ) -> bool:
        """
        Publish todo-deleted event

        Args:
            todo_id: ID of the deleted todo
            user_id: ID of the user who deleted the todo
            was_completed: Whether the todo was marked as completed
            had_due_date: Whether the todo had a due date

        Returns:
            True if event published successfully
        """
        if not EVENTS_ENABLED or not pubsub_client:
            logger.debug("Events not enabled, skipping todo-deleted publication")
            return False

        try:
            event_id = str(uuid.uuid4())
            timestamp = TodoDeletedPublisher._get_current_timestamp()

            return await pubsub_client.publish_todo_deleted(
                event_id=event_id,
                todo_id=todo_id,
                user_id=user_id,
                was_completed=was_completed,
                had_due_date=had_due_date
            )

        except Exception as e:
            logger.error(f"❌ Failed to publish todo-deleted event: {e}")
            return False


class TodoReminderPublisher(EventPublisher):
    """Publisher for todo-reminder events"""

    @staticmethod
    async def publish(
        todo_id: str,
        user_id: str,
        title: str,
        due_date: Optional[str] = None,
        minutes_before: int = 1440
    ) -> bool:
        """
        Publish todo-reminder event

        Args:
            todo_id: ID of the todo
            user_id: ID of the user who owns the todo
            title: Todo title (for reminder notification)
            due_date: Due date in ISO format
            minutes_before: How many minutes before due date

        Returns:
            True if event published successfully
        """
        if not EVENTS_ENABLED or not pubsub_client:
            logger.debug("Events not enabled, skipping todo-reminder publication")
            return False, "Events not enabled"

        try:
            event_id = str(uuid.uuid4())
            timestamp = TodoReminderPublisher._get_current_timestamp()

            # Note: pubsub_client.publish_todo_reminder doesn't support minutes_before parameter
            # It's included in the event schema but not used during publish
            success = await pubsub_client.publish_todo_reminder(
                event_id=event_id,
                todo_id=todo_id,
                user_id=user_id,
                title=title,
                due_date=due_date
            )

            return (success, None) if success else (False, "Failed to publish")

        except Exception as e:
            logger.error(f"❌ Failed to publish todo-reminder event: {e}")
            return False, str(e)


# Convenience exports
__all__ = [
    'TodoCreatedPublisher',
    'TodoUpdatedPublisher',
    'TodoDeletedPublisher',
    'TodoReminderPublisher'
]

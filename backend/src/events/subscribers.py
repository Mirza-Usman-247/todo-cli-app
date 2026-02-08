"""
Event Subscribers
Handle events received from Kafka via Dapr Pub/Sub
"""
import json
from typing import Dict, Any, Optional
import logging

# Phase 5: Event handling (optional)
try:
    from src.dapr.state import state_client
    from src.dapr.jobs import jobs_client
    STATE_ENABLED = True
    JOBS_ENABLED = True
except ImportError:
    STATE_ENABLED = False
    JOBS_ENABLED = False
    state_client = None
    jobs_client = None

try:
    from src.events.schemas import get_schema
    from src.models.task import Task
    from src.events.publishers import TodoReminderPublisher
    SCHEMAS_ENABLED = True
except ImportError:
    SCHEMAS_ENABLED = False
    get_schema = None
    Task = None
    TodoReminderPublisher = None

logger = logging.getLogger(__name__)

class EventSubscriber:
    """Base class for event subscribers"""

    @staticmethod
    def _parse_event_data(event_data: bytes) -> Optional[Dict[str, Any]]:
        """Parse event data from bytes to dict"""
        try:
            if isinstance(event_data, bytes):
                event_str = event_data.decode('utf-8')
                return json.loads(event_str)
            elif isinstance(event_data, str):
                return json.loads(event_data)
            elif isinstance(event_data, dict):
                return event_data
            else:
                logger.error(f"Unknown event data type: {type(event_data)}")
                return None
        except Exception as e:
            logger.error(f"Failed to parse event data: {e}")
            return None


class TodoCreatedSubscriber(EventSubscriber):
    """Handler for todo-created events - persists to State Store"""

    @staticmethod
    async def handle(event_data: bytes) -> bool:
        """
        Handle todo-created event by creating task in State Store

        Args:
            event_data: Raw event data from Kafka

        Returns:
            True if handled successfully
        """
        if not STATE_ENABLED or not state_client:
            logger.debug("State not enabled, skipping todo-created handling")
            return False

        if not SCHEMAS_ENABLED or not Task:
            logger.debug("Models not available, skipping todo-created handling")
            return False

        try:
            data = EventSubscriber._parse_event_data(event_data)
            if not data:
                return False

            # Extract event metadata
            event_id = data.get("eventId")
            todo_id = data.get("todoId")
            user_id = data.get("userId")
            payload = data.get("payload", {})

            if not all([event_id, todo_id, user_id]):
                logger.error("Missing required fields in todo-created event")
                return False

            # Check for duplicate event (idempotency)
            existing, existing_etag = await state_client.get(f"task:{todo_id}")
            if existing:
                logger.info(f"⚠️  Duplicate todo-created event ignored: {event_id}")
                return True

            # Create Task from payload
            task_data = {
                "id": todo_id,
                "userId": user_id,
                "title": payload.get("title", "Untitled"),
                "description": payload.get("description"),
                "isCompleted": payload.get("completed", False),
                "priority": payload.get("priority", "medium"),
                "tags": payload.get("tags", []),
                "dueDate": payload.get("dueDate"),
                "createdAt": payload.get("createdAt"),
                "updatedAt": payload.get("updatedAt"),
                "completedAt": None,
                "etag": None
            }

            task = Task(**task_data)

            # Save to State Store
            success = await state_client.set(f"task:{todo_id}", task.dict())

            if success:
                logger.info(f"✅ Created task {todo_id} in State Store from event {event_id}")

                # Schedule reminder if dueDate is set
                if task.dueDate and jobs_client:
                    await jobs_client.schedule_reminder(
                        todo_id=todo_id,
                        user_id=user_id,
                        title=task.title,
                        due_date=task.dueDate
                    )

            return success

        except Exception as e:
            logger.error(f"❌ Failed to handle todo-created event: {e}")
            return False


class TodoUpdatedSubscriber(EventSubscriber):
    """Handler for todo-updated events - updates task in State Store"""

    @staticmethod
    async def handle(event_data: bytes) -> bool:
        """
        Handle todo-updated event by updating task in State Store

        Args:
            event_data: Raw event data from Kafka

        Returns:
            True if handled successfully
        """
        if not STATE_ENABLED or not state_client:
            logger.debug("State not enabled, skipping todo-updated handling")
            return False

        if not SCHEMAS_ENABLED or not Task:
            logger.debug("Models not available, skipping todo-updated handling")
            return False

        try:
            data = EventSubscriber._parse_event_data(event_data)
            if not data:
                return False

            # Extract event metadata
            event_id = data.get("eventId")
            todo_id = data.get("todoId")
            user_id = data.get("userId")
            payload = data.get("payload", {})
            changed_fields = data.get("changedFields", [])

            if not all([event_id, todo_id, user_id]):
                logger.error("Missing required fields in todo-updated event")
                return False

            # Get current task from State Store with ETag
            existing_task_data, etag = await state_client.get(f"task:{todo_id}")
            if not existing_task_data:
                logger.warning(f"⚠️  Task {todo_id} not found in State Store")
                return False

            # Check if this is a duplicate (idempotency)
            # Simple check: if updatedAt hasn't changed, it's a duplicate
            current_updated_at = existing_task_data.get("updatedAt")
            new_updated_at = payload.get("updatedAt")

            if current_updated_at == new_updated_at:
                logger.info(f"⚠️  Duplicate todo-updated event ignored: {event_id}")
                return True

            # Update only changed fields (optimistic)
            for field in changed_fields:
                if field in payload:
                    existing_task_data[field] = payload[field]

            # Always update updatedAt
            existing_task_data["updatedAt"] = payload.get("updatedAt", existing_task_data.get("updatedAt"))

            # Create updated Task
            task = Task(**existing_task_data)

            # Save to State Store with ETag for concurrency control
            success = await state_client.set(f"task:{todo_id}", task.dict(), etag=etag)

            if success:
                logger.info(f"✅ Updated task {todo_id} in State Store from event {event_id}")

                # Reschedule reminder if dueDate changed
                if "dueDate" in changed_fields and jobs_client:
                    await jobs_client.cancel_reminder(todo_id=todo_id)
                    await jobs_client.schedule_reminder(
                        todo_id=todo_id,
                        user_id=user_id,
                        title=task.title,
                        due_date=task.dueDate
                    )

            return success

        except Exception as e:
            logger.error(f"❌ Failed to handle todo-updated event: {e}")
            return False


class TodoDeletedSubscriber(EventSubscriber):
    """Handler for todo-deleted events - removes task from State Store"""

    @staticmethod
    async def handle(event_data: bytes) -> bool:
        """
        Handle todo-deleted event by deleting task from State Store

        Args:
            event_data: Raw event data from Kafka

        Returns:
            True if handled successfully
        """
        if not STATE_ENABLED or not state_client:
            logger.debug("State not enabled, skipping todo-deleted handling")
            return False

        try:
            data = EventSubscriber._parse_event_data(event_data)
            if not data:
                return False

            # Extract event metadata
            event_id = data.get("eventId")
            todo_id = data.get("todoId")
            user_id = data.get("userId")

            if not all([event_id, todo_id, user_id]):
                logger.error("Missing required fields in todo-deleted event")
                return False

            # Cancel reminder job if exists
            if jobs_client:
                await jobs_client.cancel_reminder(todo_id=todo_id)

            # Delete from State Store
            success = await state_client.delete(f"task:{todo_id}")

            if success:
                logger.info(f"✅ Deleted task {todo_id} from State Store from event {event_id}")

            return success

        except Exception as e:
            logger.error(f"❌ Failed to handle todo-deleted event: {e}")
            return False


class TodoReminderSubscriber(EventSubscriber):
    """Handler for todo-reminder events - sends notification"""

    @staticmethod
    async def handle(event_data: bytes) -> bool:
        """
        Handle todo-reminder event by sending notification

        Args:
            event_data: Raw event data from Kafka

        Returns:
            True if handled successfully
        """
        if not SCHEMAS_ENABLED:
            logger.debug("Schemas not available, skipping todo-reminder handling")
            return False

        try:
            data = EventSubscriber._parse_event_data(event_data)
            if not data:
                return False

            # Extract event metadata
            event_id = data.get("eventId")
            todo_id = data.get("todoId")
            user_id = data.get("userId")
            title = data.get("title")
            due_date = data.get("dueDate")
            minutes_before = data.get("minutesBefore", 1440)

            if not all([event_id, todo_id, user_id, title]):
                logger.error("Missing required fields in todo-reminder event")
                return False

            # TODO: Integrate with notification service
            # For now, just log the reminder
            logger.info(
                f"📧 REMINDER: Task '{title}' (ID: {todo_id}) is due in {minutes_before} minutes! "
                f"Event: {event_id}"
            )

            # In a real implementation, this would:
            # 1. Get user's notification preferences from State Store
            # 2. Send email/SMS/push notification
            # 3. Log notification delivery

            return True

        except Exception as e:
            logger.error(f"❌ Failed to handle todo-reminder event: {e}")
            return False


# Map event types to handlers
EVENT_HANDLERS = {
    "todo-created": TodoCreatedSubscriber.handle,
    "todo-updated": TodoUpdatedSubscriber.handle,
    "todo-deleted": TodoDeletedSubscriber.handle,
    "todo-reminder": TodoReminderSubscriber.handle,
}


async def handle_event(event_type: str, event_data: bytes) -> bool:
    """
    Generic event dispatcher

    Args:
        event_type: Type of event (todo-created, todo-updated, etc.)
        event_data: Raw event data from Kafka

    Returns:
        True if event handled successfully
    """
    handler = EVENT_HANDLERS.get(event_type)
    if not handler:
        logger.error(f"No handler found for event type: {event_type}")
        return False

    return await handler(event_data)

"""
Dapr Pub/Sub Client Wrapper
Publishes events to Kafka via Dapr Pub/Sub component
"""
from dapr.clients import DaprClient
from typing import Dict, Any
import logging
import uuid

logger = logging.getLogger(__name__)

PUBSUB_NAME = "pubsub-kafka"


class DaprPubSubClient:
    """Wrapper for Dapr Pub/Sub operations"""

    def __init__(self):
        self.pubsub_name = PUBSUB_NAME

    async def publish_event(
        self,
        topic: str,
        event_data: Dict[str, Any],
        partition_key: str = None
    ) -> bool:
        """
        Publish event to Kafka via Dapr

        Args:
            topic: Kafka topic name (e.g., 'todo-created')
            event_data: Event payload dictionary
            partition_key: Partition key (typically todoId for ordering)

        Returns:
            True if published successfully
        """
        try:
            with DaprClient() as client:
                # Add metadata for partition key
                metadata = {}
                if partition_key:
                    metadata["cloudevents.subject"] = partition_key

                # Publish to Kafka via Dapr
                client.publish_event(
                    pubsub_name=self.pubsub_name,
                    topic_name=topic,
                    data=event_data,
                    metadata=metadata
                )

                logger.info(
                    f"✅ Published event to topic '{topic}' "
                    f"[eventId={event_data.get('eventId')}]"
                )
                return True

        except Exception as e:
            logger.error(f"❌ Failed to publish event to topic '{topic}': {e}")
            raise

    async def publish_todo_created(
        self,
        event_id: str,
        todo_id: str,
        user_id: str,
        payload: Dict[str, Any]
    ) -> bool:
        """Publish todo-created event"""
        event_data = {
            "eventId": event_id,
            "eventType": "todo-created",
            "timestamp": payload.get("createdAt"),
            "todoId": todo_id,
            "userId": user_id,
            "schemaVersion": "1.0",
            "payload": payload
        }
        return await self.publish_event("todo-created", event_data, partition_key=todo_id)

    async def publish_todo_updated(
        self,
        event_id: str,
        todo_id: str,
        user_id: str,
        payload: Dict[str, Any],
        changed_fields: list = None
    ) -> bool:
        """Publish todo-updated event"""
        event_data = {
            "eventId": event_id,
            "eventType": "todo-updated",
            "timestamp": payload.get("updatedAt"),
            "todoId": todo_id,
            "userId": user_id,
            "schemaVersion": "1.0",
            "payload": payload,
            "changedFields": changed_fields or []
        }
        return await self.publish_event("todo-updated", event_data, partition_key=todo_id)

    async def publish_todo_deleted(
        self,
        event_id: str,
        todo_id: str,
        user_id: str,
        was_completed: bool = False,
        had_due_date: bool = False
    ) -> bool:
        """Publish todo-deleted event"""
        import datetime
        event_data = {
            "eventId": event_id,
            "eventType": "todo-deleted",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "todoId": todo_id,
            "userId": user_id,
            "schemaVersion": "1.0",
            "payload": {
                "wasCompleted": was_completed,
                "hadDueDate": had_due_date
            }
        }
        return await self.publish_event("todo-deleted", event_data, partition_key=todo_id)

    async def publish_todo_reminder(
        self,
        event_id: str,
        todo_id: str,
        user_id: str,
        title: str,
        due_date: str
    ) -> bool:
        """Publish todo-reminder event"""
        import datetime
        event_data = {
            "eventId": event_id,
            "eventType": "todo-reminder",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "todoId": todo_id,
            "userId": user_id,
            "schemaVersion": "1.0",
            "payload": {
                "title": title,
                "dueDate": due_date
            }
        }
        return await self.publish_event("todo-reminder", event_data, partition_key=todo_id)


# Singleton instance
pubsub_client = DaprPubSubClient()

"""
Event Domain Model - Phase 5 Event-Driven Architecture
Represents domain events for the todo application
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid


class Event(BaseModel):
    """Base domain event model"""
    eventId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    eventType: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    todoId: str
    userId: str
    schemaVersion: str = "1.0"
    payload: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "eventId": "123e4567-e89b-12d3-a456-426614174000",
                "eventType": "todo-created",
                "timestamp": "2026-01-29T00:00:00Z",
                "todoId": "task-123",
                "userId": "user-456",
                "schemaVersion": "1.0",
                "payload": {}
            }
        }


class TodoCreatedEvent(Event):
    """Event emitted when a todo is created"""
    eventType: str = Field(default="todo-created", frozen=True)

    class Config:
        json_schema_extra = {
            "example": {
                "eventId": "123e4567-e89b-12d3-a456-426614174000",
                "eventType": "todo-created",
                "timestamp": "2026-01-29T00:00:00Z",
                "todoId": "task-123",
                "userId": "user-456",
                "schemaVersion": "1.0",
                "payload": {
                    "title": "Complete project",
                    "description": "Finish the documentation",
                    "priority": "high",
                    "tags": ["urgent"],
                    "dueDate": "2026-12-31T23:59:59Z",
                    "completed": False,
                    "createdAt": "2026-01-29T00:00:00Z",
                    "updatedAt": "2026-01-29T00:00:00Z"
                }
            }
        }


class TodoUpdatedEvent(Event):
    """Event emitted when a todo is updated"""
    eventType: str = Field(default="todo-updated", frozen=True)
    changedFields: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "eventId": "123e4567-e89b-12d3-a456-426614174000",
                "eventType": "todo-updated",
                "timestamp": "2026-01-29T00:00:00Z",
                "todoId": "task-123",
                "userId": "user-456",
                "schemaVersion": "1.0",
                "changedFields": ["title", "priority"],
                "payload": {
                    "title": "Updated title",
                    "description": "Finish the documentation",
                    "priority": "urgent",
                    "tags": ["urgent"],
                    "dueDate": "2026-12-31T23:59:59Z",
                    "completed": False,
                    "createdAt": "2026-01-29T00:00:00Z",
                    "updatedAt": "2026-01-29T01:00:00Z"
                }
            }
        }


class TodoDeletedEvent(Event):
    """Event emitted when a todo is deleted"""
    eventType: str = Field(default="todo-deleted", frozen=True)

    class Config:
        json_schema_extra = {
            "example": {
                "eventId": "123e4567-e89b-12d3-a456-426614174000",
                "eventType": "todo-deleted",
                "timestamp": "2026-01-29T00:00:00Z",
                "todoId": "task-123",
                "userId": "user-456",
                "schemaVersion": "1.0",
                "payload": {
                    "wasCompleted": True,
                    "hadDueDate": True,
                    "wasRecurring": False
                }
            }
        }


class TodoReminderEvent(Event):
    """Event emitted when a todo reminder is triggered"""
    eventType: str = Field(default="todo-reminder", frozen=True)

    class Config:
        json_schema_extra = {
            "example": {
                "eventId": "123e4567-e89b-12d3-a456-426614174000",
                "eventType": "todo-reminder",
                "timestamp": "2026-01-29T00:00:00Z",
                "todoId": "task-123",
                "userId": "user-456",
                "schemaVersion": "1.0",
                "payload": {
                    "title": "Complete project",
                    "dueDate": "2026-12-31T23:59:59Z",
                    "minutesBefore": 1440
                }
            }
        }


# Convenience exports
__all__ = [
    'Event',
    'TodoCreatedEvent',
    'TodoUpdatedEvent',
    'TodoDeletedEvent',
    'TodoReminderEvent'
]

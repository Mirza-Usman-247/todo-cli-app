"""
Event Schemas and Validation
JSON Schema definitions for all event types with validation
"""
import json
from typing import Dict, Any

# JSON Schema for todo-created event
TODO_CREATED_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "TodoCreatedEvent",
    "type": "object",
    "required": ["eventId", "eventType", "timestamp", "todoId", "userId", "payload"],
    "properties": {
        "eventId": {
            "type": "string",
            "description": "Unique identifier for this event"
        },
        "eventType": {
            "type": "string",
            "enum": ["todo-created"],
            "description": "Type of event"
        },
        "schemaVersion": {
            "type": "string",
            "enum": ["1.0"],
            "description": "Event schema version"
        },
        "timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "When the event was generated (ISO 8601)"
        },
        "todoId": {
            "type": "string",
            "description": "ID of the todo item"
        },
        "userId": {
            "type": "string",
            "description": "ID of the user who owns the todo"
        },
        "payload": {
            "type": "object",
            "required": ["title"],
            "properties": {
                "title": {"type": "string", "maxLength": 200},
                "description": {"type": "string", "maxLength": 1000},
                "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                "tags": {
                    "type": "array",
                    "items": {"type": "string", "maxLength": 50},
                    "maxItems": 10
                },
                "dueDate": {"type": "string", "format": "date-time"},
                "completed": {"type": "boolean"},
                "createdAt": {"type": "string", "format": "date-time"},
                "updatedAt": {"type": "string", "format": "date-time"}
            }
        }
    }
}

# JSON Schema for todo-updated event
TODO_UPDATED_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "TodoUpdatedEvent",
    "type": "object",
    "required": ["eventId", "eventType", "timestamp", "todoId", "userId", "changedFields", "payload"],
    "properties": {
        "eventId": {"type": "string"},
        "eventType": {"type": "string", "enum": ["todo-updated"]},
        "schemaVersion": {"type": "string", "enum": ["1.0"]},
        "timestamp": {"type": "string", "format": "date-time"},
        "todoId": {"type": "string"},
        "userId": {"type": "string"},
        "changedFields": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 20,
            "description": "List of fields that changed in this update"
        },
        "payload": {
            "type": "object",
            "description": "Complete task state after update"
        }
    }
}

# JSON Schema for todo-deleted event
TODO_DELETED_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "TodoDeletedEvent",
    "type": "object",
    "required": ["eventId", "eventType", "timestamp", "todoId", "userId"],
    "properties": {
        "eventId": {"type": "string"},
        "eventType": {"type": "string", "enum": ["todo-deleted"]},
        "schemaVersion": {"type": "string", "enum": ["1.0"]},
        "timestamp": {"type": "string", "format": "date-time"},
        "todoId": {"type": "string"},
        "userId": {"type": "string"},
        "wasCompleted": {"type": "boolean", "default": False},
        "hadDueDate": {"type": "boolean", "default": False}
    }
}

# JSON Schema for todo-reminder event
TODO_REMINDER_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "TodoReminderEvent",
    "type": "object",
    "required": ["eventId", "eventType", "timestamp", "todoId", "userId", "title"],
    "properties": {
        "eventId": {"type": "string"},
        "eventType": {"type": "string", "enum": ["todo-reminder"]},
        "schemaVersion": {"type": "string", "enum": ["1.0"]},
        "timestamp": {"type": "string", "format": "date-time"},
        "todoId": {"type": "string"},
        "userId": {"type": "string"},
        "title": {"type": "string", "maxLength": 200},
        "dueDate": {"type": "string", "format": "date-time"},
        "minutesBefore": {
            "type": "integer",
            "minimum": 1,
            "maximum": 10080,
            "description": "Minutes before dueDate when reminder was sent (1 week max)"
        }
    }
}

def get_schema(event_type: str) -> dict:
    """Get JSON Schema for an event type"""
    schemas = {
        "todo-created": TODO_CREATED_SCHEMA,
        "todo-updated": TODO_UPDATED_SCHEMA,
        "todo-deleted": TODO_DELETED_SCHEMA,
        "todo-reminder": TODO_REMINDER_SCHEMA,
    }
    return schemas.get(event_type, {})

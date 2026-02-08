# Event-Driven Task API Endpoints Reference

## Overview

The Event-Driven Task API provides 9 REST endpoints that integrate with Kafka pub/sub and Redis state store via Dapr. Each endpoint follows event-driven architecture principles: **Command → Event → State Update**.

## Base URL

- **Local**: `http://localhost:8000`
- **Production**: `https://api.todo-app.example.com`

## Architecture Pattern

All mutation endpoints follow this pattern:

```
Client Request → API Endpoint → Publish Event to Kafka
                                       ↓
                              Dapr Subscription
                                       ↓
                              Event Handler (Idempotent)
                                       ↓
                              Update State Store (Redis)
```

---

## Endpoints

### 1. Health Check

**Endpoint**: `GET /health`

**Purpose**: Verify API service health and Dapr connectivity

**Why?**:
- Kubernetes liveness and readiness probes
- Load balancer health checks
- Monitoring and alerting
- Troubleshooting connectivity issues

**Response**:
```json
{
  "status": "healthy",
  "service": "todo-api",
  "dapr_enabled": true,
  "components": ["pubsub-kafka", "statestore-redis", "kubernetes-secrets"]
}
```

**Use Case**: Called every 10 seconds by Kubernetes to ensure pod is ready for traffic.

---

### 2. Create Task

**Endpoint**: `POST /api/v1/events/tasks`

**Purpose**: Create a new task and publish `todo-created` event

**Why Event-Driven?**:
- **Decoupling**: API doesn't directly write to database; event handlers do
- **Auditability**: Every task creation generates an immutable event in Kafka
- **Extensibility**: Other services can subscribe to `todo-created` (notifications, analytics)
- **Resilience**: If state store is down temporarily, event is queued for later processing

**Request Body**:
```json
{
  "userId": "user-123",
  "title": "Complete project documentation",
  "description": "Write comprehensive API docs",
  "priority": "high",
  "tags": ["documentation", "api"],
  "dueDate": "2026-02-15T23:59:59Z"
}
```

**Response** (201 Created):
```json
{
  "task": {
    "id": "task-abc-123",
    "userId": "user-123",
    "title": "Complete project documentation",
    "description": "Write comprehensive API docs",
    "priority": "high",
    "tags": ["documentation", "api"],
    "dueDate": "2026-02-15T23:59:59Z",
    "isCompleted": false,
    "createdAt": "2026-01-30T10:00:00Z",
    "updatedAt": "2026-01-30T10:00:00Z"
  },
  "eventId": "event-xyz-789"
}
```

**Event Published**:
```json
{
  "eventId": "event-xyz-789",
  "eventType": "todo-created",
  "timestamp": "2026-01-30T10:00:00Z",
  "todoId": "task-abc-123",
  "userId": "user-123",
  "payload": { /* full task object */ }
}
```

**Flow**:
1. API validates request
2. Generates unique `taskId` and `eventId`
3. Publishes event to `todo-created` Kafka topic
4. Returns immediately (async processing)
5. Event handler persists to Redis
6. Optional: Schedule reminder 24h before due date

**Why Not Direct Write?**:
- Direct write couples API to database schema
- No audit trail of creation
- Can't easily add features like:
  - Email notification on creation
  - Analytics tracking
  - Machine learning on task patterns
- Harder to scale (database bottleneck)

---

### 3. List Tasks

**Endpoint**: `GET /api/v1/events/tasks?user_id={userId}`

**Purpose**: Retrieve all tasks for a user from state store

**Why?**:
- Read operations don't need events (CQRS pattern)
- Direct read from Redis is fast (< 10ms)
- State store is eventually consistent with events

**Query Parameters**:
- `user_id` (required): User identifier

**Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": "task-abc-123",
      "userId": "user-123",
      "title": "Complete project documentation",
      "priority": "high",
      "isCompleted": false,
      "createdAt": "2026-01-30T10:00:00Z"
    }
  ],
  "total": 1
}
```

**Performance**:
- Redis read: ~5-10ms
- No Kafka involved (read-only)
- Scales horizontally (multiple Redis replicas)

---

### 4. Get Single Task

**Endpoint**: `GET /api/v1/events/tasks/{taskId}?user_id={userId}`

**Purpose**: Retrieve a specific task by ID

**Why?**:
- Detail view for task
- Authorization check (userId must match task owner)
- Used after mutation to get updated state

**Path Parameters**:
- `taskId` (required): Task identifier

**Query Parameters**:
- `user_id` (required): User identifier for authorization

**Response** (200 OK):
```json
{
  "task": {
    "id": "task-abc-123",
    "userId": "user-123",
    "title": "Complete project documentation",
    "description": "Write comprehensive API docs",
    "priority": "high",
    "tags": ["documentation", "api"],
    "dueDate": "2026-02-15T23:59:59Z",
    "isCompleted": false,
    "createdAt": "2026-01-30T10:00:00Z",
    "updatedAt": "2026-01-30T10:00:00Z"
  }
}
```

**Error** (404 Not Found):
```json
{
  "detail": "Task not found or not authorized"
}
```

---

### 5. Update Task

**Endpoint**: `PUT /api/v1/events/tasks/{taskId}?user_id={userId}`

**Purpose**: Update task fields and publish `todo-updated` event

**Why Event-Driven?**:
- **Change Tracking**: Event includes `previousState` for audit trail
- **Notification**: Subscribers can detect priority changes and alert user
- **History**: Kafka retains all changes for 14 days (configurable)
- **Undo Feature**: Can replay events to restore previous states

**Path Parameters**:
- `taskId` (required): Task identifier

**Query Parameters**:
- `user_id` (required): User identifier for authorization

**Request Body** (partial update):
```json
{
  "title": "Complete project documentation (UPDATED)",
  "priority": "urgent",
  "dueDate": "2026-02-10T23:59:59Z"
}
```

**Response** (200 OK):
```json
{
  "task": {
    "id": "task-abc-123",
    "title": "Complete project documentation (UPDATED)",
    "priority": "urgent",
    "dueDate": "2026-02-10T23:59:59Z",
    "updatedAt": "2026-01-30T11:00:00Z"
  },
  "eventId": "event-update-456"
}
```

**Event Published**:
```json
{
  "eventId": "event-update-456",
  "eventType": "todo-updated",
  "timestamp": "2026-01-30T11:00:00Z",
  "todoId": "task-abc-123",
  "userId": "user-123",
  "payload": { /* updated task */ },
  "previousState": {
    "priority": "high",
    "dueDate": "2026-02-15T23:59:59Z"
  }
}
```

**Use Case - Change Notification**:
```
Priority changed: high → urgent
→ Event handler detects change
→ Sends urgent priority email to user
```

---

### 6. Delete Task

**Endpoint**: `DELETE /api/v1/events/tasks/{taskId}?user_id={userId}`

**Purpose**: Soft-delete task and publish `todo-deleted` event

**Why Event-Driven?**:
- **Soft Delete**: Event is published; actual deletion happens async
- **Reversible**: Can restore from event log if deleted by mistake
- **Cleanup**: Event handler cancels scheduled reminders
- **Audit**: Deletion is logged in Kafka (compliance requirement)

**Path Parameters**:
- `taskId` (required): Task identifier

**Query Parameters**:
- `user_id` (required): User identifier for authorization

**Response** (200 OK):
```json
{
  "message": "Task deleted successfully",
  "eventId": "event-delete-789"
}
```

**Event Published**:
```json
{
  "eventId": "event-delete-789",
  "eventType": "todo-deleted",
  "timestamp": "2026-01-30T12:00:00Z",
  "todoId": "task-abc-123",
  "userId": "user-123",
  "payload": {
    "id": "task-abc-123",
    "deletedAt": "2026-01-30T12:00:00Z"
  }
}
```

**Event Handler Actions**:
1. Remove task from Redis state store
2. Cancel scheduled reminder (Dapr Jobs API)
3. Log deletion to audit system

---

### 7. Toggle Task Completion

**Endpoint**: `PATCH /api/v1/events/tasks/{taskId}/complete?user_id={userId}`

**Purpose**: Mark task as complete/incomplete and publish `todo-updated` event

**Why Separate Endpoint?**:
- **Common Operation**: Toggling completion is most frequent user action
- **Semantic Clarity**: PATCH for partial update vs PUT for full update
- **Optimized**: Can skip loading full task; only update one field

**Path Parameters**:
- `taskId` (required): Task identifier

**Query Parameters**:
- `user_id` (required): User identifier for authorization

**Request Body** (optional):
```json
{
  "isCompleted": true
}
```
*If body is omitted, toggles current state*

**Response** (200 OK):
```json
{
  "task": {
    "id": "task-abc-123",
    "isCompleted": true,
    "completedAt": "2026-01-30T13:00:00Z",
    "updatedAt": "2026-01-30T13:00:00Z"
  },
  "eventId": "event-complete-321"
}
```

**Use Case - Gamification**:
```
Task marked complete
→ Event handler increments user XP
→ Checks if user earned achievement
→ Sends congratulations notification
```

---

### 8. Search and Filter Tasks

**Endpoint**: `POST /api/v1/events/tasks/search`

**Purpose**: Search tasks by priority, tags, completion status, keyword

**Why POST Instead of GET?**:
- Complex filter criteria (too long for query string)
- JSON body is more flexible than URL encoding
- RESTful convention for complex queries

**Request Body**:
```json
{
  "userId": "user-123",
  "priority": "high",
  "tags": ["documentation"],
  "isCompleted": false,
  "keyword": "project",
  "sortBy": "dueDate",
  "sortOrder": "asc"
}
```

**Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": "task-abc-123",
      "title": "Complete project documentation",
      "priority": "high",
      "tags": ["documentation", "api"],
      "dueDate": "2026-02-15T23:59:59Z"
    }
  ],
  "total": 1,
  "filters_applied": {
    "priority": "high",
    "tags": ["documentation"],
    "keyword": "project"
  }
}
```

**Performance**:
- In-memory filtering after loading from Redis
- For large datasets (> 10,000 tasks), consider Elasticsearch
- Current implementation: O(n) where n = user's task count

---

### 9. Schedule Reminder

**Endpoint**: `POST /api/v1/events/tasks/reminders/{taskId}?user_id={userId}`

**Purpose**: Schedule a reminder using Dapr Jobs API

**Why Dapr Jobs?**:
- **Distributed**: Works across multiple pods
- **Reliable**: Persisted in etcd; survives pod restarts
- **Scalable**: Dapr handles scheduling and execution
- **Event-Driven**: Publishes `todo-reminder` event when triggered

**Path Parameters**:
- `taskId` (required): Task identifier

**Query Parameters**:
- `user_id` (required): User identifier for authorization

**Request Body** (optional):
```json
{
  "reminderTime": "2026-02-14T23:59:59Z",
  "hoursBeforeDue": 24
}
```
*If omitted, defaults to 24 hours before dueDate*

**Response** (200 OK):
```json
{
  "message": "Reminder scheduled successfully",
  "jobName": "reminder-task-abc-123",
  "reminderTime": "2026-02-14T23:59:59Z",
  "dueDate": "2026-02-15T23:59:59Z"
}
```

**Dapr Job Created**:
```json
{
  "name": "reminder-task-abc-123",
  "schedule": "2026-02-14T23:59:59Z",
  "data": {
    "todoId": "task-abc-123",
    "userId": "user-123"
  }
}
```

**When Job Triggers**:
1. Dapr calls webhook: `POST /jobs/reminder`
2. Backend publishes `todo-reminder` event
3. Event handler sends notification (email/push/SMS)

**Use Case**:
```
User sets reminder: "Remind me 1 day before deadline"
→ Job scheduled for 2026-02-14 23:59
→ At that time, Dapr triggers job
→ Backend publishes reminder event
→ Email service sends: "Task due in 24 hours!"
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data",
  "errors": [
    {
      "field": "priority",
      "message": "Must be one of: low, medium, high, urgent"
    }
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "User not authenticated"
}
```

### 404 Not Found
```json
{
  "detail": "Task not found or not authorized"
}
```

### 409 Conflict (Concurrency)
```json
{
  "detail": "Task was modified by another request. Please refresh and try again.",
  "etag_mismatch": true
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "error_id": "error-xyz-123"
}
```

---

## Event-Driven Benefits Summary

### Why Not Traditional CRUD?

**Traditional API** (direct database writes):
```
POST /tasks → Write to PostgreSQL → Return 201
```

**Problems**:
- ❌ No audit trail
- ❌ Tight coupling to database
- ❌ Hard to add features (notifications, analytics)
- ❌ Single point of failure
- ❌ No event history

**Event-Driven API** (Kafka + State Store):
```
POST /tasks → Publish Event → Return 202
              ↓
          Event Handler → Update State Store
              ↓
          Other Subscribers (notification, analytics)
```

**Benefits**:
- ✅ Complete audit trail (Kafka retention)
- ✅ Loose coupling (API ↔ Storage ↔ Consumers)
- ✅ Easy to extend (add new subscribers)
- ✅ Resilient (events queued if handler down)
- ✅ Replayable (restore state from events)
- ✅ Scalable (horizontal scaling of consumers)

---

## Testing the API

### Create a Task
```bash
curl -X POST http://localhost:8000/api/v1/events/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test-user",
    "title": "Test Event-Driven Task",
    "priority": "high",
    "tags": ["test"],
    "dueDate": "2026-12-31T23:59:59Z"
  }'
```

### List Tasks
```bash
curl http://localhost:8000/api/v1/events/tasks?user_id=test-user
```

### Update Task
```bash
TASK_ID="<task-id-from-create>"
curl -X PUT http://localhost:8000/api/v1/events/tasks/${TASK_ID}?user_id=test-user \
  -H "Content-Type: application/json" \
  -d '{
    "priority": "urgent",
    "title": "UPDATED TITLE"
  }'
```

### Mark Complete
```bash
curl -X PATCH http://localhost:8000/api/v1/events/tasks/${TASK_ID}/complete?user_id=test-user
```

### Delete Task
```bash
curl -X DELETE http://localhost:8000/api/v1/events/tasks/${TASK_ID}?user_id=test-user
```

---

## Authentication (Future)

Currently using `user_id` query parameter for simplicity. In production:

1. **JWT Tokens**:
```bash
curl -H "Authorization: Bearer <jwt-token>" \
  http://localhost:8000/api/v1/events/tasks
```

2. **Extract userId from JWT**:
```python
@app.post("/api/v1/events/tasks")
async def create_task(
    request: CreateTaskRequest,
    current_user: User = Depends(get_current_user)
):
    request.userId = current_user.id  # Override from JWT
    # ...
```

---

## Rate Limiting (Future)

Add rate limiting to prevent abuse:

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/events/tasks")
@limiter.limit("100/minute")  # Max 100 tasks per minute
async def create_task(...):
    ...
```

---

## Related Documentation

- [Event Architecture](../architecture/EVENT_ARCHITECTURE.md)
- [Dapr Components](../architecture/DAPR_COMPONENTS.md)
- [Kafka Topics](../architecture/KAFKA_TOPICS.md)
- [Local Development Guide](LOCAL_DEVELOPMENT_GUIDE.md)

# Event-Driven Architecture (T122)

This document describes the event-driven architecture of the Todo App Phase 5.

## Overview

The Todo App uses an event-driven architecture powered by Apache Kafka and Dapr to enable scalability, resilience, and loose coupling between components.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                          │
│                          + Dapr Sidecar                             │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         │ Dapr Service Invocation
                         │ (HTTP/gRPC)
                         │
┌────────────────────────▼────────────────────────────────────────────┐
│                      Backend (FastAPI)                              │
│                       + Dapr Sidecar                                │
│                                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  REST API   │  │  Event       │  │  Business    │              │
│  │  Endpoints  │─►│  Publishers  │  │  Logic       │              │
│  └─────────────┘  └──────┬───────┘  └──────────────┘              │
│                          │                                          │
└──────────────────────────┼──────────────────────────────────────────┘
                           │
                           │ Publish Events
                           │ (CloudEvents format)
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                   Dapr Pub/Sub Component                            │
│                      (pubsub-kafka)                                 │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                     Apache Kafka Cluster                            │
│                                                                     │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│   │ todo-created │  │ todo-updated │  │ todo-deleted │            │
│   │   (topic)    │  │   (topic)    │  │   (topic)    │            │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │
│          │                 │                  │                     │
│   ┌──────▼──────────────────▼──────────────────▼───────┐           │
│   │            todo-reminder (topic)                    │           │
│   └─────────────────────────┬───────────────────────────┘           │
└─────────────────────────────┼───────────────────────────────────────┘
                              │
                              │ Subscribe to Events
                              │ (Consumer Groups)
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                    Dapr Subscriptions                               │
│                                                                     │
│   ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│   │ backend-todo-    │  │ backend-todo-    │  │ backend-todo-   │ │
│   │    created       │  │    updated       │  │    deleted      │ │
│   └────────┬─────────┘  └────────┬─────────┘  └────────┬────────┘ │
│            │                     │                      │          │
│   ┌────────▼──────────────────────▼──────────────────────▼────────┐ │
│   │          backend-todo-reminder (Dapr Jobs API)               │ │
│   └──────────────────────────┬───────────────────────────────────┘ │
└──────────────────────────────┼─────────────────────────────────────┘
                               │
                               │ Event Subscribers
                               │ (Idempotent Handlers)
                               │
┌──────────────────────────────▼─────────────────────────────────────┐
│                         Backend (FastAPI)                          │
│                          + Dapr Sidecar                            │
│                                                                    │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  Event      │  │  State       │  │  Business    │             │
│  │  Handlers   │─►│  Management  │  │  Logic       │             │
│  └─────────────┘  └──────┬───────┘  └──────────────┘             │
│                          │                                         │
└──────────────────────────┼─────────────────────────────────────────┘
                           │
                           │ Read/Write State
                           │ (ETag-based concurrency)
                           │
┌──────────────────────────▼─────────────────────────────────────────┐
│                   Dapr State Store Component                       │
│                      (statestore-redis)                            │
└──────────────────────────┬─────────────────────────────────────────┘
                           │
                           │
┌──────────────────────────▼─────────────────────────────────────────┐
│                       Redis Cluster                                │
│                    (Persistent Storage)                            │
│                                                                    │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│   │ task:abc123  │  │ task:def456  │  │ task:ghi789  │           │
│   │   (state)    │  │   (state)    │  │   (state)    │           │
│   └──────────────┘  └──────────────┘  └──────────────┘           │
└────────────────────────────────────────────────────────────────────┘
```

## Event Flow

### 1. Task Creation Flow

```
User → Frontend → Dapr (Service Invocation) → Backend API
                                                     │
                                                     ▼
                                             Create Task Event
                                                     │
                                                     ▼
                            Dapr Pub/Sub → Kafka (todo-created topic)
                                                     │
                                                     ▼
                                        Dapr Subscription (backend)
                                                     │
                                                     ▼
                                              Event Handler
                                                     │
                                                     ├─► Check Idempotency
                                                     │   (eventId deduplication)
                                                     │
                                                     ├─► Persist to State Store
                                                     │   (Redis via Dapr)
                                                     │
                                                     └─► Schedule Reminder (optional)
                                                         (Dapr Jobs API)
```

### 2. Task Update Flow

```
User → Frontend → Backend API → Validate Update
                                      │
                                      ▼
                               Read Current State
                               (with ETag)
                                      │
                                      ▼
                              Apply Update
                                      │
                                      ▼
                            Publish Update Event
                            (todo-updated topic)
                                      │
                                      ▼
                             Event Handler
                                      │
                                      ├─► Check Idempotency
                                      │
                                      ├─► Update State Store
                                      │   (with ETag check)
                                      │
                                      └─► Reschedule Reminder
                                          (if dueDate changed)
```

### 3. Task Deletion Flow

```
User → Frontend → Backend API → Validate Deletion
                                      │
                                      ▼
                            Publish Delete Event
                            (todo-deleted topic)
                                      │
                                      ▼
                             Event Handler
                                      │
                                      ├─► Check Idempotency
                                      │
                                      ├─► Delete from State Store
                                      │
                                      └─► Cancel Reminder
                                          (Dapr Jobs API)
```

### 4. Reminder Flow

```
Dapr Jobs API (Scheduled) → Publish Reminder Event
                                   (todo-reminder topic)
                                         │
                                         ▼
                                   Event Handler
                                         │
                                         ├─► Retrieve Task from State
                                         │
                                         ├─► Send Notification
                                         │   (Email/Push/Webhook)
                                         │
                                         └─► Update Task Metadata
                                             (reminder sent flag)
```

## Event Types

### 1. todo-created

**Purpose**: Published when a new task is created

**Schema**:
```json
{
  "eventId": "uuid",
  "eventType": "todo-created",
  "timestamp": "2026-01-29T12:00:00Z",
  "todoId": "uuid",
  "userId": "string",
  "payload": {
    "id": "uuid",
    "userId": "string",
    "title": "string",
    "description": "string",
    "priority": "low|medium|high|urgent",
    "tags": ["string"],
    "dueDate": "ISO8601",
    "isCompleted": false,
    "createdAt": "ISO8601",
    "updatedAt": "ISO8601"
  }
}
```

### 2. todo-updated

**Purpose**: Published when a task is modified

**Schema**:
```json
{
  "eventId": "uuid",
  "eventType": "todo-updated",
  "timestamp": "2026-01-29T12:00:00Z",
  "todoId": "uuid",
  "userId": "string",
  "payload": {
    "id": "uuid",
    "userId": "string",
    "title": "string",
    "description": "string",
    "priority": "low|medium|high|urgent",
    "tags": ["string"],
    "dueDate": "ISO8601",
    "isCompleted": boolean,
    "createdAt": "ISO8601",
    "updatedAt": "ISO8601"
  },
  "previousState": {
    "priority": "previous value",
    "isCompleted": "previous value"
  }
}
```

### 3. todo-deleted

**Purpose**: Published when a task is deleted

**Schema**:
```json
{
  "eventId": "uuid",
  "eventType": "todo-deleted",
  "timestamp": "2026-01-29T12:00:00Z",
  "todoId": "uuid",
  "userId": "string",
  "payload": {
    "id": "uuid",
    "deletedAt": "ISO8601"
  }
}
```

### 4. todo-reminder

**Purpose**: Published when a task reminder is triggered

**Schema**:
```json
{
  "eventId": "uuid",
  "eventType": "todo-reminder",
  "timestamp": "2026-01-29T12:00:00Z",
  "todoId": "uuid",
  "userId": "string",
  "payload": {
    "id": "uuid",
    "title": "string",
    "dueDate": "ISO8601",
    "hoursBeforeDue": 24,
    "notificationChannel": "email|push|webhook"
  }
}
```

## Event Guarantees

### At-Least-Once Delivery

- Kafka guarantees at-least-once delivery
- Consumers may receive duplicate events
- **Mitigation**: Idempotent event handlers using `eventId`

### Event Ordering

- Events for the same `todoId` are ordered (same partition key)
- Events across different tasks may be processed out of order
- **Ordering Key**: `todoId` used as Kafka partition key

### Idempotency

All event handlers are idempotent:

```python
async def handle_event(event_data):
    event_id = event_data['eventId']

    # Check if event already processed
    if await is_event_processed(event_id):
        logger.info(f"Duplicate event {event_id} ignored")
        return True  # ACK the message

    # Process event
    result = await process_event(event_data)

    # Mark event as processed
    await mark_event_processed(event_id)

    return result
```

### Concurrency Control

State updates use ETag-based optimistic locking:

```python
# Read with ETag
task, etag = await state_client.get("task:123")

# Update with ETag check
success = await state_client.set(
    "task:123",
    updated_task,
    etag=etag  # Fails if ETag doesn't match
)
```

## Scaling Considerations

### Horizontal Scaling

- Multiple backend instances can process events in parallel
- Kafka partitions distribute load across consumers
- Dapr handles consumer group management

### Partitioning Strategy

- **Key**: `todoId`
- **Partitions**: 3 (configurable)
- **Benefit**: Events for same task processed sequentially

### Consumer Group

- **Group ID**: `backend-group-prod`
- **Instances**: Scales with backend deployment
- **Rebalancing**: Automatic via Kafka

## Failure Handling

### Event Processing Failures

1. **Transient Failures**: Retry with exponential backoff
2. **Permanent Failures**: Log error, send to dead letter queue
3. **Poison Pills**: Skip after N retries, alert ops team

### State Store Failures

- **Read Failures**: Retry with backoff
- **Write Failures**: Return 500 to client, event will be retried
- **Concurrency Conflicts**: Return 409, client retries

### Kafka Failures

- **Broker Down**: Automatic failover to replica
- **Network Issues**: Client retries with backoff
- **Topic Unavailable**: Circuit breaker pattern

## Monitoring & Observability

### Metrics

- `dapr_component_pubsub_egress_count`: Events published
- `dapr_component_pubsub_ingress_count`: Events consumed
- `event_processing_duration_seconds`: Processing latency
- `event_processing_errors_total`: Failed events

### Alerts

- High event processing latency (>500ms P95)
- Event processing failures (>1% error rate)
- Consumer lag (>1000 messages)
- Dapr sidecar health

### Tracing

- Distributed tracing via Dapr + Zipkin
- Trace ID propagated through CloudEvents
- End-to-end request tracking from API to state update

## Security

### Authentication

- Events are internal (not exposed publicly)
- Kafka uses SASL/SCRAM authentication (production)
- mTLS between Dapr sidecars

### Authorization

- Events include `userId` for authorization checks
- State Store keys include `userId` prefix
- Access control via Dapr policies

### Encryption

- **In-transit**: TLS for Kafka connections
- **At-rest**: Redis encryption (OKE production)
- **Events**: No PII in event payloads (reference by ID)

## References

- [Dapr Pub/Sub Documentation](https://docs.dapr.io/developing-applications/building-blocks/pubsub/)
- [CloudEvents Specification](https://cloudevents.io/)
- [Kafka Consumer Groups](https://kafka.apache.org/documentation/#consumergroups)
- [Event-Driven Architecture Patterns](https://www.enterpriseintegrationpatterns.com/patterns/messaging/)

---
description: "Atomic task breakdown for Event-Driven Todo Application with Kafka and Dapr"
---

# Tasks: Event-Driven Todo Application with Kafka and Dapr

**Input**: Design documents from `/specs/004-event-driven-todo/`
**Prerequisites**: plan.md (✅), spec.md (✅), research.md (✅), data-model.md (✅), contracts/ (✅), quickstart.md (✅)

**Organization**: Tasks are grouped by deployment target (Local/Cloud/Both) and user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] [Target] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US8)
- **[Target]**: Deployment target - Local (Minikube), Cloud (OKE), or Both
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/src/`
- **Dapr Components**: `dapr/components/`, `dapr/subscriptions/`
- **Kafka Infrastructure**: `kafka/topics/`, `kafka/strimzi/`
- **Helm Charts**: `helm/todo-app-event-driven/`
- **CI/CD**: `.github/workflows/`
- **Documentation**: `docs/`

---

## Phase 1: Infrastructure Setup (Local) - Kafka & Dapr Foundation

**Purpose**: Deploy core infrastructure on Minikube to enable local development and testing
**Target**: Local (Minikube)
**Category**: Kafka Infrastructure, Dapr Components

### Kafka Cluster Deployment (Local)

- [X] T001 [US6] [Local] Deploy Strimzi Kafka operator on Minikube via kubectl in namespace kafka
  - **Spec Ref**: FR-033, FR-035
  - **Verification**: `kubectl get deployment strimzi-cluster-operator -n kafka` shows Running ✅
  - **Files**: `kafka/strimzi/operator-install.yaml` (installed via URL)
  - **Completed**: 2026-01-27

- [X] T002 [US6] [Local] Create Kafka cluster CRD with KRaft mode (no Zookeeper) in kafka/strimzi/kafka-cluster.yaml
  - **Spec Ref**: FR-035
  - **Verification**: Kafka broker pod running ✅
  - **Files**: `kafka/strimzi/kafka-cluster.yaml` (KRaft mode with Kafka 4.1.1)
  - **Completed**: 2026-01-27
  - **Note**: Updated to KRaft mode as Zookeeper is deprecated in latest Strimzi

- [X] T003 [P] [US6] [Local] Create Kafka topic "todo-created" with 1 partition, 1 replica, 7-day retention
  - **Spec Ref**: FR-001, FR-035
  - **Verification**: Topic created manually via kubectl exec ✅
  - **Files**: `kafka/topics/todo-created.yaml`
  - **Completed**: 2026-01-27

- [X] T004 [P] [US6] [Local] Create Kafka topic "todo-updated" with 1 partition, 1 replica, 7-day retention
  - **Spec Ref**: FR-002, FR-035
  - **Verification**: Topic created manually via kubectl exec ✅
  - **Files**: `kafka/topics/todo-updated.yaml`
  - **Completed**: 2026-01-27

- [X] T005 [P] [US6] [Local] Create Kafka topic "todo-deleted" with 1 partition, 1 replica, 7-day retention
  - **Spec Ref**: FR-003, FR-035
  - **Verification**: Topic created manually via kubectl exec ✅
  - **Files**: `kafka/topics/todo-deleted.yaml`
  - **Completed**: 2026-01-27

- [X] T006 [P] [US6] [Local] Create Kafka topic "todo-reminder" with 1 partition, 1 replica, 7-day retention
  - **Spec Ref**: FR-004, FR-035
  - **Verification**: Topic created manually via kubectl exec ✅
  - **Files**: `kafka/topics/todo-reminder.yaml`
  - **Completed**: 2026-01-27

**Checkpoint**: Kafka cluster is deployed and all 4 topics are ready on Minikube

### Dapr Control Plane Deployment (Local)

- [X] T007 [US6] [Local] Install Dapr control plane on Minikube via `dapr init --kubernetes --wait`
  - **Spec Ref**: FR-033, FR-014
  - **Verification**: `kubectl get pods -n dapr-system` shows 8/8 Running ✅
  - **Files**: None (CLI operation)
  - **Completed**: 2026-01-27

- [X] T008 [US6] [Local] Deploy Redis State Store backend on Minikube via Helm (bitnami/redis, auth disabled, no persistence)
  - **Spec Ref**: FR-036
  - **Verification**: Redis deployed successfully ✅
  - **Files**: None (Helm chart)
  - **Completed**: 2026-01-27

**Checkpoint**: Dapr control plane and Redis are healthy on Minikube

---

## Phase 2: Dapr Component Configuration (Local)

**Purpose**: Define Dapr components for Pub/Sub, State Store, and Secrets
**Target**: Local (Minikube)
**Category**: Dapr Components

### Dapr Component Definitions

- [X] T009 [P] [US1] [Local] Create Dapr Pub/Sub component YAML for Kafka backend in dapr/components/pubsub-kafka.yaml
  - **Spec Ref**: FR-010, FR-015
  - **Verification**: `kubectl get component pubsub-kafka` shows component created ✅
  - **Config**: brokers: my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092, consumerGroup: backend-group
  - **Files**: `dapr/components/pubsub-kafka.yaml`
  - **Completed**: 2026-01-27

- [X] T010 [P] [US1] [Local] Create Dapr State Store component YAML for Redis backend in dapr/components/statestore-redis.yaml
  - **Spec Ref**: FR-011, FR-015, FR-036
  - **Verification**: `kubectl get component statestore-redis` shows component created ✅
  - **Config**: redisHost: redis-master:6379, enableTLS: false
  - **Files**: `dapr/components/statestore-redis.yaml`
  - **Completed**: 2026-01-27

- [X] T011 [P] [US1] [Local] Create Dapr Secrets component YAML for Kubernetes Secrets backend in dapr/components/secrets-kubernetes.yaml
  - **Spec Ref**: FR-012, FR-015, FR-046, FR-047
  - **Verification**: `kubectl get component kubernetes-secrets` shows component created ✅
  - **Files**: `dapr/components/secrets-kubernetes.yaml`
  - **Completed**: 2026-01-27

### Dapr Subscriptions

- [X] T012 [US1] [Local] Create Dapr Subscription for backend to subscribe to "todo-created" topic
  - **Spec Ref**: FR-010
  - **Verification**: `kubectl get subscription backend-todo-created` shows subscription created ✅
  - **Config**: pubsubname: pubsub-kafka, topic: todo-created, route: /events/todo-created
  - **Files**: `dapr/subscriptions/backend-subscriptions.yaml`
  - **Completed**: 2026-01-27

- [X] T013 [US1] [Local] Create Dapr Subscription for backend to subscribe to "todo-updated" topic
  - **Spec Ref**: FR-010
  - **Verification**: `kubectl get subscription backend-todo-updated` shows subscription created ✅
  - **Config**: pubsubname: pubsub-kafka, topic: todo-updated, route: /events/todo-updated
  - **Files**: `dapr/subscriptions/backend-subscriptions.yaml`
  - **Completed**: 2026-01-27

- [X] T014 [US1] [Local] Create Dapr Subscription for backend to subscribe to "todo-deleted" topic
  - **Spec Ref**: FR-010
  - **Verification**: `kubectl get subscription backend-todo-deleted` shows subscription created ✅
  - **Config**: pubsubname: pubsub-kafka, topic: todo-deleted, route: /events/todo-deleted
  - **Files**: `dapr/subscriptions/backend-subscriptions.yaml`
  - **Completed**: 2026-01-27

- [X] T015 [US2] [Local] Create Dapr Subscription for backend to subscribe to "todo-reminder" topic
  - **Spec Ref**: FR-010, FR-028
  - **Verification**: `kubectl get subscription backend-todo-reminder` shows subscription created ✅
  - **Config**: pubsubname: pubsub-kafka, topic: todo-reminder, route: /events/todo-reminder
  - **Files**: `dapr/subscriptions/backend-subscriptions.yaml`
  - **Completed**: 2026-01-27

**Checkpoint**: All Dapr components and subscriptions are deployed on Minikube

---

## Phase 3: Backend Service Implementation - Event Publishers & Handlers

**Purpose**: Implement backend service with Dapr SDK, event publishing, and event handling
**Target**: Both (Local + Cloud)
**Category**: Backend Implementation

### Backend Project Structure & Dependencies

- [ ] T016 [P] [US1] [Both] Create backend project structure in backend/src/ with subdirectories: dapr/, events/, api/, services/, models/
  - **Spec Ref**: Project structure from plan.md
  - **Verification**: Directory structure exists
  - **Files**: `backend/src/dapr/`, `backend/src/events/`, `backend/src/api/`, `backend/src/services/`, `backend/src/models/`

- [ ] T017 [US1] [Both] Initialize FastAPI backend with Dapr SDK dependencies in backend/requirements.txt and backend/src/main.py
  - **Spec Ref**: FR-009, FR-010, FR-011
  - **Verification**: `pip install -r backend/requirements.txt` succeeds, FastAPI app starts
  - **Files**: `backend/requirements.txt` (add fastapi, uvicorn, dapr, dapr-ext-fastapi), `backend/src/main.py`

### Dapr Client Integration

- [ ] T018 [P] [US1] [Both] Implement Dapr Pub/Sub client wrapper in backend/src/dapr/pubsub.py with publish_event() method
  - **Spec Ref**: FR-010
  - **Verification**: Unit test publishes test event to Kafka via Dapr
  - **Files**: `backend/src/dapr/pubsub.py`, `backend/tests/unit/test_dapr_pubsub.py`

- [ ] T019 [P] [US1] [Both] Implement Dapr State Store client wrapper in backend/src/dapr/state.py with get(), set(), delete(), etag methods
  - **Spec Ref**: FR-011
  - **Verification**: Unit test reads/writes state to Redis via Dapr
  - **Files**: `backend/src/dapr/state.py`, `backend/tests/unit/test_dapr_state.py`

- [ ] T020 [P] [US1] [Both] Implement Dapr Secrets client wrapper in backend/src/dapr/secrets.py with get_secret() method
  - **Spec Ref**: FR-012, FR-047
  - **Verification**: Unit test retrieves secret from Kubernetes Secrets via Dapr
  - **Files**: `backend/src/dapr/secrets.py`, `backend/tests/unit/test_dapr_secrets.py`

- [ ] T021 [P] [US2] [Both] Implement Dapr Jobs API client wrapper in backend/src/dapr/jobs.py with schedule_job(), cancel_job() methods
  - **Spec Ref**: FR-013, FR-029, FR-030
  - **Verification**: Unit test schedules and cancels job via Dapr Jobs API
  - **Files**: `backend/src/dapr/jobs.py`, `backend/tests/unit/test_dapr_jobs.py`

### Domain Models

- [ ] T022 [P] [US1] [Both] Create Task domain model in backend/src/models/task.py with validation for title, priority, tags, dueDate
  - **Spec Ref**: FR-016, FR-020, FR-021, FR-028
  - **Verification**: Unit test validates all Task attributes and constraints (max 50 tags, title not empty, dueDate in future)
  - **Files**: `backend/src/models/task.py`, `backend/tests/unit/test_task_model.py`

- [ ] T023 [P] [US1] [Both] Create Event domain model in backend/src/models/event.py with eventId, eventType, timestamp, todoId, userId, payload
  - **Spec Ref**: FR-005, FR-006
  - **Verification**: Unit test creates event instances for all 4 event types
  - **Files**: `backend/src/models/event.py`, `backend/tests/unit/test_event_model.py`

### Event Schema Validation

- [ ] T024 [US1] [Both] Implement JSON Schema validation in backend/src/events/schemas.py for all 4 event types (todo-created, todo-updated, todo-deleted, todo-reminder)
  - **Spec Ref**: FR-006, FR-007
  - **Verification**: Unit test validates events against JSON Schema files from specs/004-event-driven-todo/contracts/events/
  - **Files**: `backend/src/events/schemas.py`, `backend/tests/contract/test_event_schemas.py`

### Event Publishers

- [ ] T025 [US1] [Both] Implement todo-created event publisher in backend/src/events/publishers.py with idempotency via eventId
  - **Spec Ref**: FR-001, FR-005, FR-007
  - **Verification**: Integration test publishes todo-created event to Kafka with valid schema and partition key (todoId)
  - **Files**: `backend/src/events/publishers.py`, `backend/tests/integration/test_publishers.py`

- [ ] T026 [US1] [Both] Implement todo-updated event publisher in backend/src/events/publishers.py with changedFields tracking
  - **Spec Ref**: FR-002, FR-005
  - **Verification**: Integration test publishes todo-updated event with changedFields array
  - **Files**: `backend/src/events/publishers.py` (add publish_todo_updated)

- [ ] T027 [US1] [Both] Implement todo-deleted event publisher in backend/src/events/publishers.py with minimal payload
  - **Spec Ref**: FR-003, FR-005
  - **Verification**: Integration test publishes todo-deleted event with wasCompleted, hadDueDate, wasRecurring flags
  - **Files**: `backend/src/events/publishers.py` (add publish_todo_deleted)

- [ ] T028 [US2] [Both] Implement todo-reminder event publisher in backend/src/events/publishers.py triggered by Dapr Jobs API
  - **Spec Ref**: FR-004, FR-005, FR-013
  - **Verification**: Integration test schedules job that publishes todo-reminder event at scheduled time
  - **Files**: `backend/src/events/publishers.py` (add publish_todo_reminder)

### Event Subscribers (Idempotent Handlers)

- [ ] T029 [US1] [Both] Implement todo-created event subscriber in backend/src/events/subscribers.py with idempotency check via eventId
  - **Spec Ref**: FR-007, FR-008
  - **Verification**: Integration test sends duplicate events, confirms only one is processed (state store checks eventId)
  - **Files**: `backend/src/events/subscribers.py`, `backend/tests/integration/test_event_flows.py`

- [ ] T030 [US1] [Both] Implement todo-updated event subscriber in backend/src/events/subscribers.py with ETag-based concurrency control
  - **Spec Ref**: FR-007, FR-008
  - **Verification**: Integration test updates same task concurrently, confirms ETag prevents lost updates
  - **Files**: `backend/src/events/subscribers.py` (add handle_todo_updated)

- [ ] T031 [US1] [Both] Implement todo-deleted event subscriber in backend/src/events/subscribers.py with reminder job cancellation
  - **Spec Ref**: FR-007, FR-008, FR-030
  - **Verification**: Integration test deletes task, confirms reminder job is cancelled via Dapr Jobs API
  - **Files**: `backend/src/events/subscribers.py` (add handle_todo_deleted)

- [ ] T032 [US2] [Both] Implement todo-reminder event subscriber in backend/src/events/subscribers.py for notification handling
  - **Spec Ref**: FR-007, FR-008
  - **Verification**: Integration test processes reminder event, confirms notification sent (logs for Phase V)
  - **Files**: `backend/src/events/subscribers.py` (add handle_todo_reminder)

**Checkpoint**: Backend can publish and consume all 4 event types idempotently via Dapr Pub/Sub

---

## Phase 4: Backend Service Business Logic - Task Management

**Purpose**: Implement task CRUD operations with event publishing
**Target**: Both (Local + Cloud)
**Category**: Backend Implementation

### Task Service Layer

- [ ] T033 [US1] [Both] Implement TaskService.create_task() in backend/src/services/task_service.py with State Store persistence, todo-created event publishing, and dueDate validation (reject past dates)
  - **Spec Ref**: FR-016, FR-001, FR-011, Edge Case: due date in past
  - **Verification**: Integration test creates task, confirms stored in State Store and event published to Kafka; unit test validates dueDate rejection for past dates
  - **Files**: `backend/src/services/task_service.py`, `backend/tests/integration/test_task_service.py`, `backend/tests/unit/test_task_validation.py`

- [ ] T034 [US1] [Both] Implement TaskService.update_task() in backend/src/services/task_service.py with ETag concurrency control and todo-updated event publishing
  - **Spec Ref**: FR-017, FR-002, FR-011
  - **Verification**: Integration test updates task, confirms state updated with ETag check and event published
  - **Files**: `backend/src/services/task_service.py` (add update_task)

- [ ] T035 [US1] [Both] Implement TaskService.delete_task() in backend/src/services/task_service.py with State Store deletion and todo-deleted event publishing
  - **Spec Ref**: FR-018, FR-003, FR-011
  - **Verification**: Integration test deletes task, confirms removed from State Store and event published
  - **Files**: `backend/src/services/task_service.py` (add delete_task)

- [ ] T036 [US1] [Both] Implement TaskService.get_task() in backend/src/services/task_service.py to retrieve task from State Store by todoId
  - **Spec Ref**: FR-011
  - **Verification**: Unit test retrieves existing task, returns None for non-existent task
  - **Files**: `backend/src/services/task_service.py` (add get_task)

- [ ] T037 [US1] [Both] Implement TaskService.list_tasks() in backend/src/services/task_service.py to retrieve all tasks for userId from State Store
  - **Spec Ref**: FR-011
  - **Verification**: Integration test lists tasks for user, confirms only user's tasks returned
  - **Files**: `backend/src/services/task_service.py` (add list_tasks)

- [ ] T038 [US1] [Both] Implement TaskService.mark_complete() in backend/src/services/task_service.py to toggle completion status with todo-updated event
  - **Spec Ref**: FR-019, FR-002
  - **Verification**: Integration test marks task complete, confirms state updated and event published
  - **Files**: `backend/src/services/task_service.py` (add mark_complete)

### Reminder Service Layer

- [ ] T039 [US2] [Both] Implement ReminderService.schedule_reminder() in backend/src/services/reminder_service.py to create Dapr Job 24h before dueDate
  - **Spec Ref**: FR-029, FR-013
  - **Verification**: Integration test sets dueDate, confirms Dapr Job scheduled for dueDate - 24h
  - **Files**: `backend/src/services/reminder_service.py`, `backend/tests/integration/test_reminder_service.py`

- [ ] T040 [US2] [Both] Implement ReminderService.cancel_reminder() in backend/src/services/reminder_service.py to cancel Dapr Job when task completed or deleted
  - **Spec Ref**: FR-030, FR-013
  - **Verification**: Integration test completes task, confirms Dapr Job cancelled
  - **Files**: `backend/src/services/reminder_service.py` (add cancel_reminder)

- [ ] T041 [US2] [Both] Implement ReminderService.reschedule_reminder() in backend/src/services/reminder_service.py to update Dapr Job when dueDate changes
  - **Spec Ref**: FR-031, FR-013
  - **Verification**: Integration test updates dueDate, confirms old job cancelled and new job scheduled
  - **Files**: `backend/src/services/reminder_service.py` (add reschedule_reminder)

- [ ] T041A [US2] [Both] Implement timezone conversion service in backend/src/services/timezone_service.py for due dates and reminders (UTC storage, user timezone display)
  - **Spec Ref**: FR-032
  - **Verification**: Unit test converts UTC timestamps to user timezone and vice versa, integration test creates task with timezone-aware dueDate
  - **Files**: `backend/src/services/timezone_service.py`, `backend/tests/unit/test_timezone_service.py`

### Search and Filter Service Layer

- [ ] T042 [US3] [Both] Implement SearchService.filter_by_priority() in backend/src/services/search_service.py to filter tasks from State Store by priority
  - **Spec Ref**: FR-022
  - **Verification**: Integration test filters by High priority, confirms only High priority tasks returned
  - **Files**: `backend/src/services/search_service.py`, `backend/tests/integration/test_search_service.py`

- [ ] T043 [US3] [Both] Implement SearchService.filter_by_tags() in backend/src/services/search_service.py to filter tasks by tags with AND logic
  - **Spec Ref**: FR-023
  - **Verification**: Integration test filters by multiple tags, confirms only tasks with ALL tags returned
  - **Files**: `backend/src/services/search_service.py` (add filter_by_tags)

- [ ] T044 [US4] [Both] Implement SearchService.search_by_keyword() in backend/src/services/search_service.py to search title and description
  - **Spec Ref**: FR-024
  - **Verification**: Integration test searches keyword, confirms matching tasks returned (case-insensitive)
  - **Files**: `backend/src/services/search_service.py` (add search_by_keyword)

- [ ] T045 [US4] [Both] Implement SearchService.sort_tasks() in backend/src/services/search_service.py to sort by dueDate, priority, or createdAt
  - **Spec Ref**: FR-025
  - **Verification**: Integration test sorts tasks by dueDate ascending, confirms correct order
  - **Files**: `backend/src/services/search_service.py` (add sort_tasks)

### Recurring Tasks Service Layer

- [ ] T046 [US5] [Both] Implement RecurringService.create_recurring_task() in backend/src/services/recurring_service.py with Dapr Job for next occurrence and minimum 1-hour interval validation
  - **Spec Ref**: FR-026, FR-026A, FR-013
  - **Verification**: Integration test creates daily recurring task, confirms Dapr Job scheduled for next occurrence; unit test validates rejection of intervals < 1 hour
  - **Files**: `backend/src/services/recurring_service.py`, `backend/tests/integration/test_recurring_service.py`, `backend/tests/unit/test_recurring_validation.py`

- [ ] T047 [US5] [Both] Implement RecurringService.handle_recurring_completion() in backend/src/services/recurring_service.py to recreate task after completion
  - **Spec Ref**: FR-027
  - **Verification**: Integration test completes recurring task, confirms new instance created with updated dueDate
  - **Files**: `backend/src/services/recurring_service.py` (add handle_recurring_completion)

**Checkpoint**: Backend business logic is complete with State Store persistence, event publishing, and Dapr Jobs integration

---

## Phase 5: Backend API Endpoints - HTTP/Dapr Service Invocation

**Purpose**: Expose HTTP API endpoints for frontend via Dapr Service Invocation
**Target**: Both (Local + Cloud)
**Category**: Backend Implementation

### Task CRUD API Endpoints

- [ ] T048 [P] [US1] [Both] Implement POST /api/tasks endpoint in backend/src/api/tasks.py to create task via TaskService
  - **Spec Ref**: FR-016
  - **Verification**: Integration test POSTs task, confirms 201 response and task created in State Store
  - **Files**: `backend/src/api/tasks.py`, `backend/tests/integration/test_api_tasks.py`

- [ ] T049 [P] [US1] [Both] Implement GET /api/tasks endpoint in backend/src/api/tasks.py to list tasks via TaskService
  - **Spec Ref**: FR-011
  - **Verification**: Integration test GETs tasks, confirms 200 response with task list
  - **Files**: `backend/src/api/tasks.py` (add GET /tasks)

- [ ] T050 [P] [US1] [Both] Implement GET /api/tasks/{id} endpoint in backend/src/api/tasks.py to retrieve single task via TaskService
  - **Spec Ref**: FR-011
  - **Verification**: Integration test GETs task by ID, confirms 200 response or 404 if not found
  - **Files**: `backend/src/api/tasks.py` (add GET /tasks/{id})

- [ ] T051 [P] [US1] [Both] Implement PUT /api/tasks/{id} endpoint in backend/src/api/tasks.py to update task via TaskService
  - **Spec Ref**: FR-017
  - **Verification**: Integration test PUTs updated task, confirms 200 response and state updated
  - **Files**: `backend/src/api/tasks.py` (add PUT /tasks/{id})

- [ ] T052 [P] [US1] [Both] Implement DELETE /api/tasks/{id} endpoint in backend/src/api/tasks.py to delete task via TaskService
  - **Spec Ref**: FR-018
  - **Verification**: Integration test DELETEs task, confirms 204 response and task removed from State Store
  - **Files**: `backend/src/api/tasks.py` (add DELETE /tasks/{id})

- [ ] T053 [P] [US1] [Both] Implement PATCH /api/tasks/{id}/complete endpoint in backend/src/api/tasks.py to toggle completion via TaskService
  - **Spec Ref**: FR-019
  - **Verification**: Integration test PATCHes complete status, confirms 200 response and completion toggled
  - **Files**: `backend/src/api/tasks.py` (add PATCH /tasks/{id}/complete)

### Search and Filter API Endpoints

- [ ] T054 [US4] [Both] Implement GET /api/search endpoint in backend/src/api/search.py with query params: keyword, priority, tags[], sortBy
  - **Spec Ref**: FR-022, FR-023, FR-024, FR-025
  - **Verification**: Integration test GETs /search?keyword=test&priority=High&sortBy=dueDate, confirms filtered and sorted results
  - **Files**: `backend/src/api/search.py`, `backend/tests/integration/test_api_search.py`

### Reminder Management API Endpoints

- [ ] T055 [US2] [Both] Implement POST /api/reminders endpoint in backend/src/api/reminders.py to manually trigger reminder for task
  - **Spec Ref**: FR-028, FR-029
  - **Verification**: Integration test POSTs reminder request, confirms Dapr Job scheduled
  - **Files**: `backend/src/api/reminders.py`, `backend/tests/integration/test_api_reminders.py`

### Health Check Endpoint

- [ ] T056 [P] [US6] [Both] Implement GET /health endpoint in backend/src/api/health.py with Dapr sidecar readiness check
  - **Spec Ref**: FR-039
  - **Verification**: Integration test GETs /health, confirms 200 response when Dapr sidecar is ready
  - **Files**: `backend/src/api/health.py`

**Checkpoint**: Backend API is complete and ready for frontend integration

---

## Phase 6: Frontend Implementation - Next.js with Dapr SDK

**Purpose**: Implement frontend service with Next.js and Dapr SDK for service invocation
**Target**: Both (Local + Cloud)
**Category**: Frontend Implementation

### Frontend Project Structure & Dependencies

- [ ] T057 [P] [US1] [Both] Create frontend project structure in frontend/src/ with subdirectories: dapr/, components/, pages/, services/
  - **Spec Ref**: Project structure from plan.md
  - **Verification**: Directory structure exists
  - **Files**: `frontend/src/dapr/`, `frontend/src/components/`, `frontend/src/pages/`, `frontend/src/services/`

- [ ] T058 [US1] [Both] Initialize Next.js frontend with TypeScript and Dapr SDK in frontend/package.json
  - **Spec Ref**: FR-009
  - **Verification**: `npm install` succeeds, Next.js app starts
  - **Files**: `frontend/package.json` (add next, react, @dapr/dapr), `frontend/tsconfig.json`

### Dapr Service Invocation Client

- [ ] T059 [US1] [Both] Implement Dapr Service Invocation client in frontend/src/dapr/serviceinvocation.ts to call backend via app-id
  - **Spec Ref**: FR-009
  - **Verification**: Unit test invokes backend health endpoint via Dapr, confirms response
  - **Files**: `frontend/src/dapr/serviceinvocation.ts`, `frontend/tests/unit/test_dapr_invocation.ts`

### Frontend Service Layer (API Wrappers)

- [ ] T060 [P] [US1] [Both] Implement TaskService.createTask() in frontend/src/services/taskService.ts via Dapr Service Invocation
  - **Spec Ref**: FR-016, FR-009
  - **Verification**: Integration test creates task via frontend service, confirms backend receives request
  - **Files**: `frontend/src/services/taskService.ts`, `frontend/tests/integration/test_task_service.ts`

- [ ] T061 [P] [US1] [Both] Implement TaskService.listTasks() in frontend/src/services/taskService.ts via Dapr Service Invocation
  - **Spec Ref**: FR-009
  - **Verification**: Integration test lists tasks via frontend service, confirms response from backend
  - **Files**: `frontend/src/services/taskService.ts` (add listTasks)

- [ ] T062 [P] [US1] [Both] Implement TaskService.updateTask() in frontend/src/services/taskService.ts via Dapr Service Invocation
  - **Spec Ref**: FR-017, FR-009
  - **Verification**: Integration test updates task via frontend service, confirms backend receives update
  - **Files**: `frontend/src/services/taskService.ts` (add updateTask)

- [ ] T063 [P] [US1] [Both] Implement TaskService.deleteTask() in frontend/src/services/taskService.ts via Dapr Service Invocation
  - **Spec Ref**: FR-018, FR-009
  - **Verification**: Integration test deletes task via frontend service, confirms backend receives deletion
  - **Files**: `frontend/src/services/taskService.ts` (add deleteTask)

- [ ] T064 [US4] [Both] Implement SearchService.searchTasks() in frontend/src/services/searchService.ts via Dapr Service Invocation
  - **Spec Ref**: FR-024, FR-025, FR-009
  - **Verification**: Integration test searches tasks with filters/sort, confirms backend returns results
  - **Files**: `frontend/src/services/searchService.ts`, `frontend/tests/integration/test_search_service.ts`

### React Components

- [ ] T065 [P] [US1] [Both] Create TaskList component in frontend/src/components/TaskList.tsx to display tasks with priority badges and tags
  - **Spec Ref**: FR-020, FR-021
  - **Verification**: Unit test renders task list with 3 tasks, confirms priority colors and tags displayed
  - **Files**: `frontend/src/components/TaskList.tsx`, `frontend/tests/unit/test_TaskList.test.tsx`

- [ ] T066 [P] [US1] [Both] Create TaskForm component in frontend/src/components/TaskForm.tsx for create/edit with title, description, priority, tags, dueDate inputs
  - **Spec Ref**: FR-016, FR-017
  - **Verification**: Unit test renders form, fills inputs, submits, confirms onSubmit callback called
  - **Files**: `frontend/src/components/TaskForm.tsx`, `frontend/tests/unit/test_TaskForm.test.tsx`

- [ ] T067 [P] [US3] [Both] Create SearchFilter component in frontend/src/components/SearchFilter.tsx with keyword input, priority dropdown, tags multi-select
  - **Spec Ref**: FR-022, FR-023, FR-024
  - **Verification**: Unit test renders filter controls, changes values, confirms onChange callback called
  - **Files**: `frontend/src/components/SearchFilter.tsx`, `frontend/tests/unit/test_SearchFilter.test.tsx`

- [ ] T068 [P] [US2] [Both] Create ReminderSettings component in frontend/src/components/ReminderSettings.tsx for due date picker with reminder toggle
  - **Spec Ref**: FR-028, FR-029
  - **Verification**: Unit test renders date picker, sets date, confirms onChange callback called
  - **Files**: `frontend/src/components/ReminderSettings.tsx`, `frontend/tests/unit/test_ReminderSettings.test.tsx`

### Next.js Pages

- [ ] T069 [US1] [Both] Create index page in frontend/src/pages/index.tsx with TaskList and SearchFilter components
  - **Spec Ref**: FR-016, FR-024
  - **Verification**: Integration test loads page, confirms task list and search filter rendered
  - **Files**: `frontend/src/pages/index.tsx`, `frontend/tests/integration/test_index_page.ts`

- [ ] T070 [US1] [Both] Create task detail page in frontend/src/pages/tasks/[id].tsx with TaskForm component for editing
  - **Spec Ref**: FR-017
  - **Verification**: Integration test navigates to task detail, edits task, confirms update sent to backend
  - **Files**: `frontend/src/pages/tasks/[id].tsx`, `frontend/tests/integration/test_task_detail_page.ts`

**Checkpoint**: Frontend can create, list, update, delete tasks with search/filter via Dapr Service Invocation

---

## Phase 7: Helm Charts for Local Deployment (Minikube)

**Purpose**: Create Helm charts with Minikube-specific configuration
**Target**: Local (Minikube)
**Category**: Minikube Deployment

### Helm Chart Structure

- [ ] T071 [US6] [Local] Create Helm chart structure in helm/todo-app-event-driven/ with Chart.yaml, values.yaml, values-minikube.yaml
  - **Spec Ref**: FR-037
  - **Verification**: `helm lint helm/todo-app-event-driven` passes
  - **Files**: `helm/todo-app-event-driven/Chart.yaml`, `helm/todo-app-event-driven/values.yaml`, `helm/todo-app-event-driven/values-minikube.yaml`

### Application Deployment Templates

- [ ] T072 [US6] [Local] Create backend Deployment template in helm/todo-app-event-driven/templates/deployment-backend.yaml with Dapr sidecar annotations
  - **Spec Ref**: FR-014, FR-037
  - **Verification**: `helm template` renders deployment with dapr.io/enabled: "true", dapr.io/app-id: "backend", dapr.io/app-port: "8000"
  - **Files**: `helm/todo-app-event-driven/templates/deployment-backend.yaml`

- [ ] T073 [US6] [Local] Create frontend Deployment template in helm/todo-app-event-driven/templates/deployment-frontend.yaml with Dapr sidecar annotations
  - **Spec Ref**: FR-014, FR-037
  - **Verification**: `helm template` renders deployment with dapr.io/enabled: "true", dapr.io/app-id: "frontend", dapr.io/app-port: "3000"
  - **Files**: `helm/todo-app-event-driven/templates/deployment-frontend.yaml`

- [ ] T074 [P] [US6] [Local] Create backend Service template in helm/todo-app-event-driven/templates/service-backend.yaml with ClusterIP type
  - **Spec Ref**: FR-037
  - **Verification**: `helm template` renders Service with port 8000
  - **Files**: `helm/todo-app-event-driven/templates/service-backend.yaml`

- [ ] T075 [P] [US6] [Local] Create frontend Service template in helm/todo-app-event-driven/templates/service-frontend.yaml with NodePort type for Minikube
  - **Spec Ref**: FR-033, FR-037
  - **Verification**: `helm template` with values-minikube.yaml renders NodePort Service
  - **Files**: `helm/todo-app-event-driven/templates/service-frontend.yaml`

### Dapr Component Templates

- [ ] T076 [P] [US6] [Local] Copy dapr/components/pubsub-kafka.yaml to helm/todo-app-event-driven/templates/dapr-components/pubsub.yaml
  - **Spec Ref**: FR-015, FR-037
  - **Verification**: `helm template` renders Pub/Sub component
  - **Files**: `helm/todo-app-event-driven/templates/dapr-components/pubsub.yaml`

- [ ] T077 [P] [US6] [Local] Copy dapr/components/statestore-redis.yaml to helm/todo-app-event-driven/templates/dapr-components/statestore.yaml
  - **Spec Ref**: FR-015, FR-037
  - **Verification**: `helm template` renders State Store component
  - **Files**: `helm/todo-app-event-driven/templates/dapr-components/statestore.yaml`

- [ ] T078 [P] [US6] [Local] Copy dapr/components/secrets-kubernetes.yaml to helm/todo-app-event-driven/templates/dapr-components/secrets.yaml
  - **Spec Ref**: FR-015, FR-037
  - **Verification**: `helm template` renders Secrets component
  - **Files**: `helm/todo-app-event-driven/templates/dapr-components/secrets.yaml`

### ConfigMap and Secret Templates

- [ ] T079 [P] [US6] [Local] Create ConfigMap template in helm/todo-app-event-driven/templates/configmap.yaml for environment variables
  - **Spec Ref**: FR-037
  - **Verification**: `helm template` renders ConfigMap with DAPR_HTTP_PORT, DAPR_GRPC_PORT
  - **Files**: `helm/todo-app-event-driven/templates/configmap.yaml`

- [ ] T080 [P] [US6] [Local] Create Secret template in helm/todo-app-event-driven/templates/secret.yaml for sensitive configuration
  - **Spec Ref**: FR-046
  - **Verification**: `helm template` renders Secret with base64-encoded values
  - **Files**: `helm/todo-app-event-driven/templates/secret.yaml`

### Minikube Values Configuration

- [ ] T081 [US6] [Local] Configure values-minikube.yaml with local settings: imagePullPolicy: IfNotPresent, NodePort service, single replicas
  - **Spec Ref**: FR-033
  - **Verification**: `helm template -f values-minikube.yaml` renders with Minikube-specific configuration
  - **Files**: `helm/todo-app-event-driven/values-minikube.yaml`

**Checkpoint**: Helm chart can deploy application to Minikube with Dapr sidecars and components

---

## Phase 8: Local Deployment Validation (Minikube)

**Purpose**: Deploy complete stack to Minikube and validate end-to-end event flows
**Target**: Local (Minikube)
**Category**: Minikube Deployment

### Build Docker Images for Minikube

- [ ] T082 [US6] [Local] Create Dockerfile for backend in backend/Dockerfile with Python 3.13+ base image
  - **Spec Ref**: FR-033
  - **Verification**: `docker build -t todo-backend:dev backend/` succeeds
  - **Files**: `backend/Dockerfile`

- [ ] T083 [US6] [Local] Create Dockerfile for frontend in frontend/Dockerfile with Node.js 18+ base image
  - **Spec Ref**: FR-033
  - **Verification**: `docker build -t todo-frontend:dev frontend/` succeeds
  - **Files**: `frontend/Dockerfile`

- [ ] T084 [US6] [Local] Build and load Docker images into Minikube via `eval $(minikube docker-env) && docker build ...`
  - **Spec Ref**: FR-033
  - **Verification**: `minikube ssh docker images` shows todo-backend:dev and todo-frontend:dev
  - **Files**: None (Docker build commands)

### Deploy Full Stack to Minikube

- [ ] T085 [US6] [Local] Deploy Helm chart to Minikube with values-minikube.yaml: `helm install todo-app ./helm/todo-app-event-driven -f values-minikube.yaml`
  - **Spec Ref**: FR-033, FR-037
  - **Verification**: `helm status todo-app` shows deployed, all pods show 2/2 Ready (app + Dapr sidecar)
  - **Files**: None (Helm install command)

- [ ] T086 [US6] [Local] Verify Dapr sidecars are injected by checking pod container count: `kubectl get pods -o jsonpath='{.items[*].spec.containers[*].name}'`
  - **Spec Ref**: FR-014
  - **Verification**: Each pod has 2 containers (app + daprd)
  - **Files**: None (kubectl command)

### End-to-End Event Flow Validation

- [ ] T087 [US1] [Local] Test end-to-end event flow: Create task via frontend, verify backend processes todo-created event from Kafka
  - **Spec Ref**: FR-001, SC-001
  - **Verification**: Create task in frontend UI → Check backend logs for "Event received: todo-created" → Check State Store for task → Latency < 2 seconds
  - **Files**: `backend/tests/e2e/test_event_flow_create.py`

- [ ] T088 [US1] [Local] Test end-to-end event flow: Update task via frontend, verify backend processes todo-updated event from Kafka
  - **Spec Ref**: FR-002, SC-001
  - **Verification**: Update task in frontend UI → Check backend logs for "Event received: todo-updated" → Check State Store for updated task
  - **Files**: `backend/tests/e2e/test_event_flow_update.py`

- [ ] T089 [US1] [Local] Test end-to-end event flow: Delete task via frontend, verify backend processes todo-deleted event from Kafka
  - **Spec Ref**: FR-003, SC-001
  - **Verification**: Delete task in frontend UI → Check backend logs for "Event received: todo-deleted" → Check State Store confirms deletion
  - **Files**: `backend/tests/e2e/test_event_flow_delete.py`

- [ ] T090 [US2] [Local] Test end-to-end event flow: Set due date, verify reminder job scheduled and todo-reminder event published at scheduled time
  - **Spec Ref**: FR-004, FR-029, SC-003
  - **Verification**: Set dueDate 25 hours in future → Wait for scheduled time → Check backend logs for "Event received: todo-reminder" → Verify within 5 minutes of scheduled time
  - **Files**: `backend/tests/e2e/test_event_flow_reminder.py`

### Idempotency and Concurrency Validation

- [ ] T091 [US1] [Local] Test idempotent event handling: Publish duplicate todo-created events, verify only one task created in State Store
  - **Spec Ref**: FR-007, SC-007
  - **Verification**: Publish same event with same eventId twice → Check State Store shows only 1 task → Check backend logs show "Duplicate event ignored"
  - **Files**: `backend/tests/e2e/test_idempotency.py`

- [ ] T092 [US1] [Local] Test ETag-based concurrency control: Update same task concurrently from 2 clients, verify one update succeeds and one fails with 409 Conflict
  - **Spec Ref**: FR-011 (ETag usage)
  - **Verification**: Update task from 2 frontend instances simultaneously → One returns 200, other returns 409
  - **Files**: `backend/tests/e2e/test_concurrency.py`

### Kafka Topic Inspection

- [ ] T093 [US1] [Local] Verify Kafka topics contain events: `kubectl exec -n kafka my-cluster-kafka-0 -- bin/kafka-console-consumer.sh --topic todo-created --from-beginning --max-messages 10`
  - **Spec Ref**: FR-001, FR-002, FR-003, FR-004
  - **Verification**: Console consumer shows CloudEvents-formatted events in all 4 topics
  - **Files**: None (kubectl exec command)

**Checkpoint**: Minikube deployment is complete, all event flows validated, idempotency confirmed

---

## Phase 9: Cloud Infrastructure Setup (OKE)

**Purpose**: Provision Oracle Kubernetes Engine cluster and managed Kafka infrastructure
**Target**: Cloud (OKE)
**Category**: Cloud Deployment

### OKE Cluster Provisioning

- [ ] T094 [US7] [Cloud] Create OKE cluster provisioning script in scripts/provision-oke-cluster.sh with OCI CLI commands
  - **Spec Ref**: FR-034
  - **Verification**: Script provisions OKE cluster with 3 worker nodes (2 CPU, 8GB RAM each)
  - **Files**: `scripts/provision-oke-cluster.sh`

- [ ] T095 [US7] [Cloud] Provision OKE cluster via script: `bash scripts/provision-oke-cluster.sh`
  - **Spec Ref**: FR-034
  - **Verification**: `kubectl get nodes` shows 3 Ready nodes, `kubectl cluster-info` shows OKE endpoint
  - **Files**: None (OCI provisioning)

### Managed Kafka Setup (Redpanda Cloud / Confluent Cloud)

- [ ] T096 [US7] [Cloud] Provision managed Kafka cluster on Redpanda Cloud or Confluent Cloud with 3 brokers, 3 partitions per topic
  - **Spec Ref**: FR-035
  - **Verification**: Kafka cluster shows Running, broker endpoints available, credentials configured
  - **Files**: `docs/oke-kafka-setup.md` (manual steps for managed Kafka)

- [ ] T097 [US7] [Cloud] Create Kafka topics on managed cluster: todo-created, todo-updated, todo-deleted, todo-reminder with 3 partitions, 7-day retention
  - **Spec Ref**: FR-035
  - **Verification**: Managed Kafka UI or CLI shows 4 topics with correct configuration
  - **Files**: `kafka/topics/create-cloud-topics.sh` (script to create topics on managed Kafka)

- [ ] T098 [US7] [Cloud] Create Kubernetes Secret for managed Kafka credentials: `kubectl create secret generic kafka-credentials --from-literal=brokers=... --from-literal=username=... --from-literal=password=...`
  - **Spec Ref**: FR-046
  - **Verification**: `kubectl get secret kafka-credentials` shows secret created
  - **Files**: None (kubectl command)

### Dapr Control Plane for Production

- [ ] T099 [US7] [Cloud] Install Dapr control plane on OKE with production configuration: `dapr init --kubernetes --enable-ha --enable-mtls --wait`
  - **Spec Ref**: FR-034
  - **Verification**: `kubectl get pods -n dapr-system` shows 5/5 Running with 3 replicas for placement server (HA)
  - **Files**: None (Dapr CLI command)

### Redis State Store for Production

- [ ] T100 [US7] [Cloud] Deploy Redis cluster on OKE via Helm with persistence enabled and 3 replicas: `helm install redis bitnami/redis --set replica.replicaCount=3 --set master.persistence.enabled=true`
  - **Spec Ref**: FR-036
  - **Verification**: `kubectl get pods | grep redis` shows 1 master + 3 replicas Running
  - **Files**: None (Helm chart)

**Checkpoint**: OKE cluster, managed Kafka, Dapr control plane, and Redis are deployed and healthy

---

## Phase 10: Helm Charts for Cloud Deployment (OKE)

**Purpose**: Create OKE-specific Helm configuration with production settings
**Target**: Cloud (OKE)
**Category**: Cloud Deployment

### OKE Values Configuration

- [ ] T101 [US7] [Cloud] Configure values-oke.yaml with production settings: LoadBalancer service, multiple replicas (3), resource limits, autoscaling
  - **Spec Ref**: FR-034, FR-039
  - **Verification**: `helm template -f values-oke.yaml` renders with LoadBalancer, 3 replicas, CPU/memory limits
  - **Files**: `helm/todo-app-event-driven/values-oke.yaml`

### Production Dapr Component Configuration

- [ ] T102 [US7] [Cloud] Update Pub/Sub component template to use managed Kafka brokers and credentials from Kubernetes Secret
  - **Spec Ref**: FR-015, FR-035, FR-047
  - **Verification**: `helm template -f values-oke.yaml` renders Pub/Sub component with secretKeyRef for Kafka credentials
  - **Files**: `helm/todo-app-event-driven/templates/dapr-components/pubsub.yaml` (add conditional for cloud)

- [ ] T103 [US7] [Cloud] Update State Store component template to use Redis cluster with persistence
  - **Spec Ref**: FR-036
  - **Verification**: `helm template -f values-oke.yaml` renders State Store component with Redis cluster endpoint
  - **Files**: `helm/todo-app-event-driven/templates/dapr-components/statestore.yaml` (add conditional for cloud)

### Health Checks and Probes

- [ ] T104 [US7] [Cloud] Add Kubernetes readiness and liveness probes to backend Deployment template
  - **Spec Ref**: FR-039
  - **Verification**: `helm template -f values-oke.yaml` renders deployment with readinessProbe: /health, livenessProbe: /health
  - **Files**: `helm/todo-app-event-driven/templates/deployment-backend.yaml` (add probes)

- [ ] T105 [US7] [Cloud] Add Kubernetes readiness and liveness probes to frontend Deployment template
  - **Spec Ref**: FR-039
  - **Verification**: `helm template -f values-oke.yaml` renders deployment with readinessProbe: /, livenessProbe: /
  - **Files**: `helm/todo-app-event-driven/templates/deployment-frontend.yaml` (add probes)

### Horizontal Pod Autoscaling

- [ ] T106 [US7] [Cloud] Create HorizontalPodAutoscaler template for backend in helm/todo-app-event-driven/templates/hpa-backend.yaml
  - **Spec Ref**: FR-034 (scaling considerations)
  - **Verification**: `helm template -f values-oke.yaml` renders HPA with minReplicas: 3, maxReplicas: 10, targetCPUUtilizationPercentage: 70
  - **Files**: `helm/todo-app-event-driven/templates/hpa-backend.yaml`

- [ ] T107 [US7] [Cloud] Create HorizontalPodAutoscaler template for frontend in helm/todo-app-event-driven/templates/hpa-frontend.yaml
  - **Spec Ref**: FR-034
  - **Verification**: `helm template -f values-oke.yaml` renders HPA with minReplicas: 3, maxReplicas: 10
  - **Files**: `helm/todo-app-event-driven/templates/hpa-frontend.yaml`

**Checkpoint**: Helm chart supports production deployment to OKE with HA, autoscaling, and health checks

---

## Phase 11: CI/CD Pipeline Setup (GitHub Actions)

**Purpose**: Automate build, test, and deployment to OKE via GitHub Actions
**Target**: Cloud (OKE)
**Category**: CI/CD Setup

### Container Registry Setup

- [ ] T108 [US7] [Cloud] Create GitHub Secrets for OCI container registry credentials: OCIR_USERNAME, OCIR_PASSWORD, OCIR_REGION
  - **Spec Ref**: FR-038
  - **Verification**: GitHub repository Settings → Secrets shows 3 secrets configured
  - **Files**: None (GitHub UI)

### Build and Push Images Workflow

- [ ] T109 [US7] [Cloud] Create GitHub Actions workflow for Docker image build and push in .github/workflows/build-and-push-images.yaml
  - **Spec Ref**: FR-038
  - **Verification**: Workflow runs on push to main, builds backend and frontend images, pushes to OCIR
  - **Files**: `.github/workflows/build-and-push-images.yaml`

### Kubernetes Deployment Workflow

- [ ] T110 [US7] [Cloud] Create GitHub Actions workflow for OKE deployment in .github/workflows/deploy-oke-production.yaml with Helm deployment steps
  - **Spec Ref**: FR-038, FR-039
  - **Verification**: Workflow deploys to OKE via `helm upgrade --install todo-app ... -f values-oke.yaml`, waits for rollout, runs health checks
  - **Files**: `.github/workflows/deploy-oke-production.yaml`

### Health Check and Rollback Workflow

- [ ] T111 [US7] [Cloud] Add health check stage to deployment workflow: `kubectl wait --for=condition=Ready pods -l app=backend --timeout=120s`
  - **Spec Ref**: FR-039, SC-006
  - **Verification**: Workflow fails if pods not ready within 120s, triggers rollback
  - **Files**: `.github/workflows/deploy-oke-production.yaml` (add health check step)

- [ ] T112 [US7] [Cloud] Add automated rollback stage to deployment workflow: `helm rollback todo-app` if health checks fail
  - **Spec Ref**: FR-039
  - **Verification**: Simulate failed deployment, workflow triggers rollback to previous revision
  - **Files**: `.github/workflows/deploy-oke-production.yaml` (add rollback step)

### Integration Test Workflow

- [ ] T113 [US7] [Cloud] Create GitHub Actions workflow for event flow integration tests in .github/workflows/test-event-flows.yaml
  - **Spec Ref**: FR-038
  - **Verification**: Workflow runs integration tests from backend/tests/integration/, publishes results
  - **Files**: `.github/workflows/test-event-flows.yaml`

**Checkpoint**: CI/CD pipeline is complete, can build images and deploy to OKE with automated health checks and rollback

---

## Phase 12: Observability Setup (Prometheus + Grafana)

**Purpose**: Deploy monitoring and logging infrastructure for production
**Target**: Cloud (OKE)
**Category**: Monitoring and Logging

### Prometheus Deployment

- [ ] T114 [US8] [Cloud] Deploy Prometheus on OKE via Helm with Dapr metrics scraping: `helm install prometheus prometheus-community/prometheus`
  - **Spec Ref**: FR-041
  - **Verification**: `kubectl get pods | grep prometheus` shows Prometheus server Running, Prometheus UI shows Dapr targets
  - **Files**: `monitoring/prometheus-values.yaml` (Prometheus Helm values)

- [ ] T115 [US8] [Cloud] Configure Prometheus to scrape Dapr sidecar metrics endpoints (:9090/metrics) via ServiceMonitor CRD
  - **Spec Ref**: FR-044
  - **Verification**: Prometheus UI → Targets shows daprd endpoints UP
  - **Files**: `monitoring/servicemonitor-dapr.yaml`

### Grafana Deployment

- [ ] T116 [US8] [Cloud] Deploy Grafana on OKE via Helm: `helm install grafana grafana/grafana`
  - **Spec Ref**: FR-042
  - **Verification**: `kubectl get pods | grep grafana` shows Grafana Running, Grafana UI accessible
  - **Files**: `monitoring/grafana-values.yaml` (Grafana Helm values)

- [ ] T117 [US8] [Cloud] Import Dapr Grafana dashboards from https://github.com/dapr/dapr/tree/master/grafana into Grafana instance
  - **Spec Ref**: FR-042, FR-044
  - **Verification**: Grafana UI shows Dapr System Dashboard, Dapr Services Dashboard, Dapr Actor Dashboard
  - **Files**: `monitoring/grafana-dashboards/` (JSON dashboard definitions)

### Custom Metrics and Dashboards

- [ ] T118 [US8] [Cloud] Create custom Grafana dashboard for event flow metrics: pub/sub lag, event throughput, error rates
  - **Spec Ref**: FR-042, FR-044
  - **Verification**: Grafana dashboard shows metrics for all 4 Kafka topics (todo-created, todo-updated, todo-deleted, todo-reminder)
  - **Files**: `monitoring/grafana-dashboards/event-flows.json`

- [ ] T119 [US8] [Cloud] Create custom Grafana dashboard for task service metrics: task CRUD rates, State Store latency, concurrency conflicts
  - **Spec Ref**: FR-042
  - **Verification**: Grafana dashboard shows task creation rate, State Store get/set latency, ETag conflict rate
  - **Files**: `monitoring/grafana-dashboards/task-service.json`

### Log Aggregation

- [ ] T120 [US8] [Cloud] Deploy Fluent Bit on OKE as DaemonSet to collect logs from all pods: `helm install fluent-bit fluent/fluent-bit`
  - **Spec Ref**: FR-043
  - **Verification**: `kubectl get pods -n logging | grep fluent-bit` shows DaemonSet running on all nodes
  - **Files**: `monitoring/fluent-bit-values.yaml` (Fluent Bit Helm values)

- [ ] T121 [US8] [Cloud] Configure Fluent Bit to forward logs to OCI Logging or centralized log backend
  - **Spec Ref**: FR-043
  - **Verification**: Log backend shows logs from backend and frontend services
  - **Files**: `monitoring/fluent-bit-values.yaml` (add output configuration)

**Checkpoint**: Observability stack is deployed, Prometheus metrics and Grafana dashboards are available, logs are centralized

---

## Phase 13: Documentation

**Purpose**: Create comprehensive documentation for Phase V
**Target**: Both (Local + Cloud)
**Category**: Documentation

### Architecture Documentation

- [ ] T122 [P] [Both] Create event architecture diagram in docs/event-architecture.md with Kafka topics, Dapr components, service interactions
  - **Verification**: Diagram shows all 4 event types, producers, consumers, Kafka partitions
  - **Files**: `docs/event-architecture.md`

- [ ] T123 [P] [Both] Document Dapr component configuration in docs/dapr-components.md with Pub/Sub, State Store, Secrets, Jobs API examples
  - **Verification**: Documentation includes YAML examples for all components
  - **Files**: `docs/dapr-components.md`

- [ ] T124 [P] [Both] Document Kafka topic schemas and conventions in docs/kafka-topics.md with retention policies and partition strategies
  - **Verification**: Documentation includes topic configuration and event schema references
  - **Files**: `docs/kafka-topics.md`

### Deployment Documentation

- [ ] T125 [Both] Document OKE cluster provisioning and deployment in docs/oke-deployment.md with step-by-step instructions
  - **Verification**: Documentation covers OCI setup, OKE provisioning, managed Kafka configuration, CI/CD setup
  - **Files**: `docs/oke-deployment.md`

- [ ] T126 [Both] Document local development guide in docs/local-development.md with Minikube setup, debugging tips, troubleshooting
  - **Verification**: Documentation covers Minikube installation, Dapr CLI usage, event flow debugging
  - **Files**: `docs/local-development.md`

**Checkpoint**: All documentation is complete and up-to-date

---

## Phase 14: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation across all features
**Target**: Both (Local + Cloud)

### Final Validation

- [ ] T127 [US6] [Local] Run complete quickstart.md validation on fresh Minikube cluster
  - **Spec Ref**: SC-005
  - **Verification**: Follow quickstart.md step-by-step, confirm deployment completes in under 10 minutes, all event flows work
  - **Files**: None (manual validation)

- [ ] T128 [US7] [Cloud] Validate production deployment on OKE with 100 concurrent task operations
  - **Spec Ref**: SC-002, SC-004, SC-006
  - **Verification**: Load test with 100 concurrent users, confirm no event loss/duplication, deployment completes in under 15 minutes
  - **Files**: `backend/tests/load/test_concurrent_operations.py`

### Performance Optimization

- [ ] T129 [Both] Optimize State Store queries in backend/src/dapr/state.py with bulk operations and caching
  - **Spec Ref**: SC-011
  - **Verification**: Search query latency < 1 second for 1000 tasks
  - **Files**: `backend/src/dapr/state.py` (add bulk get/set methods)

### Security Hardening

- [ ] T130 [Both] Validate all secrets are retrieved via Dapr Secrets API and none are hardcoded
  - **Spec Ref**: FR-046, FR-047
  - **Verification**: Code review confirms no hardcoded credentials, all secrets retrieved at runtime
  - **Files**: None (code review)

- [ ] T131 [Cloud] Enable Dapr mTLS for service-to-service communication in production
  - **Spec Ref**: FR-034 (production security)
  - **Verification**: Dapr sidecar logs show mTLS enabled, traffic encrypted
  - **Files**: `dapr/components/` (add mTLS configuration)

### Final Integration Tests

- [ ] T132 [Both] Run full test suite: unit tests, integration tests, contract tests, e2e tests
  - **Spec Ref**: SC-013
  - **Verification**: All tests pass, 95%+ code coverage
  - **Files**: None (test execution)

**Checkpoint**: Phase V is complete, all quality gates passed, ready for production

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Infrastructure Setup - Local)**: No dependencies - start immediately after Minikube is running
- **Phase 2 (Dapr Components - Local)**: Depends on Phase 1 completion (Kafka cluster and Dapr control plane must be deployed)
- **Phase 3 (Backend Implementation)**: Depends on Phase 2 completion (Dapr components must be configured)
- **Phase 4 (Backend Business Logic)**: Depends on Phase 3 completion (Dapr client wrappers must exist)
- **Phase 5 (Backend API)**: Depends on Phase 4 completion (services must exist)
- **Phase 6 (Frontend Implementation)**: Can start in parallel with Phase 4/5, depends on Phase 3 (Dapr service invocation client needed)
- **Phase 7 (Helm Charts - Local)**: Depends on Phase 5 and Phase 6 completion (backend and frontend code must exist)
- **Phase 8 (Local Validation)**: Depends on Phase 7 completion (Helm chart must exist)
- **Phase 9 (Cloud Infrastructure)**: Can start in parallel with Phase 1-8, no code dependencies
- **Phase 10 (Helm Charts - Cloud)**: Depends on Phase 7 completion (extends local Helm chart)
- **Phase 11 (CI/CD)**: Depends on Phase 9 and Phase 10 completion (OKE cluster and Helm chart must exist)
- **Phase 12 (Observability)**: Depends on Phase 9 completion (OKE cluster must exist), can run in parallel with Phase 11
- **Phase 13 (Documentation)**: Can run in parallel with all phases, should be completed before Phase 14
- **Phase 14 (Polish)**: Depends on all previous phases completion

### User Story Dependencies

- **US1 (Event-Driven CRUD)**: No dependencies - foundational feature
- **US2 (Reminders)**: Depends on US1 (task management must exist)
- **US3 (Priorities & Tags)**: Depends on US1 (task management must exist)
- **US4 (Search & Sort)**: Depends on US1 and US3 (tasks with priorities/tags must exist)
- **US5 (Recurring Tasks)**: Depends on US1 and US2 (task management and reminder scheduling must exist)
- **US6 (Local Deployment)**: Depends on US1 completion (core functionality must work)
- **US7 (Cloud Deployment)**: Depends on US6 completion (local deployment must be validated first)
- **US8 (Monitoring)**: Depends on US7 completion (production deployment must exist)

### Parallel Opportunities

- All tasks marked **[P]** can run in parallel within their phase
- Phase 3, 4, 5 tasks can be parallelized by user story (e.g., different developers work on US1, US2, US3)
- Phase 6 (Frontend) can run in parallel with Phase 4 and 5 (Backend)
- Phase 9 (Cloud Infrastructure) can start independently while local development continues
- Phase 13 (Documentation) can run continuously in parallel with implementation

---

## Implementation Strategy

### MVP First (US1 + US6 Only)

1. Complete Phase 1: Kafka and Dapr on Minikube
2. Complete Phase 2: Dapr components
3. Complete Phase 3-5: Backend for US1 only (event-driven CRUD)
4. Complete Phase 6: Frontend for US1 only
5. Complete Phase 7-8: Local deployment and validation
6. **STOP and VALIDATE**: Test US1 end-to-end on Minikube
7. Deploy/demo if ready

### Incremental Delivery (Priority Order)

1. US1 + US6 → MVP (event-driven CRUD on Minikube)
2. US2 → Add reminders with Dapr Jobs API
3. US3 → Add priorities and tags
4. US7 → Deploy to OKE with CI/CD
5. US4 → Add search and sort
6. US8 → Add observability
7. US5 → Add recurring tasks

### Parallel Team Strategy

With multiple developers:

1. **Team 1**: Phase 1-2 (Infrastructure setup)
2. Once Phase 2 completes:
   - **Developer A**: Phase 3-5 (Backend US1)
   - **Developer B**: Phase 6 (Frontend US1)
   - **Developer C**: Phase 9 (Cloud infrastructure)
3. Phase 8 (Local validation) after Developer A and B complete
4. Phase 10-11 (Cloud deployment) after Developer C completes
5. **Team 2**: Phase 3-5 (Backend US2, US3, US4, US5) in parallel with Team 1 completing US1
6. **Developer D**: Phase 12 (Observability) after cloud deployment works
7. **Developer E**: Phase 13 (Documentation) continuously

---

## Notes

- **[P]** tasks can run in parallel (different files, no shared state)
- **[Story]** label maps task to user story for traceability
- **[Target]** indicates whether task applies to Local (Minikube), Cloud (OKE), or Both
- All event-driven tasks require idempotency testing (duplicate event handling)
- All Dapr component tasks require component validation via `kubectl get component`
- All Helm chart tasks require `helm lint` validation
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
- Avoid: vague tasks, same file conflicts, skipping event schema validation

---

## Task Summary

**Total Tasks**: 132
**Phases**: 14
**User Stories**: 8
**Categories**: Kafka Infrastructure, Dapr Components, Backend Implementation, Frontend Implementation, Minikube Deployment, Cloud Deployment, CI/CD Setup, Monitoring and Logging, Documentation

**Estimated Effort** (by phase):
- Phase 1: 6 tasks (~2 hours)
- Phase 2: 7 tasks (~2 hours)
- Phase 3: 14 tasks (~8 hours)
- Phase 4: 14 tasks (~8 hours)
- Phase 5: 9 tasks (~4 hours)
- Phase 6: 14 tasks (~8 hours)
- Phase 7: 11 tasks (~4 hours)
- Phase 8: 9 tasks (~4 hours)
- Phase 9: 7 tasks (~4 hours)
- Phase 10: 7 tasks (~3 hours)
- Phase 11: 6 tasks (~3 hours)
- Phase 12: 8 tasks (~4 hours)
- Phase 13: 5 tasks (~2 hours)
- Phase 14: 5 tasks (~2 hours)

**Total Estimated Effort**: ~58 hours (single developer, sequential)
**Parallel Execution**: ~20-25 hours (3-4 developers)

**Critical Path**: Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 7 → Phase 8 (local validation)
**Critical Path Duration**: ~32 hours (blocks all other work)

---

**Tasks Status**: Ready for implementation via `/sp.implement`
**Last Updated**: 2026-01-27

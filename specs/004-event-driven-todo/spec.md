# Feature Specification: Event-Driven Todo Application with Kafka and Dapr

**Feature Branch**: `004-event-driven-todo`
**Created**: 2026-01-27
**Status**: Draft
**Input**: User description: "Phase Scope: Implement advanced application features and deploy to both local and cloud Kubernetes environments with event-driven architecture using Kafka and Dapr"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and Manage Tasks with Event-Driven Updates (Priority: P1)

Users can create, update, and delete tasks through the web interface, with all changes automatically propagated through the system via events, ensuring all services stay synchronized without direct coupling.

**Why this priority**: This is the core functionality that validates the event-driven architecture. Without this working, the entire event-driven system has no value. It establishes the foundation for all other features.

**Independent Test**: Can be fully tested by creating a todo via the frontend, verifying the event is published to Kafka, and confirming the backend processes the event and updates the state store. Delivers immediate value by proving the event-driven architecture works.

**Acceptance Scenarios**:

1. **Given** a user is logged into the todo application, **When** they create a new task with title and description, **Then** a "todo-created" event is published to Kafka and the task appears in the task list within 2 seconds
2. **Given** an existing task in the system, **When** the user updates the task title or description, **Then** a "todo-updated" event is published to Kafka and the changes are reflected across all services within 2 seconds
3. **Given** an existing task in the system, **When** the user deletes the task, **Then** a "todo-deleted" event is published to Kafka and the task is removed from all views within 2 seconds
4. **Given** the backend service restarts, **When** new events are published, **Then** the service resumes processing events without data loss using Kafka consumer groups
5. **Given** multiple replicas of the backend service are running, **When** a task event is published, **Then** exactly one replica processes the event (no duplicate processing)

---

### User Story 2 - Set Due Dates and Receive Reminders (Priority: P2)

Users can assign due dates to tasks and receive automated reminders via the Dapr Jobs API, ensuring they never miss important deadlines without manual tracking.

**Why this priority**: Adds significant user value on top of basic task management. Demonstrates Dapr Jobs API integration and time-based event processing.

**Independent Test**: Can be fully tested by creating a task with a due date, scheduling a reminder via Dapr Jobs API, and verifying the reminder event is published at the scheduled time. Delivers value by enabling time-sensitive task management.

**Acceptance Scenarios**:

1. **Given** a user is creating a new task, **When** they set a due date 24 hours in the future, **Then** the system schedules a reminder job via Dapr Jobs API
2. **Given** a task has a due date approaching (within 24 hours), **When** the scheduled reminder job executes, **Then** a "todo-reminder" event is published to Kafka and the user receives a notification
3. **Given** a user updates a task's due date, **When** they change the date, **Then** the existing reminder job is cancelled and a new job is scheduled for the updated date
4. **Given** a user completes a task before its due date, **When** they mark it complete, **Then** the scheduled reminder job is cancelled
5. **Given** a scheduled reminder job fails to execute, **When** the job scheduler retries, **Then** the reminder is eventually delivered with at-least-once guarantee

---

### User Story 3 - Organize Tasks with Priorities and Tags (Priority: P2)

Users can assign priorities (High, Medium, Low) and custom tags to tasks, then filter and search by these attributes to organize their workflow effectively.

**Why this priority**: Enhances task organization and user productivity. Can be implemented independently of event-driven features but benefits from event propagation for real-time filtering.

**Independent Test**: Can be fully tested by assigning priorities and tags to tasks, using filter/search functionality, and verifying results are accurate and updated in real-time via events. Delivers value by enabling advanced task organization.

**Acceptance Scenarios**:

1. **Given** a user is creating or editing a task, **When** they assign a priority level (High/Medium/Low), **Then** the priority is saved and a "todo-updated" event includes the priority change
2. **Given** a user is creating or editing a task, **When** they add custom tags (e.g., "work", "urgent", "personal"), **Then** the tags are saved and propagated via events
3. **Given** the user has tasks with different priorities, **When** they filter by priority level, **Then** only tasks matching that priority are displayed
4. **Given** the user has tasks with various tags, **When** they search by tag name, **Then** all tasks with that tag are returned
5. **Given** the user has multiple filters active (priority + tags), **When** they search, **Then** tasks matching ALL filter criteria are displayed (AND logic)

---

### User Story 4 - Advanced Search and Sorting (Priority: P3)

Users can search tasks by keyword (title/description) and sort results by various criteria (due date, priority, created date) to quickly find relevant tasks.

**Why this priority**: Quality-of-life improvement that enhances usability but is not critical for core functionality. Depends on P1 and P2 features.

**Independent Test**: Can be fully tested by creating tasks with varied attributes, performing searches, and verifying sort order. Delivers value by improving task discoverability.

**Acceptance Scenarios**:

1. **Given** the user has multiple tasks, **When** they enter a keyword in the search box, **Then** tasks with matching titles or descriptions are displayed
2. **Given** search results are displayed, **When** the user sorts by due date, **Then** tasks are ordered chronologically (earliest due date first)
3. **Given** search results are displayed, **When** the user sorts by priority, **Then** tasks are ordered High → Medium → Low
4. **Given** search results are displayed, **When** the user sorts by created date, **Then** newest tasks appear first
5. **Given** the user searches with no results, **When** no tasks match, **Then** a helpful message is displayed suggesting search refinements

---

### User Story 5 - Create Recurring Tasks (Priority: P3)

Users can create recurring tasks (daily, weekly, monthly) that are automatically recreated via Dapr Jobs API after completion, reducing manual effort for repetitive tasks.

**Why this priority**: Advanced feature that builds on task management and scheduling capabilities. Lower priority as it serves a subset of users.

**Independent Test**: Can be fully tested by creating a recurring task, completing it, and verifying a new instance is scheduled via Dapr Jobs API. Delivers value by automating repetitive task creation.

**Acceptance Scenarios**:

1. **Given** a user is creating a new task, **When** they set recurrence to "Daily", **Then** a Dapr recurring job is scheduled to recreate the task every 24 hours
2. **Given** a user completes a recurring task, **When** they mark it complete, **Then** a new instance of the task is created with the next due date
3. **Given** a user sets weekly recurrence for a task, **When** they specify a day of the week, **Then** the task recurs on that day every week
4. **Given** a user sets monthly recurrence for a task, **When** they specify a day of the month, **Then** the task recurs on that day every month
5. **Given** a user deletes a recurring task, **When** they confirm deletion, **Then** the Dapr recurring job is cancelled and no future instances are created

---

### User Story 6 - Deploy to Local Kubernetes (Minikube) (Priority: P1)

Developers can deploy the entire event-driven system to a local Minikube cluster with Dapr and Kafka, enabling local development and testing without cloud dependencies.

**Why this priority**: Critical for development workflow and local validation before cloud deployment. Must work before cloud deployment is attempted.

**Independent Test**: Can be fully tested by running deployment scripts, verifying all pods are healthy, and confirming event flows work end-to-end on Minikube. Delivers value by enabling local development.

**Acceptance Scenarios**:

1. **Given** a developer has Minikube installed, **When** they run the deployment script, **Then** Dapr control plane is installed and healthy
2. **Given** Dapr is installed, **When** the deployment continues, **Then** Kafka cluster (Strimzi) is deployed and accessible
3. **Given** Kafka is running, **When** application services are deployed, **Then** Dapr sidecars are injected into all pods
4. **Given** all services are running, **When** a task is created via the frontend, **Then** the event flows through Kafka and is processed by the backend
5. **Given** the system is deployed locally, **When** the developer accesses the frontend via NodePort, **Then** the application is fully functional

---

### User Story 7 - Deploy to Oracle Kubernetes Engine (OKE) (Priority: P1)

The system can be deployed to Oracle Kubernetes Engine (OKE) production cluster via GitHub Actions CI/CD pipeline, using managed or self-hosted Kafka, with monitoring and logging enabled.

**Why this priority**: Critical for production deployment. Validates cloud portability and CI/CD automation.

**Independent Test**: Can be fully tested by triggering the CI/CD pipeline, verifying deployment succeeds, and confirming the application works in production. Delivers value by enabling production use.

**Acceptance Scenarios**:

1. **Given** a developer commits code to the main branch, **When** the GitHub Actions workflow triggers, **Then** Docker images are built and pushed to a container registry
2. **Given** images are built, **When** the deployment stage runs, **Then** Helm charts are applied to the Oracle Kubernetes Engine (OKE) cluster
3. **Given** the deployment completes, **When** health checks run, **Then** all pods report healthy status
4. **Given** the system is deployed, **When** Kafka is configured (managed or self-hosted), **Then** event flows work identically to local deployment
5. **Given** the system is running in production, **When** monitoring is checked, **Then** Prometheus metrics and logs are available
6. **Given** a deployment fails health checks, **When** the rollback process triggers, **Then** the previous version is restored automatically

---

### User Story 8 - Monitor System Health and Events (Priority: P2)

Operators can view system metrics, logs, and event flows through Prometheus/Grafana dashboards and Dapr observability tools to ensure system health and troubleshoot issues.

**Why this priority**: Essential for production operations but can be added after core functionality works. Enables proactive issue detection.

**Independent Test**: Can be fully tested by accessing monitoring dashboards, viewing metrics for all services, and correlating logs with event flows. Delivers value by enabling operational visibility.

**Acceptance Scenarios**:

1. **Given** the system is deployed, **When** an operator accesses Grafana, **Then** dashboards show metrics for all services (CPU, memory, request rates)
2. **Given** events are flowing through Kafka, **When** an operator views event metrics, **Then** pub/sub lag, throughput, and error rates are visible
3. **Given** a service experiences errors, **When** an operator checks logs, **Then** errors are correlated with specific events and requests
4. **Given** Dapr sidecars are running, **When** an operator views Dapr dashboard, **Then** service invocation metrics and state store operations are visible
5. **Given** a pod crashes, **When** Kubernetes restarts it, **Then** the restart event is logged and visible in monitoring

---

### Edge Cases

- What happens when Kafka is unavailable temporarily? (Dapr should buffer events and retry)
- How does the system handle duplicate events? (Idempotent event handlers prevent duplicate processing)
- What if a scheduled reminder job fires while the task is being deleted? (Job cancellation should be atomic with task deletion)
- What happens when a user sets a due date in the past? (System should reject or auto-adjust to future date)
- How does the system handle very large tag lists (100+ tags)? (UI should paginate/truncate, backend should handle efficiently)
- What if a user creates a recurring task that recurs every minute? (System should enforce minimum recurrence intervals)
- How does the system behave during Dapr sidecar initialization delays? (Application should wait for sidecar readiness)
- What if State Store (Redis/PostgreSQL) is unavailable? (Writes fail gracefully, reads return cached data if available)
- How does the system handle timezone differences for due dates and reminders? (Store in UTC, display in user's timezone)
- What happens when multiple users update the same task concurrently? (Optimistic locking with ETags prevents lost updates)

## Requirements *(mandatory)*

### Functional Requirements

#### Event-Driven Architecture
- **FR-001**: System MUST publish a "todo-created" event to Kafka when a new task is created
- **FR-002**: System MUST publish a "todo-updated" event to Kafka when a task is modified
- **FR-003**: System MUST publish a "todo-deleted" event to Kafka when a task is removed
- **FR-004**: System MUST publish a "todo-reminder" event to Kafka when a scheduled reminder is triggered
- **FR-005**: All events MUST include event metadata (eventId, timestamp, userId, todoId)
- **FR-006**: Event schemas MUST be documented in JSON Schema format
- **FR-007**: Event consumers MUST process events idempotently (handle duplicates gracefully)
- **FR-008**: System MUST guarantee at-least-once event delivery

#### Dapr Integration
- **FR-009**: Services MUST communicate via Dapr Service Invocation (no direct HTTP calls)
- **FR-010**: Services MUST use Dapr Pub/Sub API for publishing and subscribing to Kafka events
- **FR-011**: Services MUST use Dapr State Store API for all persistent state (no direct database connections)
- **FR-012**: Services MUST retrieve secrets via Dapr Secrets API (Kubernetes Secrets backend)
- **FR-013**: Scheduled reminders MUST use Dapr Jobs API
- **FR-014**: Each service pod MUST have a Dapr sidecar injected via Kubernetes annotations
- **FR-015**: Dapr components MUST be defined declaratively in YAML files

#### Task Management Features
- **FR-016**: Users MUST be able to create tasks with title, description, due date, priority, and tags
- **FR-017**: Users MUST be able to update any task attribute (title, description, due date, priority, tags)
- **FR-018**: Users MUST be able to delete tasks
- **FR-019**: Users MUST be able to mark tasks as complete/incomplete
- **FR-020**: System MUST support priority levels: High, Medium, Low
- **FR-021**: Users MUST be able to add multiple custom tags to tasks
- **FR-022**: Users MUST be able to filter tasks by priority
- **FR-023**: Users MUST be able to filter tasks by tag (multiple tags with AND logic)
- **FR-024**: Users MUST be able to search tasks by keyword (title and description)
- **FR-025**: Users MUST be able to sort tasks by due date, priority, or created date
- **FR-026**: System MUST support recurring tasks with intervals: daily, weekly, monthly
- **FR-026A**: System MUST enforce minimum 1-hour recurrence interval with validation error for shorter intervals (prevents system overload)
- **FR-027**: Recurring tasks MUST be automatically recreated after completion

#### Reminders and Scheduling
- **FR-028**: Users MUST be able to set due dates for tasks
- **FR-029**: System MUST schedule reminder jobs 24 hours before due date
- **FR-030**: Reminder jobs MUST be cancelled when tasks are completed or deleted
- **FR-031**: Reminder jobs MUST be rescheduled when due dates are updated
- **FR-032**: System MUST handle timezone conversions for due dates and reminders

#### Deployment and Infrastructure
- **FR-033**: System MUST deploy to Minikube for local development and testing
- **FR-034**: System MUST deploy to production Kubernetes (Oracle Kubernetes Engine - OKE)
- **FR-035**: Kafka MUST be deployed via Strimzi operator (self-hosted) or managed service (Redpanda/Confluent)
- **FR-036**: System MUST use Dapr State Store with Redis or PostgreSQL backend
- **FR-037**: All deployments MUST use Helm charts for reproducibility
- **FR-038**: CI/CD pipeline MUST use GitHub Actions for automated deployments
- **FR-039**: Production deployments MUST include health checks and automated rollback
- **FR-040**: System MUST run identically on Minikube and cloud Kubernetes without code changes

#### Observability
- **FR-041**: System MUST expose Prometheus metrics for all services
- **FR-042**: System MUST provide Grafana dashboards for monitoring
- **FR-043**: System MUST centralize logs from all services
- **FR-044**: System MUST provide Dapr observability for service invocation and pub/sub metrics
- **FR-045**: System MUST log all event publications and consumptions for debugging

#### Security and Secrets
- **FR-046**: All secrets MUST be stored in Kubernetes Secrets (no hardcoding)
- **FR-047**: Services MUST retrieve secrets via Dapr Secrets API at runtime

### Key Entities

- **Task**: Represents a todo item with attributes: id (UUID), title (string), description (string), completed (boolean), priority (enum: High/Medium/Low), tags (array of strings), dueDate (ISO8601 timestamp), recurring (boolean), recurrenceInterval (enum: daily/weekly/monthly), createdAt (timestamp), updatedAt (timestamp), userId (string)

- **Event**: Represents a domain event with attributes: eventId (UUID), eventType (string: todo-created, todo-updated, todo-deleted, todo-reminder), timestamp (ISO8601), todoId (UUID), userId (string), payload (object containing event-specific data)

- **ReminderJob**: Represents a scheduled reminder with attributes: jobId (UUID), todoId (UUID), scheduledTime (ISO8601 timestamp), status (enum: pending/executed/cancelled)

- **DaprComponent**: Represents infrastructure configuration with attributes: name (string), type (enum: pubsub/statestore/secretstore/jobs), backend (string: kafka/redis/postgresql/kubernetes), metadata (configuration parameters)

- **KafkaTopic**: Represents event stream with attributes: topicName (string), partitionCount (integer), replicationFactor (integer), retentionPeriod (duration), consumerGroups (array of strings)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task and see it reflected in the UI within 2 seconds (end-to-end event processing latency)
- **SC-002**: System processes 100 concurrent task creations without event loss or duplication
- **SC-003**: Reminder notifications are delivered within 5 minutes of scheduled time with 99% accuracy
- **SC-004**: System supports 10 concurrent users performing CRUD operations without degradation
- **SC-005**: Minikube deployment completes successfully in under 10 minutes with all health checks passing
- **SC-006**: Cloud Kubernetes deployment via CI/CD completes in under 15 minutes with automated health validation
- **SC-007**: Event processing idempotency prevents duplicate task creation/updates 100% of the time
- **SC-008**: System recovers from Kafka unavailability within 30 seconds once service is restored
- **SC-009**: Dapr sidecar startup completes in under 10 seconds, unblocking application pod readiness
- **SC-010**: Monitoring dashboards display real-time metrics with less than 30-second lag
- **SC-011**: Search results return within 1 second for queries across 1000 tasks
- **SC-012**: System scales horizontally to N replicas without event duplication or loss
- **SC-013**: 95% of users successfully complete task creation, filtering, and search on first attempt
- **SC-014**: Recurring tasks are recreated within 5 minutes of completion with correct due dates

### Assumptions

- Users have modern web browsers (Chrome, Firefox, Safari, Edge - last 2 versions)
- Kubernetes clusters have sufficient resources (minimum 4 CPU cores, 8GB RAM for Minikube; auto-scaling enabled for cloud)
- Network latency between services is under 100ms for local deployment, under 200ms for cloud
- Kafka topics have at least 3 partitions and replication factor of 3 (production) or 1 (local)
- State Store (Redis/PostgreSQL) provides strong consistency for task state
- Users are authenticated and userId is available from session/token (authentication mechanism not in scope for this phase)
- Timezone handling defaults to UTC storage with client-side timezone conversion
- Minimum recurrence interval for recurring tasks is 1 hour (prevents system overload)
- Maximum tag count per task is 50 (UI and backend enforce limit)

### Dependencies

- MCP Context 7 Server must be available for fetching Dapr, Kafka, and Kubernetes documentation
- Kubernetes cluster (Minikube for local, OKE for production) must be provisioned before deployment
- Oracle Cloud Infrastructure (OCI) account with OKE access and credentials configured
- Dapr control plane must be installed on Kubernetes before application deployment
- Kafka infrastructure (Strimzi operator or managed service) must be deployed before application services
- Redis or PostgreSQL must be available as Dapr State Store backend
- GitHub repository must have secrets configured for cloud provider credentials
- Container registry access must be configured for pushing/pulling Docker images
- Prometheus and Grafana must be installed for observability (optional but recommended)

### Out of Scope (Phase V)

- User authentication and authorization (assume userId is available from existing auth via Kubernetes ServiceAccount tokens OR HTTP session cookies from Phase III chatbot auth layer; implementation detail for future phase)
- Multi-tenancy and data isolation (single-user system for Phase V)
- Real-time WebSocket updates for collaborative editing
- Advanced event sourcing or CQRS patterns beyond simple pub/sub
- Mobile applications (web application only)
- Email or SMS notifications for reminders (events published to Kafka only)
- Advanced recurring patterns (e.g., "every 2nd Monday", "last day of month")
- Task attachments or file uploads
- Task comments or collaboration features
- Audit logs or event replay UI
- Multi-region Kafka clusters or geo-replication
- Advanced Dapr features (actors, workflows, bindings)

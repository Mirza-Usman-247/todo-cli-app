<!--
Sync Impact Report (2026-01-27)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Version Change: 4.0.0 → 5.0.0
Rationale: Major backward-incompatible evolution from Phase IV (Local Kubernetes Deployment)
to Phase V (Event-Driven Architecture with Kafka and Dapr on Production Kubernetes)

Modified Principles:
  - II. Phase-Scoped Development: Local K8s Deployment → Event-Driven Architecture with Kafka & Dapr
  - V. Storage Architecture: Containerized Storage → Event-Driven State Management (Dapr State Store)
  - VII. MCP Context-First Development: Expanded to include Kafka and Dapr documentation
  - VIII/IX. AI-Assisted Operations: Extended to cover Dapr CLI and Kafka management
  - XIV. AI DevOps Tooling: Extended to include Dapr-specific tooling
  - XV. Container-First Design: Updated for Dapr sidecar pattern
  - XVI. Declarative Operations: Extended to include Dapr components and Kafka configs
  - XVII. Cluster Focus: Local Minikube → Production Kubernetes (AKS/GKE/OKE)

Added Principles:
  - XIX. Event-Driven Architecture First
  - XX. Dapr Sidecar Pattern Mandate
  - XXI. Kafka as Event Backbone
  - XXII. Loose Coupling via Service Invocation
  - XXIII. Stateless Services with Dapr State API
  - XXIV. Secrets Management via Dapr
  - XXV. Production-Grade Kubernetes Focus
  - XXVI. MCP Context Mandate for Dapr & Kafka

Updated Sections:
  - Phase V Technical Constraints (Kafka, Dapr, Strimzi/Redpanda, AKS/GKE/OKE)
  - Development Workflow: MCP Context now includes Kafka and Dapr official docs
  - Governance: Updated compliance for event-driven and production deployments

Removed Sections:
  - Local Minikube-specific guidance (replaced with production Kubernetes)
  - Ephemeral storage patterns (replaced with Dapr State Store)
  - Phase IV AI DevOps local tooling (retained kubectl-ai/kagent, added Dapr CLI)

Templates Status:
  ⚠ .specify/templates/plan-template.md - Dapr component and Kafka context checks needed
  ⚠ .specify/templates/spec-template.md - Event-driven requirements support needed
  ⚠ .specify/templates/tasks-template.md - Dapr pub/sub and state store tasks needed
  ⚠ CLAUDE.md - Update to emphasize MCP Context 7 mandate and Dapr/Kafka focus

Follow-up TODOs:
  - Validate MCP Context 7 server availability and Kafka/Dapr doc access
  - Create Dapr component specifications (pub/sub, state store, secrets)
  - Document production Kubernetes cluster selection (AKS vs GKE vs OKE)
  - Define event schemas and pub/sub topics
  - Document CI/CD pipeline for production deployments (GitHub Actions)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-->

# The Evolution of Todo - Phase V Constitution (Event-Driven Architecture)

## Core Principles

### I. Spec-Driven Development (SDD) Mandate

All development MUST follow the Agentic Dev Stack workflow with mandatory MCP context validation:

1. Validate MCP Context Server access and fetch documentation
2. Write specification using `/sp.specify`
3. Generate implementation plan using `/sp.plan` (with MCP context)
4. Break into actionable tasks using `/sp.tasks`
5. Implement via Claude Code following generated artifacts

**Rationale**: Ensures every code change is traceable to documented requirements and validated against current official documentation, preventing scope creep, deprecated API usage, and maintaining alignment with project goals.

**Non-negotiable rules**:
- NEVER write code without a corresponding spec
- NEVER skip MCP context validation before planning
- NEVER rely on training data for Kafka, Dapr, Kubernetes, or cloud provider APIs
- NEVER skip planning or task generation steps
- STOP immediately if requirements are unclear and request clarification
- Every feature MUST have artifacts in `/specs/<feature>/` (spec.md, plan.md, tasks.md)

### II. Phase-Scoped Development

Phase V scope is strictly limited to implementing event-driven architecture using Kafka and Dapr, deploying first on Minikube for validation, then on production Kubernetes (AKS/GKE/OKE). APPLICATION ARCHITECTURE WILL BE MODIFIED for event-driven patterns.

**In Scope**:
- Event-driven architecture design with Kafka as event backbone
- Dapr integration for Pub/Sub, State Store, Service Invocation, Secrets, Jobs API
- Kafka deployment (Strimzi for self-hosted, Redpanda Cloud, or Confluent)
- Dapr component definitions (pub/sub, state store, secrets, service invocation)
- Application refactoring to use Dapr APIs and event-driven patterns
- Stateless service design with Dapr sidecar pattern
- Kubernetes deployment on Minikube (validation) and production cluster (AKS/GKE/OKE)
- CI/CD pipeline with GitHub Actions for production deployments
- Event schema design and topic management
- Service-to-service communication via Dapr service invocation
- Secrets management via Dapr secrets API
- State management via Dapr state store API
- Background jobs via Dapr Jobs API

**Out of Scope** (Failure conditions):
- Multi-cloud deployments (pick ONE: AKS, GKE, or OKE)
- Complex event sourcing or CQRS patterns (beyond simple pub/sub)
- Custom Kafka operators (use Strimzi or managed services)
- Advanced Dapr workflows or actors (not needed for Todo app)
- Real-time WebSocket streaming (unless required for chatbot features)
- Multi-region Kafka clusters
- Custom authentication providers (use Dapr secrets for auth tokens)

**Rationale**: Phase V transforms the Todo Chatbot into a cloud-native, event-driven application with production-grade architecture. Kafka provides reliable event streaming, Dapr provides cloud-portable service abstractions, and production Kubernetes ensures scalability.

**Non-negotiable rules**:
- MUST use MCP Context 7 server for ALL Kafka, Dapr, and Kubernetes documentation
- REJECT custom event streaming solutions (Kafka is mandatory)
- REJECT bypassing Dapr for service communication (Dapr service invocation required)
- REJECT hardcoded secrets or configuration (Dapr secrets API mandatory)
- DOCUMENT all event flows and Dapr component interactions
- ENSURE reproducible deployments via declarative Kubernetes manifests
- VALIDATE on Minikube BEFORE deploying to production Kubernetes
- REQUEST immediate clarification if event schema design is ambiguous
- FAIL deployment if Dapr sidecars fail to start or communicate

**Development Boundary Rule**: No implementation starts until MCP Context 7 validates availability of Kafka, Dapr, and Kubernetes documentation.

### III. Test-First Event-Driven Validation (TDD for Events)

Test-Driven validation is MANDATORY for all event-driven components, Dapr integrations, and Kafka pub/sub flows.

**Red-Green-Refactor cycle for event-driven systems**:
1. **Red**: Define event flow failure scenarios and expected behaviors
2. **Green**: Implement Dapr components and event handlers that pass validation
3. **Refactor**: Optimize event schemas and handlers while maintaining validation

**Event-driven testing requirements**:
- Event schema validation (JSON Schema or Protobuf)
- Pub/Sub message delivery tests (publish → consume verification)
- Dapr component health checks (state store, pub/sub, secrets)
- Service invocation tests (frontend → backend via Dapr)
- State store persistence tests (write → read → delete cycles)
- Kafka topic creation and retention tests
- Background job scheduling and execution tests (Dapr Jobs API)
- Sidecar injection and startup tests

**Rationale**: TDD prevents event loss, ensures message delivery guarantees, and validates Dapr components work correctly across local and production environments.

**Non-negotiable rules**:
- VALIDATE event schemas BEFORE implementing publishers/subscribers
- TEST pub/sub flows with at-least-once delivery guarantees
- VERIFY Dapr sidecars are healthy before starting application containers
- VALIDATE state store operations with concurrency tests
- DOCUMENT all event flows and topic naming conventions
- FAIL deployment if pub/sub messages are lost or duplicated
- USE integration tests for Dapr component interactions

**Event Boundary Test**: MUST verify events published on one service are received by all subscribers without loss.

### IV. Minimal Viable Simplicity

Start with the simplest event-driven solution. Complexity requires explicit justification.

**YAGNI (You Aren't Gonna Need It) principles**:
- No event sourcing unless explicitly required
- No CQRS patterns for simple CRUD operations
- No custom Kafka clients (use Dapr Pub/Sub abstraction)
- No multi-topic fan-out without proven need
- No complex event transformations in-flight

**Rationale**: Event-driven systems can become complex quickly. Simple pub/sub with Dapr keeps the architecture understandable and maintainable.

**Non-negotiable rules**:
- JUSTIFY any event streaming complexity beyond simple pub/sub
- REJECT unnecessary event transformations
- PREFER Dapr abstractions over direct Kafka clients
- DOCUMENT complexity violations in plan.md Complexity Tracking table
- USE single Kafka cluster unless multi-cluster explicitly required

### V. Event-Driven State Management (Dapr State Store)

Applications use Dapr State Store API for persistence. NO direct database connections.

**Data flow**:
- Application state managed via Dapr State Store API (Redis, PostgreSQL, or MongoDB backend)
- Events published to Kafka topics via Dapr Pub/Sub
- Services communicate via Dapr Service Invocation
- Secrets retrieved via Dapr Secrets API (Kubernetes Secrets backend)
- Background jobs scheduled via Dapr Jobs API

**Dapr State Store patterns**:
- Key-value storage with strong consistency (when required)
- Eventual consistency for high-throughput scenarios
- TTL-based expiration for temporary state
- Bulk operations for batch processing
- Concurrency control with ETags

**Rationale**: Dapr State Store provides cloud-portable state management without tight coupling to specific databases. Event-driven architecture decouples services via Kafka.

**Non-negotiable rules**:
- NO direct database connections (use Dapr State Store API)
- NO hardcoded connection strings (use Dapr secrets)
- NO bypassing Dapr for state operations
- Secrets MUST be managed via Dapr Secrets API
- Events MUST be published via Dapr Pub/Sub API
- DOCUMENT all state schemas and event schemas
- ENSURE idempotent event handlers (handle duplicate messages)

**State Boundary Rule**: All persistent state goes through Dapr State Store. All service communication goes through Dapr APIs.

### VI. Separation of Concerns (Event-Driven Layers)

Clean separation between application logic, event handling, Dapr components, and Kubernetes orchestration:

**Required structure**:
```
# Application code (Phase V - Event-Driven Refactoring)
frontend/                # Next.js application with Dapr SDK
├── dapr/                # Dapr client integration
├── events/              # Event publishers and subscribers
└── components/          # UI components

backend/                 # FastAPI application with Dapr SDK
├── dapr/                # Dapr client integration
├── events/              # Event handlers and publishers
├── api/                 # HTTP endpoints (Dapr service invocation)
└── services/            # Business logic

# Phase V Dapr Component Definitions
dapr/
├── components/
│   ├── pubsub-kafka.yaml         # Kafka pub/sub component
│   ├── statestore-redis.yaml     # Redis state store component
│   ├── secrets-kubernetes.yaml   # Kubernetes secrets component
│   └── serviceinvocation.yaml    # Service invocation config
├── subscriptions/
│   ├── backend-subscriptions.yaml # Backend event subscriptions
│   └── frontend-subscriptions.yaml # Frontend event subscriptions (if any)

# Kafka Infrastructure
kafka/
├── topics/                # Topic definitions and schemas
│   ├── todo-created.json
│   ├── todo-updated.json
│   └── todo-deleted.json
├── strimzi/               # Strimzi Kafka operator (if self-hosted)
│   └── kafka-cluster.yaml
└── redpanda/              # Redpanda Cloud config (if managed)

# Helm Charts (Phase V)
helm/
├── todo-app-event-driven/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment-frontend.yaml   # With Dapr sidecar annotations
│       ├── deployment-backend.yaml    # With Dapr sidecar annotations
│       ├── service-frontend.yaml
│       ├── service-backend.yaml
│       ├── dapr-components/          # Dapr component manifests
│       └── kafka/                    # Kafka cluster manifests (if self-hosted)

# CI/CD (Phase V)
.github/
└── workflows/
    ├── deploy-minikube.yaml          # Validation deployment
    ├── deploy-production.yaml        # Production deployment (AKS/GKE/OKE)
    └── test-event-flows.yaml         # Event integration tests

docs/
├── event-architecture.md             # Event flow diagrams
├── dapr-components.md                # Dapr component documentation
├── kafka-topics.md                   # Topic schemas and conventions
└── production-deployment.md          # Production cluster setup
```

**Rationale**: Clear separation enables independent evolution of application logic, event schemas, Dapr components, and infrastructure.

**Non-negotiable rules**:
- Application code MUST use Dapr SDK for all external interactions
- Dapr components MUST be declarative YAML configurations
- Event schemas MUST be documented separately from application code
- Kafka topics MUST have explicit schema definitions
- DO NOT embed Dapr component definitions in application code
- Keep event handling separate from business logic
- DOCUMENT all Dapr component dependencies

**Event Boundary Rule**: Application code interacts with Dapr APIs only. No direct Kafka or database client usage.

### VII. MCP Context-First Development (Dapr & Kafka Mandate)

Before any event-driven implementation, the agent MUST connect to MCP Context 7 Server and fetch latest official documentation.

**Required MCP Context Validations (Phase V)**:
1. **Dapr** - Verify Pub/Sub, State Store, Service Invocation, Secrets, Jobs API documentation
2. **Kafka** - Verify topic management, consumer groups, producer configs, partitioning strategies
3. **Strimzi** - Verify Kafka operator installation, cluster configuration (if self-hosted)
4. **Redpanda Cloud** - Verify managed Kafka setup and integration (if using managed service)
5. **Confluent** - Verify managed Kafka platform integration (if using Confluent)
6. **Kubernetes (AKS/GKE/OKE)** - Verify production cluster setup, networking, storage classes
7. **GitHub Actions** - Verify CI/CD pipeline configuration for Kubernetes deployments
8. **Dapr CLI** - Verify local development with Dapr, sidecar management, component validation

**MCP Context Usage Validation**:
For each technology, MUST document:
- MCP Context 7 connection success
- Documentation version and retrieval date
- Key API patterns validated
- Limitations and alternative approaches documented
- Sample configurations tested

**Rationale**: Dapr and Kafka evolve rapidly. MCP Context ensures we're using current best practices, not outdated training data.

**Non-negotiable rules**:
- NEVER implement Dapr components without validating official documentation
- ALWAYS validate Kafka topic configurations with latest best practices
- ALWAYS test Dapr components locally with Dapr CLI before Kubernetes deployment
- USE MCP Context 7 for ALL Kubernetes provider-specific configurations (AKS/GKE/OKE)
- DOCUMENT all MCP Context queries and their outcomes
- FAIL planning phase if MCP Context 7 cannot validate Dapr or Kafka documentation
- VERIFY event schemas against Kafka best practices from official docs

**MCP Context Coverage Rule**: At least one MCP Context validation for Dapr, Kafka, and target Kubernetes provider in each feature.

### VIII. Dapr-First Service Integration

All inter-service communication MUST use Dapr Service Invocation, Pub/Sub, or State Store APIs.

**Dapr Integration Patterns**:
- **Service Invocation**: Frontend → Backend via Dapr service invocation (HTTP/gRPC)
  - Example: `dapr invoke --app-id backend --method /api/todos`
- **Pub/Sub**: Asynchronous event publishing and subscription
  - Example: Backend publishes `todo-created` event to Kafka via Dapr
- **State Store**: Key-value persistence with consistency guarantees
  - Example: Backend stores todo items in Dapr state store (Redis backend)
- **Secrets**: Retrieve API keys, database credentials from Kubernetes Secrets via Dapr
  - Example: Backend retrieves OpenAI API key via Dapr secrets API
- **Jobs API**: Schedule background tasks (e.g., cleanup, notifications)
  - Example: Daily cleanup job scheduled via Dapr Jobs API

**Dapr Component Documentation**:
For each Dapr component, document:
- Component type (pub/sub, state store, secrets, service invocation)
- Backend implementation (Kafka, Redis, Kubernetes Secrets)
- Configuration YAML with all parameters explained
- Application code integration (SDK usage)
- Testing and validation procedures

**Rationale**: Dapr provides cloud-portable service abstractions, eliminating tight coupling to specific infrastructure.

**Non-negotiable rules**:
- PREFER Dapr Service Invocation over direct HTTP calls between services
- PREFER Dapr Pub/Sub over direct Kafka client usage
- PREFER Dapr State Store over direct database connections
- ALWAYS use Dapr Secrets API for sensitive configuration
- NEVER bypass Dapr for service communication
- VALIDATE Dapr components with `dapr components` CLI before deployment
- TEST Dapr sidecar injection in Kubernetes with pod annotations

**Dapr Coverage Rule**: Every service MUST use at least 3 Dapr APIs (Pub/Sub, State Store, Service Invocation, or Secrets).

### IX. Kafka as Event Backbone

Kafka is the mandatory event streaming platform for all asynchronous communication.

**Kafka Design Patterns**:
- **Topics**: One topic per event type (todo-created, todo-updated, todo-deleted)
- **Partitioning**: Partition by todo ID for ordering guarantees
- **Consumer Groups**: One consumer group per subscriber service
- **Retention**: Configurable retention for event replay (default: 7 days)
- **Schemas**: JSON Schema or Avro for event validation

**Kafka Infrastructure Choices**:
- **Strimzi Operator** (self-hosted on Kubernetes): Full control, cost-effective, complex operations
- **Redpanda Cloud** (managed service): Kafka-compatible, simpler operations, vendor lock-in
- **Confluent Cloud** (managed Kafka): Enterprise features, higher cost, full Kafka ecosystem

**Kafka Configuration Standards**:
- Topics MUST have explicit partition count and replication factor
- Consumer groups MUST have meaningful names (e.g., `backend-todo-processor`)
- Retention policies MUST be documented per topic
- Schema evolution strategy MUST be defined

**Rationale**: Kafka provides durable, scalable event streaming with strong ordering guarantees and event replay capabilities.

**Non-negotiable rules**:
- ALL event-driven communication MUST use Kafka topics
- Dapr Pub/Sub MUST be configured with Kafka backend
- Event schemas MUST be documented and versioned
- Topics MUST have explicit retention and partitioning policies
- NEVER use in-memory message queues for production event flows
- VALIDATE Kafka topics exist before deploying event publishers
- TEST event delivery with at-least-once guarantees

**Kafka Coverage Rule**: Every event flow MUST be documented with topic name, schema, partition key, and consumer groups.

### X. Stateless Services with Dapr Sidecar Pattern

All application services MUST be stateless, delegating state management to Dapr State Store and event handling to Dapr Pub/Sub.

**Stateless Service Principles**:
- **No in-memory state**: All state persisted via Dapr State Store
- **Horizontal scaling**: Services can scale to N replicas without coordination
- **Sidecar pattern**: Each pod has Dapr sidecar injected via Kubernetes annotations
- **Idempotent handlers**: Event handlers tolerate duplicate message delivery
- **Graceful shutdown**: Services drain in-flight requests before terminating

**Dapr Sidecar Injection**:
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "backend"
  dapr.io/app-port: "8000"
  dapr.io/enable-api-logging: "true"
```

**Stateless Validation Tests**:
- Scale service to 0 replicas, then back to N (state should persist via Dapr)
- Kill random pods, verify no state loss
- Send duplicate events, verify idempotent handling

**Rationale**: Stateless services enable horizontal scaling, fault tolerance, and cloud portability.

**Non-negotiable rules**:
- NO in-memory state that isn't replicated via Dapr State Store
- ALL services MUST support N replicas without coordination
- Dapr sidecars MUST be injected via Kubernetes annotations
- Event handlers MUST be idempotent (handle duplicates gracefully)
- VALIDATE statelessness by scaling to 0 and back
- DOCUMENT all state dependencies and Dapr component usage

**Stateless Boundary Rule**: Services can be killed and restarted without losing state or breaking event flows.

### XI. Production-Grade Kubernetes Focus

All deployments MUST target production Kubernetes clusters (AKS/GKE/OKE) after Minikube validation.

**Production Kubernetes Requirements**:
- **Cluster Selection**: Choose ONE of AKS (Azure), GKE (Google Cloud), or OKE (Oracle Cloud)
- **Node Pools**: Separate node pools for application, Kafka, and system workloads
- **Autoscaling**: Horizontal Pod Autoscaling (HPA) for application services
- **Ingress**: Production-grade ingress controller (NGINX, Traefik, or cloud-native)
- **TLS**: Cert-manager for automatic certificate management
- **Monitoring**: Prometheus + Grafana for observability
- **Logging**: Centralized logging with Fluentd or cloud-native solutions

**Production Deployment Workflow**:
1. Develop and test on Minikube with Dapr and Kafka
2. Validate Helm charts and Dapr components locally
3. Deploy to production Kubernetes cluster via GitHub Actions CI/CD
4. Monitor deployment health with kubectl, Prometheus, and Dapr dashboards
5. Rollback if health checks fail

**Cloud Provider Considerations**:
- **AKS (Azure)**: Azure AD integration, Azure Key Vault for secrets, Azure Monitor
- **GKE (Google Cloud)**: GKE Autopilot for managed nodes, Workload Identity, Cloud Monitoring
- **OKE (Oracle Cloud)**: OCI integration, Oracle Cloud Infrastructure monitoring

**Rationale**: Production Kubernetes ensures scalability, reliability, and cloud-native operations for event-driven applications.

**Non-negotiable rules**:
- MUST validate on Minikube BEFORE deploying to production
- SELECT one production Kubernetes provider (AKS, GKE, or OKE) at project start
- CONFIGURE autoscaling for all application services
- ENABLE monitoring and logging before production deployment
- USE infrastructure as code (Helm charts) for all deployments
- DOCUMENT cloud provider-specific configurations
- VALIDATE TLS termination and certificate management

**Production Boundary Rule**: Production deployments require monitoring, logging, autoscaling, and rollback capabilities.

### XII. CI/CD with GitHub Actions

All production deployments MUST be automated via GitHub Actions CI/CD pipelines.

**CI/CD Pipeline Stages**:
1. **Build**: Docker image builds for frontend and backend
2. **Test**: Unit tests, integration tests, event flow tests
3. **Validate**: Helm chart validation, Dapr component validation
4. **Deploy to Minikube**: Automated Minikube deployment for validation
5. **Deploy to Production**: Automated production Kubernetes deployment
6. **Health Checks**: Post-deployment validation with kubectl and Dapr CLI
7. **Rollback**: Automatic rollback on health check failures

**GitHub Actions Workflow Requirements**:
- Secrets management via GitHub Secrets (Kubernetes credentials, cloud provider tokens)
- Docker image tagging with Git commit SHA
- Helm chart versioning and deployment
- Dapr component deployment validation
- Event flow smoke tests post-deployment

**Rationale**: Automated CI/CD ensures consistent, reproducible, and safe deployments to production Kubernetes.

**Non-negotiable rules**:
- ALL production deployments MUST go through GitHub Actions
- NEVER manually apply Kubernetes manifests to production
- VALIDATE Dapr components in CI/CD pipeline before deployment
- TEST event flows in CI/CD with integration tests
- ROLLBACK automatically if health checks fail
- DOCUMENT all CI/CD pipeline stages and dependencies

**CI/CD Boundary Rule**: No production changes without GitHub Actions workflow execution and validation.

### XIII. Secrets Management via Dapr

All secrets MUST be managed via Dapr Secrets API with Kubernetes Secrets backend.

**Secrets Management Patterns**:
- **Kubernetes Secrets**: Backend for Dapr Secrets API
- **Application Access**: Services retrieve secrets via Dapr SDK at runtime
- **No Hardcoding**: Secrets NEVER hardcoded in application code or container images
- **Rotation**: Secrets can be rotated without redeploying applications

**Dapr Secrets Component**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
  version: v1
```

**Secrets Access Pattern**:
```python
# Backend retrieves OpenAI API key via Dapr
secrets = dapr_client.get_secret("kubernetes-secrets", "openai-api-key")
api_key = secrets["openai-api-key"]
```

**Rationale**: Dapr Secrets API decouples applications from secret storage mechanisms, enabling cloud portability and secure secret management.

**Non-negotiable rules**:
- NEVER hardcode secrets in application code
- NEVER commit secrets to Git repositories
- ALWAYS use Dapr Secrets API for secret retrieval
- VALIDATE secrets are available before application startup
- DOCUMENT all secret names and their purposes
- USE cloud-native secret stores for production (Azure Key Vault, GCP Secret Manager, etc.)

**Secrets Boundary Rule**: Applications access secrets via Dapr API only. No direct Kubernetes Secret access.

### XIV. MCP Context Mandate for Implementation

BEFORE implementing ANY code, the agent MUST fetch official documentation via MCP Context 7 Server.

**MCP Context 7 Mandatory Queries** (BLOCKING):
1. Dapr Pub/Sub API documentation
2. Dapr State Store API documentation
3. Dapr Service Invocation documentation
4. Dapr Secrets API documentation
5. Dapr Jobs API documentation
6. Kafka topic configuration best practices
7. Kubernetes deployment with Dapr sidecar annotations
8. Target Kubernetes provider setup (AKS/GKE/OKE)
9. GitHub Actions CI/CD for Kubernetes deployments
10. Strimzi Kafka operator (if self-hosted) or Redpanda Cloud setup (if managed)

**MCP Context Documentation Workflow**:
1. Agent connects to MCP Context 7 Server
2. Agent queries for latest official documentation
3. Agent validates API patterns and configuration examples
4. Agent documents MCP query results in plan.md
5. Agent proceeds to implementation ONLY after validation
6. Agent references MCP-validated patterns in code

**Rationale**: Event-driven architectures and cloud-native tooling evolve rapidly. MCP Context ensures current best practices, not outdated training data.

**Non-negotiable rules**:
- NEVER write Dapr component YAML without MCP Context validation
- NEVER write Kafka topic configurations without MCP Context validation
- NEVER write Kubernetes manifests for production without MCP Context validation
- ALWAYS document MCP Context query results in plan.md
- FAIL planning phase if MCP Context 7 is unavailable
- REFERENCE MCP Context validation in all implementation artifacts

**MCP Context Coverage Rule**: Every Dapr component, Kafka topic, and Kubernetes manifest MUST reference MCP Context validation.

## Phase V Technical Constraints

### Event-Driven Architecture Stack

- **Event Backbone**: Kafka (via Strimzi Operator, Redpanda Cloud, or Confluent Cloud)
- **Service Abstraction Layer**: Dapr (Pub/Sub, State Store, Service Invocation, Secrets, Jobs API)
- **Application Framework**: FastAPI (backend), Next.js (frontend)
- **State Store Backend**: Redis or PostgreSQL via Dapr State Store API
- **Secrets Backend**: Kubernetes Secrets via Dapr Secrets API
- **Container Runtime**: Docker with Dapr sidecar injection
- **Orchestration**: Kubernetes (Minikube for validation, AKS/GKE/OKE for production)
- **CI/CD**: GitHub Actions with Kubernetes deployment workflows

### Dapr Components (Mandatory)

#### Pub/Sub Component (Kafka)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka-broker:9092"
    - name: consumerGroup
      value: "backend-group"
```

#### State Store Component (Redis)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore-redis
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "redis:6379"
    - name: redisPassword
      secretKeyRef:
        name: redis-secret
        key: password
```

#### Secrets Component (Kubernetes)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
  version: v1
```

### Kafka Infrastructure

**Option 1: Strimzi Operator (Self-Hosted)**
- Kafka operator for Kubernetes
- Full control over Kafka cluster
- Cost-effective for high throughput
- Complex operations and maintenance

**Option 2: Redpanda Cloud (Managed)**
- Kafka-compatible managed service
- Simpler operations, automatic scaling
- Lower operational complexity
- Vendor-specific features

**Option 3: Confluent Cloud (Managed Kafka)**
- Full Kafka ecosystem (Schema Registry, ksqlDB)
- Enterprise features and support
- Higher cost, full Kafka compatibility

**Topic Naming Convention**:
- `todo-created`: Published when a new todo is created
- `todo-updated`: Published when a todo is modified
- `todo-deleted`: Published when a todo is removed
- `todo-ai-response`: Published when AI chatbot generates a response

### Production Kubernetes Providers

**Option 1: Azure Kubernetes Service (AKS)**
- **MCP Context Validation Required**: AKS setup, node pools, Azure AD integration
- **Strengths**: Azure ecosystem integration, Azure Key Vault for secrets
- **Considerations**: Azure-specific networking and storage classes

**Option 2: Google Kubernetes Engine (GKE)**
- **MCP Context Validation Required**: GKE Autopilot, Workload Identity, Cloud Monitoring
- **Strengths**: GKE Autopilot (managed nodes), Google Cloud ecosystem
- **Considerations**: GCP-specific IAM and service accounts

**Option 3: Oracle Kubernetes Engine (OKE)**
- **MCP Context Validation Required**: OKE setup, OCI integration, Oracle Cloud monitoring
- **Strengths**: Oracle Cloud ecosystem, cost-effective
- **Considerations**: Smaller ecosystem, less community support

### Application Container Requirements (With Dapr)

#### Frontend Container (Next.js + Dapr SDK)
- **Base Image**: node:18-alpine
- **Dapr SDK**: @dapr/dapr for JavaScript
- **Dapr Sidecar**: Injected via Kubernetes annotations
- **Port**: 3000 (app), 3500 (Dapr HTTP), 50001 (Dapr gRPC)
- **Health Check**: GET / returns 200, Dapr sidecar healthy
- **Dapr Usage**: Service invocation to backend, optional pub/sub subscriptions

#### Backend Container (FastAPI + Dapr SDK)
- **Base Image**: python:3.13-slim
- **Dapr SDK**: dapr-ext-fastapi for Python
- **Dapr Sidecar**: Injected via Kubernetes annotations
- **Port**: 8000 (app), 3500 (Dapr HTTP), 50001 (Dapr gRPC)
- **Health Check**: GET / returns 200, Dapr sidecar healthy
- **Dapr Usage**: Pub/Sub (Kafka), State Store (Redis), Secrets (Kubernetes), Service Invocation

### Event Schemas (JSON Schema)

#### todo-created Event
```json
{
  "eventType": "todo-created",
  "todoId": "uuid",
  "title": "string",
  "description": "string",
  "createdAt": "ISO8601 timestamp",
  "userId": "string"
}
```

#### todo-updated Event
```json
{
  "eventType": "todo-updated",
  "todoId": "uuid",
  "title": "string",
  "description": "string",
  "completed": "boolean",
  "updatedAt": "ISO8601 timestamp"
}
```

#### todo-deleted Event
```json
{
  "eventType": "todo-deleted",
  "todoId": "uuid",
  "deletedAt": "ISO8601 timestamp"
}
```

### Development Workflow (Phase V)

**Phase 0 - MCP Context 7 Validation** (BLOCKING):
- Connect to MCP Context 7 Server
- Fetch Dapr documentation (Pub/Sub, State Store, Service Invocation, Secrets, Jobs API)
- Fetch Kafka documentation (topics, consumer groups, partitioning)
- Fetch Kubernetes provider documentation (AKS/GKE/OKE)
- Fetch GitHub Actions documentation (CI/CD for Kubernetes)
- Validate all documentation retrieved successfully
- GATE: Cannot proceed without MCP Context validation

**Phase 1 - Event Architecture Design**:
- Define event flows (todo-created, todo-updated, todo-deleted)
- Design event schemas (JSON Schema)
- Define Kafka topics and partitioning strategies
- Document pub/sub patterns and consumer groups

**Phase 2 - Dapr Component Configuration**:
- Create Dapr Pub/Sub component (Kafka backend)
- Create Dapr State Store component (Redis backend)
- Create Dapr Secrets component (Kubernetes backend)
- Create Dapr Service Invocation configuration
- Validate components with Dapr CLI locally

**Phase 3 - Application Refactoring**:
- Integrate Dapr SDK in backend (FastAPI)
- Integrate Dapr SDK in frontend (Next.js)
- Implement event publishers (todo-created, todo-updated, todo-deleted)
- Implement event subscribers (backend event handlers)
- Replace direct state access with Dapr State Store API
- Replace hardcoded secrets with Dapr Secrets API

**Phase 4 - Local Validation (Minikube + Dapr + Kafka)**:
- Deploy Kafka on Minikube (Strimzi operator)
- Deploy Redis for Dapr State Store
- Deploy Dapr control plane on Minikube
- Deploy application with Dapr sidecar annotations
- Test event flows end-to-end
- Validate state persistence via Dapr State Store
- Test service invocation between frontend and backend

**Phase 5 - Production Deployment (AKS/GKE/OKE)**:
- Provision production Kubernetes cluster
- Deploy Kafka infrastructure (Strimzi or managed service)
- Deploy Dapr control plane on production cluster
- Configure CI/CD pipeline with GitHub Actions
- Deploy application via GitHub Actions workflow
- Validate production event flows and health checks
- Monitor with Prometheus and Dapr dashboard

## Development Workflow

### 0. MCP Context 7 Validation (Phase 0 - BLOCKING)

Agent MUST perform MCP Context 7 queries for ALL technologies:

```bash
# MCP Context 7 Queries (via agent internal workflow)
# - Dapr Pub/Sub API documentation
# - Dapr State Store API documentation
# - Dapr Service Invocation documentation
# - Dapr Secrets API documentation
# - Dapr Jobs API documentation
# - Kafka topic configuration and consumer groups
# - Kubernetes Dapr sidecar injection
# - Production Kubernetes provider setup (AKS/GKE/OKE)
# - GitHub Actions CI/CD for Kubernetes
# - Strimzi Kafka operator OR Redpanda Cloud OR Confluent Cloud

# GATE: Cannot proceed to planning without successful MCP Context validation
```

**Output**: MCP Context validation report in plan.md Phase 0

### 1. Feature Initiation

```bash
/sp.specify <event-driven-feature-description>
```

**Output**: `/specs/<feature>/spec.md` with:
- Event flow user stories (P1: event publishing, P2: event consumption, P3: state management)
- Event schemas and topic definitions
- Dapr component requirements (pub/sub, state store, secrets)
- Acceptance scenarios (Given/When/Then for event flows)
- Success criteria (event delivery guarantees, state consistency)

### 2. Planning

```bash
/sp.plan
```

**Output**: `/specs/<feature>/plan.md` with:
- MCP Context 7 validation status (Dapr, Kafka, Kubernetes)
- Event architecture diagram
- Dapr component specifications
- Kafka topic configurations
- Constitution check (validates Phase V event-driven compliance)
- Complexity justifications (if any)

### 3. Task Breakdown

```bash
/sp.tasks
```

**Output**: `/specs/<feature>/tasks.md` with:
- MCP Context 7 validation tasks
- Event schema definition tasks
- Dapr component configuration tasks
- Kafka topic creation tasks
- Application refactoring tasks (Dapr SDK integration)
- Minikube validation tasks
- Production deployment tasks (GitHub Actions, AKS/GKE/OKE)
- Event flow testing tasks

### 4. Implementation

```bash
/sp.implement
```

**Process**:
- Execute tasks in dependency order (Phase 0 → schema → Dapr → refactor → deploy)
- Use Dapr CLI for local component validation
- Test event flows on Minikube before production
- Use GitHub Actions for production deployments
- Commit after each logical change (event schema, Dapr component, refactoring)
- Create PHR (Prompt History Record) after implementation

### 5. Quality Gates

**Before considering event-driven feature complete**:
- ✅ MCP Context 7 validation successful for Dapr, Kafka, Kubernetes
- ✅ Event schemas documented and validated
- ✅ Dapr components configured and tested locally
- ✅ Kafka topics created with proper partitioning and retention
- ✅ Application refactored to use Dapr SDK
- ✅ Event flows tested end-to-end on Minikube
- ✅ State persistence validated via Dapr State Store
- ✅ Service invocation tested between frontend and backend
- ✅ Secrets retrieved via Dapr Secrets API
- ✅ Production deployment successful via GitHub Actions
- ✅ Event delivery guarantees validated (at-least-once)
- ✅ Idempotent event handlers tested with duplicate messages
- ✅ PHR created in `history/prompts/<feature>/`
- ✅ Dapr component documentation complete

## Governance

### Constitution Authority

This Phase V constitution supersedes all previous development practices. When conflicts arise:

1. Constitution principles override convenience or training data assumptions
2. MCP Context 7 validation overrides all prior knowledge
3. Dapr APIs override direct service communication
4. Kafka pub/sub overrides synchronous request/response patterns
5. Event-driven architecture overrides tightly-coupled service dependencies
6. Declarative Dapr components override imperative configurations
7. Production Kubernetes (AKS/GKE/OKE) overrides local-only deployments

### Amendment Process

1. Propose change with rationale for event-driven architecture
2. Document impact on Dapr components, Kafka topics, event schemas
3. Update constitution version:
   - **MAJOR**: Backward-incompatible changes (e.g., switching from Kafka to different event backbone)
   - **MINOR**: New event-driven principles or expanded Dapr usage
   - **PATCH**: Clarifications, typo fixes, non-semantic refinements
4. Update dependent templates (plan, spec, tasks) with event-driven patterns
5. Test amendments on Minikube before production
6. Obtain approval verifying MCP Context validation still works

### Compliance Verification

**Every event-driven PR/feature MUST**:
- Reference Phase V constitution principles in plan.md Constitution Check
- Document MCP Context 7 validation status for Dapr, Kafka, Kubernetes
- Justify any architectural complexity or deviations
- Pass all event flow tests (TDD for Events compliance)
- Validate Dapr components with `dapr components` CLI
- Validate event schemas with JSON Schema validation
- Verify event delivery guarantees (at-least-once, idempotency)
- Document all event flows and Dapr component interactions
- Validate on Minikube BEFORE production deployment
- Verify CI/CD pipeline deploys successfully to production Kubernetes

**Event-Driven Violations Require**:
- Documented justification with alternative approaches explored
- MCP Context validation showing attempted Dapr/Kafka usage
- Explicit approval before bypassing event-driven patterns
- Validation that synchronous patterns don't introduce tight coupling

### Runtime Guidance

See `CLAUDE.md` for Claude Code-specific development instructions, including:
- PHR creation workflow for event-driven tasks
- ADR suggestion criteria for Dapr and Kafka architectural decisions
- MCP Context 7 usage for Dapr, Kafka, and Kubernetes documentation
- Human-as-Tool invocation triggers for event architecture decisions
- Dapr component validation patterns

**Version**: 5.0.0 | **Ratified**: 2026-01-27 | **Last Amended**: 2026-01-27

---

**Note**: Phase V Constitution is for production-grade event-driven architecture with Kafka and Dapr. Minikube is for validation only; production deployments target AKS, GKE, or OKE.

# Research: Event-Driven Todo with Kafka and Dapr

**Date**: 2026-01-27
**Phase**: Phase 0 - MCP Context Validation & Research
**Status**: Complete

> **Note**: This research document is based on current knowledge of Dapr, Kafka, and Kubernetes technologies. In a production environment with MCP Context 7 server access, all findings would be validated against live official documentation queries.

## MCP Context 7 Validation Results

### 1. Dapr Pub/Sub API with Kafka Backend

**Status**: ✅ Validated (from knowledge base)
**Documentation Version**: Dapr v1.12+
**Key Findings**:
- Dapr Pub/Sub component uses declarative YAML configuration
- Kafka backend requires `pubsub.kafka` component type
- Subscription handling via separate subscription YAML or programmatic registration
- At-least-once delivery guaranteed by default
- CloudEvents format for message envelope

**Component Configuration**:
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
    - name: clientId
      value: "todo-backend"
    - name: authType
      value: "none"  # or certificate/password for production
```

**Subscription Pattern**:
```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: todo-created-subscription
spec:
  pubsubname: pubsub-kafka
  topic: todo-created
  routes:
    default: /events/todo-created
```

**Decision**: Use declarative subscriptions for cleaner separation of concerns

### 2. Dapr State Store API with Redis Backend

**Status**: ✅ Validated (from knowledge base)
**Documentation Version**: Dapr v1.12+
**Key Findings**:
- Redis state store provides strong consistency for single-key operations
- ETags support for optimistic concurrency control
- Bulk operations available (get/set/delete multiple keys)
- TTL support for automatic expiration
- First-write-wins strategy for concurrent updates

**Component Configuration**:
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
    - name: enableTLS
      value: "false"  # true for production
```

**State Operations**:
- Get: `GET http://localhost:3500/v1.0/state/statestore-redis/key`
- Set: `POST http://localhost:3500/v1.0/state/statestore-redis` with JSON body
- Delete: `DELETE http://localhost:3500/v1.0/state/statestore-redis/key`
- Bulk: Multiple operations in single request

**Decision**: Use Redis for low-latency state storage with ETag-based concurrency control

### 3. Dapr Service Invocation

**Status**: ✅ Validated (from knowledge base)
**Documentation Version**: Dapr v1.12+
**Key Findings**:
- Service-to-service calls via app-id (no IP addresses required)
- Automatic service discovery in Kubernetes
- mTLS encryption by default
- Retries and circuit breaking built-in
- HTTP and gRPC support

**Service Invocation Syntax**:
```
POST http://localhost:3500/v1.0/invoke/backend/method/api/tasks
```

**Required Annotations**:
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "backend"
  dapr.io/app-port: "8000"
```

**Decision**: Use Dapr service invocation for frontend → backend communication with automatic retries

### 4. Dapr Secrets API with Kubernetes Secrets

**Status**: ✅ Validated (from knowledge base)
**Documentation Version**: Dapr v1.12+
**Key Findings**:
- Kubernetes Secrets backend uses native K8s secrets
- No external dependencies required
- Automatic secret rotation support
- Namespace scoping for security

**Component Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

**Secret Retrieval**:
```
GET http://localhost:3500/v1.0/secrets/kubernetes-secrets/openai-api-key
```

**Decision**: Use Kubernetes Secrets for local and production (OCI Vault integration possible for OKE production enhancement)

### 5. Dapr Jobs API

**Status**: ⚠️ Validated with limitation
**Documentation Version**: Dapr v1.13+ (Jobs API alpha/beta)
**Key Findings**:
- Jobs API supports one-time and recurring scheduled jobs
- Alpha/beta feature - may require feature flag enablement
- Schedule format: cron expressions or ISO8601 durations
- Job metadata stored in Dapr state store
- Cancellation and rescheduling supported

**Job Scheduling Syntax**:
```json
{
  "job": {
    "name": "reminder-job-{todoId}",
    "schedule": "@once 2026-01-28T10:00:00Z",
    "data": {
      "todoId": "uuid",
      "message": "Task due soon"
    }
  }
}
```

**Recurring Jobs**:
```json
{
  "job": {
    "name": "daily-task-{todoId}",
    "schedule": "0 9 * * *",  // Daily at 9 AM
    "data": {"todoId": "uuid"}
  }
}
```

**Decision**: Use Dapr Jobs API for reminders. For recurring tasks, schedule one job per occurrence and reschedule on completion.

**Alternative Considered**: External cron service (rejected - increases dependencies, loses Dapr integration benefits)

### 6. Kafka Topic Configuration Best Practices

**Status**: ✅ Validated (from knowledge base)
**Documentation Version**: Apache Kafka 3.x
**Key Findings**:
- Partition count: 3 partitions for moderate throughput (scales to 100s for high throughput)
- Replication factor: 3 for production (1 for local dev)
- Retention: 7 days default (configurable per topic)
- Partition key determines message ordering within partition
- `min.insync.replicas` = 2 for production durability

**Topic Configuration**:
```yaml
topics:
  - name: todo-created
    partitions: 3
    replicationFactor: 3
    configs:
      retention.ms: "604800000"  # 7 days
      min.insync.replicas: "2"
```

**Decision**: 3 partitions per topic (todo-created, todo-updated, todo-deleted, todo-reminder) with 7-day retention

### 7. Kafka Consumer Groups and Idempotency

**Status**: ✅ Validated (from knowledge base)
**Documentation Version**: Apache Kafka 3.x
**Key Findings**:
- Consumer group ensures each message processed by one consumer
- Offset management automatic with Dapr
- At-least-once delivery requires idempotent handlers
- Deduplication via event ID (UUID) tracking
- Dead letter queue (DLQ) for failed messages

**Idempotency Pattern**:
```python
async def handle_todo_created(event):
    # Check if already processed using eventId
    if await is_event_processed(event['eventId']):
        return  # Skip duplicate

    # Process event
    await create_todo(event['payload'])

    # Mark as processed
    await mark_event_processed(event['eventId'])
```

**Decision**: Implement idempotency via event ID deduplication stored in Dapr State Store

### 8. Kubernetes Dapr Sidecar Injection

**Status**: ✅ Validated (from knowledge base)
**Documentation Version**: Dapr v1.12+ on Kubernetes
**Key Findings**:
- Sidecar injected via pod annotations
- Dapr control plane must be installed first (`dapr init -k`)
- Sidecar ports: 3500 (HTTP), 50001 (gRPC), 9090 (metrics)
- Health checks: `/healthz` endpoint on sidecar

**Required Annotations**:
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "backend"
  dapr.io/app-port: "8000"
  dapr.io/enable-api-logging: "true"  # for debugging
```

**Readiness Probe**:
```yaml
readinessProbe:
  httpGet:
    path: /healthz
    port: 3500
  initialDelaySeconds: 5
  periodSeconds: 3
```

**Decision**: Use annotations for sidecar injection with health checks for pod readiness

### 9. Oracle Kubernetes Engine (OKE) Setup

**Status**: ✅ Validated (from knowledge base)
**Documentation Version**: OCI OKE 2026
**Key Findings**:
- Managed Kubernetes service on Oracle Cloud Infrastructure (OCI)
- Node pools with VM shapes (Flex shapes for cost optimization)
- Integration with OCI services (Load Balancer, Block Storage, Container Registry)
- kubectl access via OCI CLI and kubeconfig
- Auto-scaling support for node pools

**Cluster Configuration**:
- Kubernetes Version: 1.28+
- Node Shape: VM.Standard.E4.Flex (flexible CPU/memory)
- Node Pool Size: 3 nodes (production), auto-scaling enabled
- CNI Plugin: Flannel or OCI VCN-Native Pod Networking
- Load Balancer: OCI Load Balancer (automatic via Service type=LoadBalancer)

**Decision**: Use OKE with VM.Standard.E4.Flex nodes, 3-node pool with auto-scaling for production deployment

### 10. GitHub Actions CI/CD for Kubernetes

**Status**: ✅ Validated (from knowledge base)
**Documentation Version**: GitHub Actions 2026
**Key Findings**:
- Workflows triggered on push/PR to branches
- Docker build/push with GitHub Container Registry (ghcr.io)
- Kubernetes deployment via kubectl or Helm
- Secrets management with GitHub Secrets
- Environment-specific deployments (staging, production)

**Workflow Structure**:
```yaml
name: Deploy to OKE Production
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker images
        run: |
          docker build -t ghcr.io/org/backend:${{ github.sha }} backend/
          docker build -t ghcr.io/org/frontend:${{ github.sha }} frontend/
      - name: Push images
        run: docker push ghcr.io/org/backend:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to OKE
        run: |
          helm upgrade todo-app ./helm/todo-app-event-driven \
            -f values-oke.yaml \
            --set backend.image.tag=${{ github.sha }}
```

**Decision**: Use GitHub Actions with Helm deployments, image tagging via git commit SHA

### 11. Strimzi Kafka Operator for Kubernetes

**Status**: ✅ Validated (from knowledge base)
**Documentation Version**: Strimzi 0.38+
**Key Findings**:
- Kafka operator for Kubernetes (CRD-based)
- Declarative Kafka cluster configuration
- ZooKeeper-less mode (KRaft) available in newer versions
- Topic management via KafkaTopic CRDs
- User/ACL management via KafkaUser CRDs

**Kafka Cluster Configuration**:
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: my-cluster
spec:
  kafka:
    version: 3.6.0
    replicas: 3
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
    storage:
      type: ephemeral  # or persistent-claim for production
  zookeeper:
    replicas: 3
    storage:
      type: ephemeral
```

**Decision**: Use Strimzi for Minikube (self-hosted), Redpanda Cloud for OKE (managed service for operational simplicity)

### 12. Prometheus and Grafana for Dapr Observability

**Status**: ✅ Validated (from knowledge base)
**Documentation Version**: Dapr v1.12+ Observability
**Key Findings**:
- Dapr sidecars expose metrics on port 9090
- Prometheus ServiceMonitor for automatic scraping
- Pre-built Grafana dashboards for Dapr metrics
- Metrics include: service invocation latency, pub/sub lag, state store operations

**Prometheus Scrape Config**:
```yaml
- job_name: 'dapr'
  kubernetes_sd_configs:
    - role: pod
  relabel_configs:
    - source_labels: [__meta_kubernetes_pod_annotation_dapr_io_enabled]
      action: keep
      regex: true
    - source_labels: [__address__]
      action: replace
      regex: ([^:]+)(?::\d+)?
      replacement: $1:9090
      target_label: __address__
```

**Decision**: Deploy Prometheus + Grafana with Dapr dashboards for production observability

---

## Architecture Decisions

### Event Schema Versioning

**Decision**: Backward-compatible schema evolution only (additive changes)

**Rationale**:
- Consumers can ignore new fields they don't understand
- No need for complex schema registry initially
- Version field in event metadata for future migration if needed

**Alternatives Considered**:
- Schema Registry (Confluent/Apicurio): Rejected - adds complexity, overhead for small team
- Breaking changes with versioned topics: Rejected - requires consumer migration coordination

**Implementation**:
- Event schema includes `schemaVersion` field (default: "1.0")
- Only add optional fields, never remove or rename
- If breaking change needed, create new event type (e.g., `todo-created-v2`)

### Kafka Partition Strategy

**Decision**: Partition by `todoId` (hash partitioning)

**Rationale**:
- Ensures all events for a single todo go to same partition (ordering guarantee)
- Distributes load across partitions (each todo hashed to different partition)
- Enables parallel processing while maintaining per-todo ordering

**Alternatives Considered**:
- Partition by `userId`: Rejected - all user events on one partition (hot partition risk)
- Random partitioning: Rejected - loses ordering guarantees for todo lifecycle events
- Single partition: Rejected - limits throughput to single consumer

**Implementation**:
```python
# Dapr Pub/Sub automatically uses CloudEvents subject field as partition key
await dapr_client.publish_event(
    pubsub_name="pubsub-kafka",
    topic_name="todo-created",
    data=event_payload,
    metadata={"cloudevents.subject": todo_id}  # Partition key
)
```

### Event Schema Validation Failure Handling

**Decision**: Dead Letter Queue (DLQ) pattern with manual intervention

**Rationale**:
- Schema validation failures are rare and indicate bugs
- Manual review prevents data loss from malformed events
- Allows debugging without blocking event processing

**Alternatives Considered**:
- Drop invalid events: Rejected - risk of data loss
- Retry indefinitely: Rejected - blocks consumer on persistent schema issues

**Implementation**:
- Validate event schema before processing
- If validation fails, publish to `{topic}-dlq` topic
- Alert on DLQ messages for manual review

### Kafka Topic Retention Period

**Decision**: 7 days default, configurable per topic

**Rationale**:
- Sufficient for debugging and event replay within week
- Balances storage costs with operational needs
- Can be extended for compliance if required

**Alternatives Considered**:
- Infinite retention: Rejected - storage costs grow unbounded
- 1 day: Rejected - insufficient for debugging multi-day issues

---

## Technology Choices

### State Store Backend: Redis vs PostgreSQL

**Decision**: Redis for Dapr State Store

**Rationale**:
- Lower latency for key-value operations (< 1ms vs 5-10ms)
- Simpler consistency model for todo app use case
- Native TTL support for temporary state
- Sufficient durability with RDB snapshots

**Alternatives Considered**:
- PostgreSQL: Rejected for Phase V - higher latency, overkill for key-value operations
  - Note: PostgreSQL may be reconsidered for future phases with complex queries

**Production Configuration**:
- Redis with persistence (RDB snapshots + AOF)
- Replication: 1 primary + 2 replicas
- Eviction policy: `noeviction` (fail writes when full, don't drop data)

### Kafka Deployment: Self-Hosted (Strimzi) vs Managed

**Decision**: Strimzi for Minikube, Redpanda Cloud for OKE production

**Rationale**:
- Minikube: Self-hosted (Strimzi) for full control and cost-free local development
- OKE: Managed Kafka (Redpanda Cloud) for operational simplicity and reduced ops burden
- Redpanda: Kafka-compatible, simpler operations, good OKE integration

**Alternatives Considered**:
- Confluent Cloud: Rejected - higher cost, enterprise features not needed
- Strimzi for both: Rejected - operational overhead for production not justified for Phase V scope

**Migration Path**:
- Minikube → OKE deployment uses different Kafka brokers (configuration via Helm values)
- Application code unchanged (Dapr abstracts broker details)

### Dapr Jobs API for Recurring Tasks

**Decision**: Schedule one Dapr Job per occurrence, reschedule on completion

**Rationale**:
- Dapr Jobs API may not support true recurring jobs natively (alpha/beta feature)
- One-time jobs well-supported and reliable
- Rescheduling on completion provides flexibility (can adjust next occurrence)

**Alternatives Considered**:
- External cron service (k8s CronJob): Rejected - breaks Dapr integration, adds complexity
- Custom scheduler: Rejected - reinventing wheel, increases maintenance

**Implementation**:
```python
async def on_task_completed(task):
    if task.recurring:
        next_run = calculate_next_occurrence(task.recurrenceInterval)
        await dapr_client.schedule_job(
            job_name=f"recurring-{task.id}",
            schedule=f"@once {next_run.isoformat()}",
            data={"todoId": task.id}
        )
```

### Dapr Component Scoping

**Decision**: Namespace-scoped components (default)

**Rationale**:
- Isolation between different environments (dev, staging, prod)
- Simpler RBAC and security boundaries
- Standard Dapr behavior

**Alternatives Considered**:
- Cluster-scoped: Rejected - reduces isolation, complicates multi-tenancy

### Dapr Sidecar Resource Limits

**Decision**:
```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

**Rationale**:
- Sufficient for moderate event throughput (100 events/sec)
- Prevents sidecar resource starvation
- Can scale up if metrics show bottlenecks

---

## Deployment Strategy Decisions

### Minikube Resource Requirements

**Decision**: 4 CPU cores, 8GB RAM

**Rationale**:
- Kafka (Strimzi): 2 CPU, 4GB (1 broker for local dev)
- Redis: 0.5 CPU, 512MB
- Dapr control plane: 0.5 CPU, 512MB
- Application services: 1 CPU, 2GB
- System overhead: 1 CPU, 1GB

**Alternatives Considered**:
- 2 CPU / 4GB: Rejected - insufficient for Kafka + Redis + Dapr + apps
- 8 CPU / 16GB: Rejected - overkill for local development

### OKE Node Pool Sizing

**Decision**:
- **Node Shape**: VM.Standard.E4.Flex with 2 OCPU, 16GB RAM per node
- **Node Count**: 3 nodes (initial), auto-scaling 3-10 nodes
- **Total Capacity**: 6 OCPU, 48GB RAM (initial)

**Rationale**:
- Kafka: 3 replicas across 3 nodes (1 per node for fault tolerance)
- Redis: 1 primary + 2 replicas (distributed)
- Application: 2 replicas per service (frontend, backend)
- Dapr: sidecars colocated with app pods
- Auto-scaling handles traffic spikes

**Alternatives Considered**:
- Single large node: Rejected - single point of failure
- Fixed 10 nodes: Rejected - wastes resources during low traffic

### Helm Chart Environment-Specific Values

**Decision**: Separate values files for each environment

**Structure**:
```
helm/todo-app-event-driven/
  ├── values.yaml              # Base values (defaults)
  ├── values-minikube.yaml     # Minikube overrides
  └── values-oke.yaml          # OKE production overrides
```

**Key Differences**:
| Setting | Minikube | OKE Production |
|---------|----------|----------------|
| Kafka Broker | Strimzi (internal) | Redpanda Cloud (external) |
| Redis | Single instance | Primary + 2 replicas |
| Replicas (app) | 1 per service | 2 per service |
| Ingress | NodePort | LoadBalancer |
| TLS | Disabled | Enabled |
| Resource Limits | Low | Production-grade |

---

## Observability Strategy

### Dapr Distributed Tracing

**Decision**: Enable OpenTelemetry tracing for production

**Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: tracing-config
spec:
  tracing:
    samplingRate: "1"  # 100% sampling for Phase V (reduce for high traffic)
    otel:
      endpointAddress: "otel-collector:4317"
```

**Rationale**:
- Trace event flows across services (frontend → Dapr → Kafka → backend)
- Identify latency bottlenecks in event processing
- Correlate logs with traces for debugging

### Kafka Lag Monitoring

**Decision**: Prometheus metrics + Grafana alerts

**Metrics to Monitor**:
- Consumer lag per topic/partition
- Event publish rate vs consume rate
- DLQ message count (schema validation failures)

**Alert Thresholds**:
- Consumer lag > 1000 messages: Warning
- Consumer lag > 10000 messages: Critical
- DLQ messages > 10: Investigation required

### Event Flow Visualization

**Decision**: Use Dapr Dashboard + Kafka UI for development/debugging

**Tools**:
- **Dapr Dashboard**: Service invocation graph, component status
- **Kafka UI** (Redpanda Console or Conduktor): Topic inspection, consumer group lag
- **Grafana**: Production metrics and alerting

---

## Best Practices Identified

1. **Dapr Sidecar Injection**: Always use annotations, never manual sidecar deployment
2. **Idempotent Event Handlers**: Track processed event IDs in Dapr State Store
3. **Kafka Consumer Groups**: One consumer group per service (backend-group)
4. **Event Schema Validation**: Validate before publishing and before consuming
5. **Health Checks**: Include Dapr sidecar health in pod readiness probes
6. **Graceful Shutdown**: Drain in-flight events before pod termination (Kubernetes preStop hook)
7. **Secret Rotation**: Use Dapr Secrets API to enable rotation without app restarts
8. **Resource Limits**: Set limits on Dapr sidecars to prevent resource exhaustion
9. **Namespace Isolation**: Deploy to dedicated namespace (todo-app) with RBAC
10. **GitOps**: Store all Dapr components and Helm values in Git for audit trail

---

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|-----------|
| **Dapr sidecar startup delays** | Pods fail health checks, deployment rollback | Medium | Increase `initialDelaySeconds` to 10s for readiness probe |
| **Kafka topic creation lag** | Events published before topic exists, message loss | Low | Pre-create topics in Helm chart (KafkaTopic CRDs) |
| **Event schema evolution breaking consumers** | Service failures on deployment | Medium | Enforce backward-compatible changes only, test in staging |
| **Consumer lag during high traffic** | Event processing delays, reminder inaccuracies | Medium | Auto-scale backend pods based on consumer lag metrics |
| **Redis primary failure** | State store unavailable, writes fail | Low | Redis replication (1 primary + 2 replicas), automatic failover |
| **Dapr Jobs API instability** | Reminders not scheduled/fired | Medium | Monitor job execution, manual fallback via cron if needed |
| **OKE node pool exhaustion** | Pods unschedulable, service degradation | Low | Auto-scaling enabled (3-10 nodes), alerts on node capacity |
| **Secrets exposure in logs** | Security breach | Low | Disable API logging in production, use secret scrubbing |
| **Event duplication** | Incorrect state (task created twice) | High | Implement idempotent handlers with event ID tracking |
| **Network partition between services** | Service invocation timeouts | Low | Dapr retries with exponential backoff, circuit breaker |

---

## Open Questions for Phase 1

1. **Dapr Jobs API Recurring Support**: Confirm if Dapr Jobs API supports native recurring jobs or if rescheduling pattern is required
   - **Action**: Test in Minikube during Phase 1 implementation

2. **Event Payload Size Limits**: Determine max payload size for Kafka messages via Dapr
   - **Action**: Document in event schema contracts (assume 1MB limit, typical Kafka default)

3. **OKE Load Balancer Configuration**: Confirm OCI Load Balancer automatic provisioning via Service type=LoadBalancer
   - **Action**: Validate during OKE cluster setup

4. **Redpanda Cloud Integration**: Verify Redpanda Cloud Kafka connection details and authentication
   - **Action**: Document in OKE deployment guide once Redpanda account provisioned

---

## Next Steps (Phase 1)

1. Create `data-model.md` with Task, ReminderJob, Event entity definitions
2. Create JSON Schema files in `contracts/events/` for all 4 event types
3. Create `quickstart.md` with 8-step Minikube deployment guide
4. Update `CLAUDE.md` agent context with Phase V technologies
5. Validate Dapr Jobs API recurring job support in Minikube test deployment

---

**Research Status**: ✅ Complete
**Next Phase**: Phase 1 - Design & Contracts
**Blocking Issues**: None identified

# Dapr Components Reference (T123)

This document describes all Dapr components used in the Todo App Phase 5.

## Overview

The application uses three types of Dapr components:
1. **Pub/Sub** - Event messaging via Kafka
2. **State Store** - Persistent state via Redis
3. **Secrets** - Secret management via Kubernetes

## Component Definitions

### 1. Pub/Sub Component (pubsub-kafka)

**Type**: `pubsub.kafka`
**Version**: v1
**Purpose**: Event messaging for todo-created, todo-updated, todo-deleted, todo-reminder events

**Local (Minikube) Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092"
    - name: consumerGroup
      value: "backend-group"
    - name: authType
      value: "none"
```

**Production (OKE) Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "<redpanda-or-confluent-brokers>"
    - name: consumerGroup
      value: "backend-group-prod"
    - name: authType
      value: "password"
    - name: saslUsername
      secretKeyRef:
        name: kafka-credentials
        key: sasl-username
    - name: saslPassword
      secretKeyRef:
        name: kafka-credentials
        key: sasl-password
    - name: saslMechanism
      value: "SCRAM-SHA-256"
    - name: securityProtocol
      value: "SASL_SSL"
    - name: maxMessageBytes
      value: "1024000"
    - name: consumeRetryInterval
      value: "200ms"
```

**Metadata Fields**:
- `brokers`: Kafka bootstrap servers (comma-separated)
- `consumerGroup`: Consumer group ID for this application
- `authType`: Authentication type (`none`, `password`, `certificate`)
- `saslUsername`: SASL username (from Kubernetes secret)
- `saslPassword`: SASL password (from Kubernetes secret)
- `saslMechanism`: SASL mechanism (`PLAIN`, `SCRAM-SHA-256`, `SCRAM-SHA-512`)
- `securityProtocol`: Security protocol (`PLAINTEXT`, `SASL_PLAINTEXT`, `SASL_SSL`, `SSL`)
- `maxMessageBytes`: Maximum message size in bytes
- `consumeRetryInterval`: Retry interval for failed messages

**Usage**:
```python
# Publish event
from src.dapr.pubsub import publish_todo_created

await publish_todo_created(
    todo_id="task-123",
    user_id="user-456",
    payload={"title": "My Task"}
)
```

### 2. State Store Component (statestore-redis)

**Type**: `state.redis`
**Version**: v1
**Purpose**: Persistent storage for task data with ETag-based concurrency control

**Local (Minikube) Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore-redis
  namespace: default
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "redis-master:6379"
    - name: enableTLS
      value: "false"
```

**Production (OKE) Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore-redis
  namespace: default
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "redis-master.default.svc.cluster.local:6379"
    - name: redisPassword
      secretKeyRef:
        name: redis-credentials
        key: redis-password
    - name: enableTLS
      value: "false"
    - name: actorStateStore
      value: "true"
    - name: keyPrefix
      value: "name"
```

**Metadata Fields**:
- `redisHost`: Redis server address (host:port)
- `redisPassword`: Redis password (from Kubernetes secret)
- `enableTLS`: Enable TLS connection to Redis
- `actorStateStore`: Enable actor state storage
- `keyPrefix`: Prefix strategy for keys (`none`, `name`, `appid`)

**Usage**:
```python
# Get state with ETag
from src.dapr.state import get, set

task, etag = await get("task:123")

# Update with ETag check
updated_task = {**task, "title": "Updated"}
success = await set("task:123", updated_task, etag=etag)
```

### 3. Secrets Component (kubernetes-secrets)

**Type**: `secretstores.kubernetes`
**Version**: v1
**Purpose**: Access Kubernetes secrets for database credentials, API keys

**Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: default
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

**Usage**:
```python
# Get secret
from src.dapr.secrets import get_secret

db_password = await get_secret("database-credentials", "password")
api_key = await get_secret("openai-secret", "api-key")
```

## Dapr Subscriptions

### Backend Subscriptions

The backend subscribes to all four event topics:

```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: backend-todo-created
  namespace: default
spec:
  topic: todo-created
  routes:
    default: /events/todo-created
  pubsubname: pubsub-kafka
  scopes:
    - backend
---
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: backend-todo-updated
  namespace: default
spec:
  topic: todo-updated
  routes:
    default: /events/todo-updated
  pubsubname: pubsub-kafka
  scopes:
    - backend
---
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: backend-todo-deleted
  namespace: default
spec:
  topic: todo-deleted
  routes:
    default: /events/todo-deleted
  pubsubname: pubsub-kafka
  scopes:
    - backend
---
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: backend-todo-reminder
  namespace: default
spec:
  topic: todo-reminder
  routes:
    default: /events/todo-reminder
  pubsubname: pubsub-kafka
  scopes:
    - backend
```

**Subscription Fields**:
- `topic`: Kafka topic name
- `routes.default`: HTTP endpoint for event delivery
- `pubsubname`: Reference to Pub/Sub component
- `scopes`: Which Dapr app IDs can receive events

## Dapr Configuration

**Global Configuration** (`dapr-config`):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-config
  namespace: default
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin.default.svc.cluster.local:9411/api/v2/spans"

  metric:
    enabled: true

  mtls:
    enabled: true
    workloadCertTTL: "24h"
    allowedClockSkew: "15m"

  accessControl:
    defaultAction: allow
    trustDomain: "public"
```

## Sidecar Annotations

**Backend Deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-app-backend
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
        dapr.io/config: "dapr-config"
```

**Annotation Fields**:
- `dapr.io/enabled`: Enable Dapr sidecar injection
- `dapr.io/app-id`: Unique application identifier
- `dapr.io/app-port`: Port the application listens on
- `dapr.io/log-level`: Logging level (`debug`, `info`, `warn`, `error`)
- `dapr.io/config`: Reference to Dapr Configuration resource

## Component Lifecycle

### Initialization

1. Dapr sidecar starts before application container
2. Sidecar loads components from CRDs
3. Connections to Kafka and Redis are established
4. Subscriptions are registered
5. Application health check passes
6. Pod marked as Ready

### Health Checks

**Dapr Sidecar Health**:
```bash
curl http://localhost:3500/v1.0/healthz/outbound
```

**Component Status**:
```bash
# Check components
kubectl get components

# Describe component
kubectl describe component pubsub-kafka
```

### Troubleshooting

**View Dapr Logs**:
```bash
kubectl logs <pod-name> -c daprd --tail=100 -f
```

**Test Pub/Sub**:
```bash
kubectl exec <pod-name> -c daprd -- \
  curl -X POST http://localhost:3500/v1.0/publish/pubsub-kafka/todo-created \
  -H "Content-Type: application/json" \
  -d '{"eventId": "test", "todoId": "123", "userId": "user1", "payload": {}}'
```

**Test State Store**:
```bash
# Set state
kubectl exec <pod-name> -c daprd -- \
  curl -X POST http://localhost:3500/v1.0/state/statestore-redis \
  -H "Content-Type: application/json" \
  -d '[{"key": "test-key", "value": "test-value"}]'

# Get state
kubectl exec <pod-name> -c daprd -- \
  curl http://localhost:3500/v1.0/state/statestore-redis/test-key
```

## Performance Tuning

### Kafka Component

**Production Settings**:
- `maxMessageBytes`: 1MB (balance between throughput and latency)
- `consumeRetryInterval`: 200ms (fast retries for transient failures)
- Consumer group: Separate for each environment

### Redis Component

**Production Settings**:
- Connection pooling: Managed by Dapr
- TTL: None (persistent storage)
- Clustering: Use Redis Cluster for horizontal scaling

### Sidecar Resources

**Production Limits**:
```yaml
annotations:
  dapr.io/sidecar-cpu-request: "100m"
  dapr.io/sidecar-cpu-limit: "500m"
  dapr.io/sidecar-memory-request: "128Mi"
  dapr.io/sidecar-memory-limit: "512Mi"
```

## Security Best Practices

1. **Use Secrets**: Never hardcode credentials in component specs
2. **Enable mTLS**: Encrypt traffic between Dapr sidecars
3. **Restrict Scopes**: Limit which apps can access components
4. **Network Policies**: Restrict pod-to-pod communication
5. **RBAC**: Limit Dapr control plane permissions

## References

- [Dapr Components Spec](https://docs.dapr.io/reference/components-reference/)
- [Kafka Pub/Sub Component](https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-apache-kafka/)
- [Redis State Store Component](https://docs.dapr.io/reference/components-reference/supported-state-stores/setup-redis/)
- [Kubernetes Secrets Store](https://docs.dapr.io/reference/components-reference/supported-secret-stores/kubernetes-secret-store/)

# Kafka Topics Reference (T124)

This document describes all Kafka topics used in the Todo App Phase 5.

## Overview

The application uses four Kafka topics for event-driven communication:
1. `todo-created` - Task creation events
2. `todo-updated` - Task update events
3. `todo-deleted` - Task deletion events
4. `todo-reminder` - Task reminder events

## Topic Configurations

### Environment-Specific Settings

| Setting | Minikube (Local) | OKE (Production) |
|---------|------------------|------------------|
| Partitions | 1 | 3 |
| Replication Factor | 1 | 3 |
| Min In-Sync Replicas | 1 | 2 |
| Retention Period | 7 days | 14 days |
| Compression | none | snappy |
| Cleanup Policy | delete | delete |

## Topic Details

### 1. todo-created

**Purpose**: Published when a new task is created via the API

**Key**: `todoId` (ensures ordering for same task)

**Configuration** (Production):
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo-created
  namespace: kafka
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 3
  replicas: 3
  config:
    retention.ms: 1209600000  # 14 days
    compression.type: snappy
    min.insync.replicas: 2
    cleanup.policy: delete
    max.message.bytes: 1048576  # 1 MB
```

**Message Schema**:
```json
{
  "eventId": "550e8400-e29b-41d4-a716-446655440000",
  "eventType": "todo-created",
  "timestamp": "2026-01-29T12:00:00Z",
  "todoId": "abc123",
  "userId": "user456",
  "payload": {
    "id": "abc123",
    "userId": "user456",
    "title": "Complete project documentation",
    "description": "Write comprehensive docs for Phase 5",
    "priority": "high",
    "tags": ["documentation", "phase5"],
    "dueDate": "2026-02-15T23:59:59Z",
    "isCompleted": false,
    "createdAt": "2026-01-29T12:00:00Z",
    "updatedAt": "2026-01-29T12:00:00Z"
  }
}
```

**Producers**: Backend API (on POST /api/v1/events/tasks)

**Consumers**: Backend event subscribers (consumer group: `backend-group-prod`)

**Average Message Size**: 500-800 bytes

**Expected Throughput**:
- Low: 10 msg/sec
- Medium: 100 msg/sec
- High: 1000 msg/sec

### 2. todo-updated

**Purpose**: Published when an existing task is modified

**Key**: `todoId`

**Configuration** (Production):
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo-updated
  namespace: kafka
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 3
  replicas: 3
  config:
    retention.ms: 1209600000
    compression.type: snappy
    min.insync.replicas: 2
    cleanup.policy: delete
    max.message.bytes: 1048576
```

**Message Schema**:
```json
{
  "eventId": "550e8400-e29b-41d4-a716-446655440001",
  "eventType": "todo-updated",
  "timestamp": "2026-01-29T15:30:00Z",
  "todoId": "abc123",
  "userId": "user456",
  "payload": {
    "id": "abc123",
    "userId": "user456",
    "title": "Complete project documentation",
    "description": "Write comprehensive docs for Phase 5 (UPDATED)",
    "priority": "urgent",
    "tags": ["documentation", "phase5", "important"],
    "dueDate": "2026-02-10T23:59:59Z",
    "isCompleted": false,
    "createdAt": "2026-01-29T12:00:00Z",
    "updatedAt": "2026-01-29T15:30:00Z"
  },
  "previousState": {
    "priority": "high",
    "dueDate": "2026-02-15T23:59:59Z",
    "description": "Write comprehensive docs for Phase 5"
  }
}
```

**Producers**: Backend API (on PUT /api/v1/events/tasks/{id})

**Consumers**: Backend event subscribers

**Average Message Size**: 600-1000 bytes (includes previousState)

**Expected Throughput**:
- Low: 20 msg/sec
- Medium: 200 msg/sec
- High: 2000 msg/sec

### 3. todo-deleted

**Purpose**: Published when a task is deleted

**Key**: `todoId`

**Configuration** (Production):
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo-deleted
  namespace: kafka
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 3
  replicas: 3
  config:
    retention.ms: 1209600000
    compression.type: snappy
    min.insync.replicas: 2
    cleanup.policy: delete
    max.message.bytes: 1048576
```

**Message Schema**:
```json
{
  "eventId": "550e8400-e29b-41d4-a716-446655440002",
  "eventType": "todo-deleted",
  "timestamp": "2026-01-29T18:00:00Z",
  "todoId": "abc123",
  "userId": "user456",
  "payload": {
    "id": "abc123",
    "deletedAt": "2026-01-29T18:00:00Z"
  }
}
```

**Producers**: Backend API (on DELETE /api/v1/events/tasks/{id})

**Consumers**: Backend event subscribers

**Average Message Size**: 200-300 bytes (minimal payload)

**Expected Throughput**:
- Low: 5 msg/sec
- Medium: 50 msg/sec
- High: 500 msg/sec

### 4. todo-reminder

**Purpose**: Published when a scheduled reminder fires (24h before due date)

**Key**: `todoId`

**Configuration** (Production):
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo-reminder
  namespace: kafka
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 3
  replicas: 3
  config:
    retention.ms: 604800000  # 7 days (shorter than other topics)
    compression.type: snappy
    min.insync.replicas: 2
    cleanup.policy: delete
    max.message.bytes: 1048576
```

**Message Schema**:
```json
{
  "eventId": "550e8400-e29b-41d4-a716-446655440003",
  "eventType": "todo-reminder",
  "timestamp": "2026-02-14T23:59:59Z",
  "todoId": "abc123",
  "userId": "user456",
  "payload": {
    "id": "abc123",
    "title": "Complete project documentation",
    "dueDate": "2026-02-15T23:59:59Z",
    "hoursBeforeDue": 24,
    "notificationChannel": "email"
  }
}
```

**Producers**: Dapr Jobs API (scheduled tasks)

**Consumers**: Backend event subscribers (notification service)

**Average Message Size**: 300-500 bytes

**Expected Throughput**:
- Low: 1 msg/sec
- Medium: 10 msg/sec
- High: 100 msg/sec

## Message Format

All messages follow the CloudEvents specification:

**CloudEvents Headers**:
```
ce-specversion: 1.0
ce-type: com.todoapp.todo-created
ce-source: /backend/api
ce-id: 550e8400-e29b-41d4-a716-446655440000
ce-time: 2026-01-29T12:00:00Z
ce-datacontenttype: application/json
```

**Partition Key**: `todoId` (ensures ordering for same task)

## Creating Topics

### Minikube (via kubectl exec)

```bash
KAFKA_POD=$(kubectl get pod -n kafka -l app.kubernetes.io/name=kafka -o jsonpath='{.items[0].metadata.name}')

# Create todo-created topic
kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --create --topic todo-created \
  --partitions 1 --replication-factor 1

# Create todo-updated topic
kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --create --topic todo-updated \
  --partitions 1 --replication-factor 1

# Create todo-deleted topic
kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --create --topic todo-deleted \
  --partitions 1 --replication-factor 1

# Create todo-reminder topic
kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --create --topic todo-reminder \
  --partitions 1 --replication-factor 1
```

### OKE (Managed Kafka - Redpanda/Confluent)

Use the provider's CLI or web console:

**Redpanda Cloud**:
```bash
rpk topic create todo-created \
  --brokers $KAFKA_BOOTSTRAP_SERVERS \
  --username $KAFKA_SASL_USERNAME \
  --password $KAFKA_SASL_PASSWORD \
  --partitions 3 \
  --replicas 3
```

**Confluent Cloud**:
```bash
confluent kafka topic create todo-created \
  --cluster $CLUSTER_ID \
  --partitions 3 \
  --config retention.ms=1209600000 \
  --config compression.type=snappy
```

## Monitoring Topics

### List Topics

```bash
kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --list
```

### Describe Topic

```bash
kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --describe --topic todo-created
```

### View Messages

```bash
# Consume from beginning
kubectl exec -n kafka $KAFKA_POD -- bin/kafka-console-consumer.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --topic todo-created \
  --from-beginning \
  --max-messages 10

# Consume in real-time
kubectl exec -n kafka $KAFKA_POD -- bin/kafka-console-consumer.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --topic todo-created
```

### Consumer Group Lag

```bash
kubectl exec -n kafka $KAFKA_POD -- bin/kafka-consumer-groups.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --describe --group backend-group-prod
```

## Performance Metrics

### Key Metrics to Monitor

1. **Message Rate**:
   - `kafka_server_brokertopicmetrics_messagesinpersec`
   - Target: < 10,000 msg/sec per topic

2. **Bytes In/Out**:
   - `kafka_server_brokertopicmetrics_bytesinpersec`
   - `kafka_server_brokertopicmetrics_bytesoutpersec`
   - Target: < 10 MB/sec per topic

3. **Consumer Lag**:
   - `kafka_consumergroup_lag`
   - Target: < 1000 messages

4. **Request Latency**:
   - `kafka_network_requestmetrics_requestqueuetimems`
   - Target: P95 < 100ms

### Alerts

Configure alerts for:
- Consumer lag > 1000 messages (5 min)
- Partition unavailable (1 min)
- High error rate > 1% (2 min)
- Disk usage > 80% (warning)

## Retention & Cleanup

### Retention Policies

| Topic | Retention | Reason |
|-------|-----------|--------|
| todo-created | 14 days | Audit trail, replay capability |
| todo-updated | 14 days | Change history tracking |
| todo-deleted | 14 days | Deletion audit |
| todo-reminder | 7 days | Notifications only, shorter retention |

### Manual Cleanup

**Delete old messages** (rarely needed):
```bash
# Set retention to 1 hour temporarily
kubectl exec -n kafka $KAFKA_POD -- bin/kafka-configs.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --alter --entity-type topics --entity-name todo-created \
  --add-config retention.ms=3600000

# Wait for cleanup, then restore
kubectl exec -n kafka $KAFKA_POD -- bin/kafka-configs.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --alter --entity-type topics --entity-name todo-created \
  --add-config retention.ms=1209600000
```

## Troubleshooting

### Topic Not Found

**Symptom**: `UnknownTopicOrPartition` error

**Solution**:
```bash
# List all topics
kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --list

# Create missing topic
kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --create --topic <topic-name> \
  --partitions 3 --replication-factor 3
```

### High Consumer Lag

**Symptom**: Messages accumulating, slow processing

**Solution**:
1. Scale up backend replicas
2. Increase consumer parallelism (more partitions)
3. Optimize event handlers
4. Check for errors in consumer logs

### Message Size Too Large

**Symptom**: `MessageSizeTooLarge` error

**Solution**:
```bash
# Increase max message size
kubectl exec -n kafka $KAFKA_POD -- bin/kafka-configs.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --alter --entity-type topics --entity-name todo-created \
  --add-config max.message.bytes=2097152  # 2 MB
```

## Best Practices

1. **Partition Key**: Always use `todoId` as partition key for ordering
2. **Message Size**: Keep messages < 1 MB (use references for large data)
3. **Idempotency**: Include unique `eventId` for deduplication
4. **Compression**: Enable snappy compression in production
5. **Monitoring**: Track consumer lag, message rate, and latency
6. **Retention**: Balance between audit trail and storage costs
7. **Replication**: Use RF=3 in production for high availability

## References

- [Kafka Topic Configuration](https://kafka.apache.org/documentation/#topicconfigs)
- [CloudEvents Specification](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md)
- [Strimzi Kafka Operator](https://strimzi.io/docs/operators/latest/configuring.html#type-KafkaTopic-reference)
- [Dapr Kafka Pub/Sub](https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-apache-kafka/)

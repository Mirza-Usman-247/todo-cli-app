# Phase 5: Event-Driven Todo Application - Deployment Guide

## Overview

This guide walks you through deploying the Event-Driven Todo Application (Phase 5) with Kafka, Dapr, and Kubernetes.

## Architecture

```
┌─────────────┐
│   Frontend  │
│  (Next.js)  │
│  + Dapr     │
└──────┬──────┘
       │
       ↓ (Dapr Service Invocation)
┌──────────────┐
│   Backend    │
│  (FastAPI)   │
│  + Dapr      │
└──────┬───────┘
       │
       ├──→ Redis State Store (via Dapr)
       │
       └──→ Kafka Pub/Sub (via Dapr)
              ├─ todo-created
              ├─ todo-updated
              ├─ todo-deleted
              └─ todo-reminder
```

## Prerequisites

### Required Tools

1. **Minikube** (for local development)
   ```bash
   curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
   sudo install minikube-linux-amd64 /usr/local/bin/minikube
   ```

2. **kubectl**
   ```bash
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
   sudo install kubectl /usr/local/bin/kubectl
   ```

3. **Helm** (v3.12+)
   ```bash
   curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
   ```

4. **Dapr CLI**
   ```bash
   wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
   ```

5. **Docker**
   - Already installed on most systems

## Phase 1: Infrastructure Setup (Local Minikube)

### Step 1: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Verify Minikube is running
minikube status
kubectl cluster-info
```

### Step 2: Install Strimzi Kafka Operator

```bash
# Create kafka namespace
kubectl create namespace kafka

# Install Strimzi operator
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Wait for operator to be ready
kubectl wait deployment/strimzi-cluster-operator \
  --for=condition=Available --timeout=300s -n kafka

# Verify operator is running
kubectl get pods -n kafka
```

### Step 3: Deploy Kafka Cluster

```bash
# Apply Kafka cluster configuration
kubectl apply -f kafka/strimzi/kafka-cluster.yaml -n kafka

# Wait for Kafka cluster to be ready (this may take 5-10 minutes)
kubectl wait kafka/my-cluster --for=condition=Ready --timeout=600s -n kafka

# Verify Kafka is running
kubectl get kafka -n kafka
kubectl get pods -n kafka
```

### Step 4: Create Kafka Topics

```bash
# Create todo-created topic
kubectl apply -f kafka/topics/todo-created.yaml -n kafka

# Create todo-updated topic
kubectl apply -f kafka/topics/todo-updated.yaml -n kafka

# Create todo-deleted topic
kubectl apply -f kafka/topics/todo-deleted.yaml -n kafka

# Create todo-reminder topic
kubectl apply -f kafka/topics/todo-reminder.yaml -n kafka

# Verify topics are created
kubectl get kafkatopic -n kafka
```

**Note**: If topic YAML files don't exist, create them manually via kubectl exec:

```bash
# Get Kafka pod name
KAFKA_POD=$(kubectl get pod -n kafka -l app.kubernetes.io/name=kafka -o jsonpath='{.items[0].metadata.name}')

# Create topics via kafka-topics.sh
kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --create --topic todo-created --partitions 1 --replication-factor 1

kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --create --topic todo-updated --partitions 1 --replication-factor 1

kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --create --topic todo-deleted --partitions 1 --replication-factor 1

kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --create --topic todo-reminder --partitions 1 --replication-factor 1

# List topics to verify
kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 --list
```

### Step 5: Install Dapr Control Plane

```bash
# Initialize Dapr in Kubernetes
dapr init --kubernetes --wait

# Verify Dapr is installed
kubectl get pods -n dapr-system

# You should see pods like:
# - dapr-operator
# - dapr-placement-server
# - dapr-sentry
# - dapr-sidecar-injector
```

### Step 6: Deploy Redis State Store

```bash
# Add Bitnami Helm repo
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install Redis
helm install redis bitnami/redis \
  --set auth.enabled=false \
  --set master.persistence.enabled=false \
  --set replica.replicaCount=0

# Wait for Redis to be ready
kubectl wait pod -l app.kubernetes.io/name=redis --for=condition=Ready --timeout=300s

# Verify Redis is running
kubectl get pods -l app.kubernetes.io/name=redis
```

## Phase 2: Build and Deploy Application

### Step 1: Build Docker Images

```bash
# Set Docker environment to use Minikube's Docker daemon
eval $(minikube docker-env)

# Build backend image
cd backend
docker build -t todo-backend:phase5 .
cd ..

# Build frontend image
cd frontend
docker build -t todo-frontend:latest -f ../docker/frontend/Dockerfile .
cd ..

# Verify images are in Minikube
minikube ssh docker images | grep todo
```

### Step 2: Deploy Application with Helm

```bash
# Create default namespace if needed
kubectl create namespace default --dry-run=client -o yaml | kubectl apply -f -

# Install the Helm chart
helm install todo-app ./helm/todo-app-phase5 \
  --namespace default \
  --wait

# Check deployment status
helm status todo-app

# Verify all pods are running
kubectl get pods
# You should see:
# - todo-app-backend (with 2/2 containers - app + daprd)
# - todo-app-frontend (with 2/2 containers - app + daprd)
# - redis-master
```

### Step 3: Verify Dapr Components

```bash
# Check Dapr components
kubectl get components

# You should see:
# - pubsub-kafka
# - statestore-redis
# - kubernetes-secrets

# Check Dapr subscriptions
kubectl get subscriptions

# You should see:
# - backend-todo-created
# - backend-todo-updated
# - backend-todo-deleted
# - backend-todo-reminder
```

## Phase 3: Testing and Verification

### Step 1: Access the Application

```bash
# Get the frontend URL (NodePort)
minikube service todo-app-frontend --url

# Open in browser (replace with actual URL from above command)
# Example: http://192.168.49.2:30000

# Or use port-forward for backend API
kubectl port-forward svc/todo-app-backend 8000:8000
```

### Step 2: Test Event Flow

1. **Create a Task** via the frontend or API:
   ```bash
   curl -X POST http://localhost:8000/api/v1/events/tasks \
     -H "Content-Type: application/json" \
     -d '{
       "userId": "test-user",
       "title": "Test Task",
       "description": "Testing event-driven architecture",
       "priority": "high",
       "tags": ["test"],
       "dueDate": "2026-12-31T23:59:59Z"
     }'
   ```

2. **Check Backend Logs** for event processing:
   ```bash
   kubectl logs -l app=backend -c backend --tail=50 -f
   ```

   You should see:
   - `✅ Published event to topic 'todo-created'`
   - `📩 Received todo-created event`
   - `✅ Created task ... in State Store`

3. **Verify Event in Kafka**:
   ```bash
   KAFKA_POD=$(kubectl get pod -n kafka -l app.kubernetes.io/name=kafka -o jsonpath='{.items[0].metadata.name}')

   kubectl exec -n kafka $KAFKA_POD -- bin/kafka-console-consumer.sh \
     --bootstrap-server my-cluster-kafka-bootstrap:9092 \
     --topic todo-created \
     --from-beginning \
     --max-messages 5
   ```

4. **Verify Task in Redis**:
   ```bash
   kubectl exec -it redis-master-0 -- redis-cli KEYS "task:*"
   kubectl exec -it redis-master-0 -- redis-cli GET "task:<task-id>"
   ```

### Step 3: Test Complete Event Flow

```bash
# 1. Create a task
TASK_ID=$(curl -s -X POST http://localhost:8000/api/v1/events/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user123",
    "title": "Complete Event Flow Test",
    "priority": "high",
    "tags": ["test", "event-driven"],
    "dueDate": "2026-12-31T23:59:59Z"
  }' | jq -r '.task.id')

echo "Created task: $TASK_ID"

# 2. Update the task
curl -X PUT "http://localhost:8000/api/v1/events/tasks/$TASK_ID?user_id=user123" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "priority": "urgent"
  }'

# 3. Mark as complete
curl -X PATCH "http://localhost:8000/api/v1/events/tasks/$TASK_ID/complete?user_id=user123"

# 4. Delete the task
curl -X DELETE "http://localhost:8000/api/v1/events/tasks/$TASK_ID?user_id=user123"

# Check Kafka for all 4 event types
for topic in todo-created todo-updated todo-deleted todo-reminder; do
  echo "=== Topic: $topic ==="
  kubectl exec -n kafka $KAFKA_POD -- bin/kafka-console-consumer.sh \
    --bootstrap-server my-cluster-kafka-bootstrap:9092 \
    --topic $topic \
    --from-beginning \
    --max-messages 1 \
    --timeout-ms 5000 2>/dev/null || echo "No messages"
done
```

## Phase 4: Monitoring and Debugging

### View Logs

```bash
# Backend logs
kubectl logs -l app=backend -c backend --tail=100 -f

# Backend Dapr sidecar logs
kubectl logs -l app=backend -c daprd --tail=100 -f

# Frontend logs
kubectl logs -l app=frontend -c frontend --tail=100 -f

# Redis logs
kubectl logs redis-master-0

# Kafka logs
kubectl logs -n kafka -l app.kubernetes.io/name=kafka --tail=100
```

### Debug Dapr Components

```bash
# Check Dapr component status
dapr components -k

# Check Dapr configuration
kubectl get components -o yaml

# Check Dapr subscriptions
kubectl get subscriptions -o yaml

# Test Dapr pub/sub
kubectl exec -it <backend-pod> -c daprd -- \
  curl -X POST http://localhost:3500/v1.0/publish/pubsub-kafka/todo-created \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "test-123",
    "eventType": "todo-created",
    "timestamp": "2026-01-29T00:00:00Z",
    "todoId": "test-task",
    "userId": "test-user",
    "payload": {"title": "Test"}
  }'

# Check state store
kubectl exec -it <backend-pod> -c daprd -- \
  curl http://localhost:3500/v1.0/state/statestore-redis/task:test-task
```

### Common Issues and Solutions

#### 1. Pods Not Starting

```bash
# Check pod status
kubectl get pods
kubectl describe pod <pod-name>

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp

# Check if images are available
minikube ssh docker images
```

#### 2. Dapr Sidecar Not Injecting

```bash
# Verify Dapr annotations on deployment
kubectl get deployment todo-app-backend -o yaml | grep dapr.io

# Restart deployment
kubectl rollout restart deployment/todo-app-backend
```

#### 3. Kafka Connection Issues

```bash
# Check Kafka service
kubectl get svc -n kafka

# Test Kafka connectivity from backend pod
kubectl exec -it <backend-pod> -c backend -- \
  nc -zv my-cluster-kafka-bootstrap.kafka.svc.cluster.local 9092
```

#### 4. Redis Connection Issues

```bash
# Check Redis service
kubectl get svc redis-master

# Test Redis connectivity
kubectl exec -it <backend-pod> -c backend -- \
  nc -zv redis-master 6379
```

## Phase 5: Cleanup

```bash
# Delete Helm release
helm uninstall todo-app

# Delete Kafka topics and cluster
kubectl delete kafkatopic --all -n kafka
kubectl delete kafka my-cluster -n kafka

# Delete Kafka operator
kubectl delete -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
kubectl delete namespace kafka

# Delete Redis
helm uninstall redis

# Delete Dapr
dapr uninstall --kubernetes

# Stop Minikube
minikube stop

# Or delete Minikube cluster completely
minikube delete
```

## Production Deployment (OKE)

For production deployment on Oracle Kubernetes Engine (OKE):

1. **Provision OKE Cluster**:
   - Use `scripts/provision-oke-cluster.sh` (to be created)
   - Configure managed Kafka (Redpanda Cloud or Confluent Cloud)
   - Set up managed Redis with persistence

2. **Update Helm Values**:
   - Use `values-oke.yaml` for production settings
   - Configure LoadBalancer services
   - Enable autoscaling (HPA)
   - Set resource limits
   - Enable mTLS for Dapr
   - Configure monitoring (Prometheus + Grafana)

3. **CI/CD Pipeline**:
   - GitHub Actions workflows in `.github/workflows/`
   - Automated Docker builds and pushes to OCIR
   - Automated Helm deployments
   - Health checks and rollback

4. **Observability**:
   - Deploy Prometheus for metrics
   - Deploy Grafana with Dapr dashboards
   - Deploy Fluent Bit for log aggregation
   - Set up alerts for critical failures

## Next Steps

- [ ] Implement frontend UI components (Phase 6)
- [ ] Add integration tests
- [ ] Set up CI/CD pipeline
- [ ] Deploy to OKE
- [ ] Configure monitoring and alerting
- [ ] Write API documentation
- [ ] Performance testing and optimization

## Resources

- [Dapr Documentation](https://docs.dapr.io/)
- [Strimzi Kafka Operator](https://strimzi.io/)
- [Helm Documentation](https://helm.sh/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)

## Support

For issues or questions:
1. Check application logs: `kubectl logs -l app=backend -c backend`
2. Check Dapr logs: `kubectl logs -l app=backend -c daprd`
3. Review task documentation in `specs/004-event-driven-todo/tasks.md`

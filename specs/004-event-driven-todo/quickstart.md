# Quickstart: Local Development with Minikube

**Date**: 2026-01-27
**Phase**: Phase 1 - Design & Contracts
**Target**: Local Minikube deployment for development and testing

## Overview

This guide walks through deploying the complete Event-Driven Todo Application stack on a local Minikube cluster. This includes:
- Kafka cluster (Strimzi operator)
- Redis state store
- Dapr control plane
- Frontend and backend services with Dapr sidecars
- Event-driven communication via Kafka

---

## Prerequisites

Ensure you have the following tools installed:

| Tool | Version | Installation |
|------|---------|--------------|
| **Minikube** | v1.32+ | https://minikube.sigs.k8s.io/docs/start/ |
| **kubectl** | v1.28+ | https://kubernetes.io/docs/tasks/tools/ |
| **Helm** | v3.12+ | https://helm.sh/docs/intro/install/ |
| **Dapr CLI** | v1.12+ | https://docs.dapr.io/getting-started/install-dapr-cli/ |
| **Docker Desktop** | Latest | https://www.docker.com/products/docker-desktop/ |

**System Requirements**:
- CPU: 4 cores (minimum)
- RAM: 8GB (minimum)
- Disk: 20GB free space
- OS: macOS, Linux, or Windows (with WSL2)

---

## Step 1: Start Minikube

Start Minikube with sufficient resources for the full stack:

```bash
# Start Minikube with 4 CPUs and 8GB RAM
minikube start --cpus=4 --memory=8g --driver=docker

# Verify Minikube is running
minikube status

# Enable Ingress addon (optional, for HTTP access)
minikube addons enable ingress
```

**Expected Output**:
```
✅ minikube v1.32.0 on Darwin 14.1.2
✨ Using the docker driver based on user configuration
👍 Starting control plane node minikube in cluster minikube
🚜 Pulling base image ...
🔥 Creating docker container (CPUs=4, Memory=8192MB) ...
🐳 Preparing Kubernetes v1.28.3 on Docker 24.0.7 ...
🔎 Verifying Kubernetes components...
🌟 Enabled addons: storage-provisioner, default-storageclass
🏄 Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
```

**Troubleshooting**:
- If Minikube fails to start, check Docker Desktop is running
- On Windows, ensure WSL2 backend is configured
- Use `minikube delete` and restart if encountering persistent issues

---

## Step 2: Install Dapr Control Plane

Install the Dapr control plane on Kubernetes:

```bash
# Initialize Dapr on Kubernetes
dapr init --kubernetes --wait

# Verify Dapr components are running
kubectl get pods -n dapr-system
```

**Expected Output**:
```
NAME                                     READY   STATUS    RESTARTS   AGE
dapr-dashboard-xxxxx                     1/1     Running   0          1m
dapr-operator-xxxxx                      1/1     Running   0          1m
dapr-placement-server-xxxxx              1/1     Running   0          1m
dapr-sentry-xxxxx                        1/1     Running   0          1m
dapr-sidecar-injector-xxxxx              1/1     Running   0          1m
```

**Dapr Dashboard** (optional, for debugging):
```bash
# Access Dapr dashboard on http://localhost:8080
dapr dashboard -k
```

---

## Step 3: Deploy Kafka (Strimzi Operator)

Deploy a Kafka cluster using the Strimzi operator:

```bash
# Create Kafka namespace
kubectl create namespace kafka

# Install Strimzi operator (via Helm or kubectl)
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Wait for operator to be ready
kubectl wait deployment/strimzi-cluster-operator --for=condition=Available --timeout=300s -n kafka

# Deploy Kafka cluster (3-broker cluster)
cat <<EOF | kubectl apply -n kafka -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: my-cluster
spec:
  kafka:
    version: 3.6.0
    replicas: 1  # Single broker for local dev (use 3 for production)
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
    storage:
      type: ephemeral  # Use persistent-claim for data retention
  zookeeper:
    replicas: 1
    storage:
      type: ephemeral
  entityOperator:
    topicOperator: {}
    userOperator: {}
EOF

# Wait for Kafka cluster to be ready (takes 2-3 minutes)
kubectl wait kafka/my-cluster --for=condition=Ready --timeout=300s -n kafka

# Verify Kafka pods are running
kubectl get pods -n kafka
```

**Expected Output**:
```
NAME                                          READY   STATUS    RESTARTS   AGE
my-cluster-entity-operator-xxxxx              3/3     Running   0          1m
my-cluster-kafka-0                            1/1     Running   0          2m
my-cluster-zookeeper-0                        1/1     Running   0          3m
strimzi-cluster-operator-xxxxx                1/1     Running   0          5m
```

**Create Kafka Topics**:
```bash
# Create todo-created topic
cat <<EOF | kubectl apply -n kafka -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo-created
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000  # 7 days
    segment.bytes: 1073741824
EOF

# Create todo-updated topic
kubectl apply -n kafka -f - <<EOF
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo-updated
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000
EOF

# Create todo-deleted topic
kubectl apply -n kafka -f - <<EOF
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo-deleted
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000
EOF

# Create todo-reminder topic
kubectl apply -n kafka -f - <<EOF
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo-reminder
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000
EOF

# Verify topics are ready
kubectl get kafkatopics -n kafka
```

---

## Step 4: Deploy Redis for State Store

Deploy Redis as the Dapr State Store backend:

```bash
# Add Bitnami Helm repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install Redis (single instance for dev, disable auth for simplicity)
helm install redis bitnami/redis \
  --set auth.enabled=false \
  --set master.persistence.enabled=false \
  --set replica.replicaCount=0

# Verify Redis is running
kubectl get pods | grep redis
```

**Expected Output**:
```
redis-master-0      1/1     Running   0          1m
```

**Test Redis Connection** (optional):
```bash
# Port forward to Redis
kubectl port-forward svc/redis-master 6379:6379 &

# Test connection with redis-cli (if installed)
redis-cli -h localhost ping
# Expected: PONG
```

---

## Step 5: Deploy Dapr Components

Create Dapr component definitions for Pub/Sub (Kafka), State Store (Redis), and Secrets (Kubernetes):

```bash
# Create Dapr Pub/Sub component (Kafka backend)
cat <<EOF | kubectl apply -f -
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092"
    - name: consumerGroup
      value: "backend-group"
    - name: clientId
      value: "todo-backend"
    - name: authType
      value: "none"
EOF

# Create Dapr State Store component (Redis backend)
cat <<EOF | kubectl apply -f -
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore-redis
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "redis-master:6379"
    - name: enableTLS
      value: "false"
EOF

# Create Dapr Secrets component (Kubernetes Secrets backend)
cat <<EOF | kubectl apply -f -
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
EOF

# Verify components are created
kubectl get components
```

**Create Dapr Subscriptions** (for backend service):
```bash
# Backend subscribes to all todo events
cat <<EOF | kubectl apply -f -
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: backend-todo-created
spec:
  pubsubname: pubsub-kafka
  topic: todo-created
  routes:
    default: /events/todo-created
---
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: backend-todo-updated
spec:
  pubsubname: pubsub-kafka
  topic: todo-updated
  routes:
    default: /events/todo-updated
---
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: backend-todo-deleted
spec:
  pubsubname: pubsub-kafka
  topic: todo-deleted
  routes:
    default: /events/todo-deleted
---
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: backend-todo-reminder
spec:
  pubsubname: pubsub-kafka
  topic: todo-reminder
  routes:
    default: /events/todo-reminder
EOF

# Verify subscriptions
kubectl get subscriptions
```

---

## Step 6: Deploy Application via Helm

**Note**: This step assumes Helm charts exist in `helm/todo-app-event-driven/`. If not yet created, this is a placeholder for Phase 2 implementation.

```bash
# Build and load Docker images into Minikube
# (assumes Dockerfiles exist in backend/ and frontend/)
eval $(minikube docker-env)
docker build -t todo-backend:dev backend/
docker build -t todo-frontend:dev frontend/

# Deploy via Helm (with Minikube-specific values)
helm install todo-app ./helm/todo-app-event-driven \
  -f helm/todo-app-event-driven/values-minikube.yaml \
  --set backend.image.tag=dev \
  --set frontend.image.tag=dev

# Wait for pods to be ready
kubectl wait --for=condition=Ready pods -l app=backend --timeout=120s
kubectl wait --for=condition=Ready pods -l app=frontend --timeout=120s

# Verify pods are running with Dapr sidecars
kubectl get pods
```

**Expected Output**:
```
NAME                        READY   STATUS    RESTARTS   AGE
backend-xxxxx               2/2     Running   0          1m   # 2/2 = app + Dapr sidecar
frontend-xxxxx              2/2     Running   0          1m   # 2/2 = app + Dapr sidecar
```

---

## Step 7: Access Application

Access the frontend via Minikube service:

```bash
# Get frontend service URL
minikube service todo-app-frontend --url

# Example output: http://127.0.0.1:54321
# Open this URL in your browser
```

**Alternative (Port Forward)**:
```bash
# Port forward to frontend service
kubectl port-forward svc/todo-app-frontend 3000:3000

# Access at http://localhost:3000
```

---

## Step 8: Validate Event Flows

Test the event-driven architecture:

### 8.1: Create a Task via Frontend

1. Open frontend URL in browser
2. Create a new task with title "Test Event Flow"
3. Check backend logs for event consumption

```bash
# Watch backend logs in real-time
kubectl logs -l app=backend --tail=100 -f
```

**Expected Log Output**:
```
2026-01-27 10:00:00 INFO Event received: todo-created
2026-01-27 10:00:00 INFO Processing event: eventId=550e8400...
2026-01-27 10:00:00 INFO Saving task to state store: todoId=550e8400...
2026-01-27 10:00:00 INFO Event processed successfully
```

### 8.2: Inspect Kafka Topics

Check Kafka topics for published events:

```bash
# Exec into Kafka broker
kubectl exec -it my-cluster-kafka-0 -n kafka -- /bin/bash

# Inside Kafka pod, consume todo-created topic from beginning
bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic todo-created \
  --from-beginning

# Expected output: CloudEvents JSON with todo-created event
# Press Ctrl+C to exit

# Check all topics
bin/kafka-topics.sh --bootstrap-server localhost:9092 --list

# Expected output:
# todo-created
# todo-updated
# todo-deleted
# todo-reminder
```

### 8.3: Verify State Store

Check Redis for stored tasks:

```bash
# Exec into Redis pod
kubectl exec -it redis-master-0 -- redis-cli

# Inside Redis CLI
KEYS task:*

# Expected output: List of task keys (e.g., task:user-123:550e8400...)

# Get task data
GET "task:user-123:550e8400..."

# Expected output: JSON task object

# Exit Redis CLI
exit
```

### 8.4: Test Dapr Dashboard

Access Dapr dashboard to visualize event flows:

```bash
# Start Dapr dashboard
dapr dashboard -k

# Open http://localhost:8080 in browser
# Navigate to:
# - Applications: See backend and frontend services
# - Components: See pubsub-kafka, statestore-redis, kubernetes-secrets
# - Control Plane: See Dapr system status
```

---

## Cleanup

Remove all deployed resources:

```bash
# Uninstall application Helm chart
helm uninstall todo-app

# Delete Dapr components and subscriptions
kubectl delete components --all
kubectl delete subscriptions --all

# Uninstall Redis
helm uninstall redis

# Delete Kafka cluster and topics
kubectl delete kafka my-cluster -n kafka
kubectl delete kafkatopics --all -n kafka

# Delete Strimzi operator
kubectl delete -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
kubectl delete namespace kafka

# Uninstall Dapr from Kubernetes
dapr uninstall --kubernetes

# Stop and delete Minikube cluster
minikube stop
minikube delete
```

---

## Troubleshooting

### Pods Stuck in Pending State

**Symptom**: Pods not starting, status "Pending"

**Diagnosis**:
```bash
kubectl describe pod <pod-name>
```

**Common Causes**:
- Insufficient resources (increase Minikube CPU/RAM)
- Image pull errors (rebuild images with `eval $(minikube docker-env)`)
- PVC not bound (check storage class)

**Solution**:
```bash
# Restart Minikube with more resources
minikube delete
minikube start --cpus=6 --memory=12g
```

### Dapr Sidecar Not Injecting

**Symptom**: Pods show 1/1 READY instead of 2/2

**Diagnosis**:
```bash
kubectl describe pod <pod-name> | grep dapr
```

**Solution**:
- Verify Dapr annotations in deployment YAML:
  ```yaml
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "backend"
    dapr.io/app-port: "8000"
  ```
- Reinstall Dapr control plane:
  ```bash
  dapr uninstall --kubernetes
  dapr init --kubernetes --wait
  ```

### Kafka Topics Not Creating

**Symptom**: KafkaTopic resources stuck in "NotReady"

**Diagnosis**:
```bash
kubectl get kafkatopics -n kafka
kubectl describe kafkatopic todo-created -n kafka
```

**Solution**:
- Ensure Kafka cluster is fully ready:
  ```bash
  kubectl wait kafka/my-cluster --for=condition=Ready --timeout=300s -n kafka
  ```
- Check Strimzi operator logs:
  ```bash
  kubectl logs -n kafka deployment/strimzi-cluster-operator
  ```

### Events Not Flowing

**Symptom**: Frontend creates task, but backend doesn't log event consumption

**Diagnosis**:
1. Check Dapr Pub/Sub component:
   ```bash
   kubectl get component pubsub-kafka -o yaml
   ```
2. Check Dapr subscriptions:
   ```bash
   kubectl get subscriptions
   ```
3. Check Kafka consumer groups:
   ```bash
   kubectl exec -it my-cluster-kafka-0 -n kafka -- \
     bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list
   ```

**Solution**:
- Verify Kafka broker address in Pub/Sub component matches:
  ```
  my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092
  ```
- Check backend logs for Dapr subscription errors:
  ```bash
  kubectl logs -l app=backend -c daprd
  ```

---

## Next Steps

1. ✅ Minikube environment deployed successfully
2. → Implement backend event handlers (`/events/*` endpoints)
3. → Implement frontend task management UI
4. → Test end-to-end event flows (create/update/delete tasks)
5. → Validate Dapr Jobs API for reminders
6. → Run integration tests locally
7. → Prepare for OKE production deployment

---

**Quickstart Status**: ✅ Complete
**Estimated Setup Time**: 15-20 minutes (excluding downloads)
**Next Document**: OKE production deployment guide (to be created in Phase 2)

# Local Development Guide (T126)

Guide for setting up and developing the Todo App Phase 5 locally with Minikube.

## Prerequisites

### Required Software

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) v1.30+
- [kubectl](https://kubernetes.io/docs/tasks/tools/) v1.28+
- [Helm](https://helm.sh/docs/intro/install/) v3.12+
- [Dapr CLI](https://docs.dapr.io/getting-started/install-dapr-cli/) v1.12+
- [Python](https://www.python.org/downloads/) 3.12+
- [Node.js](https://nodejs.org/) 20+
- [UV](https://github.com/astral-sh/uv) (Python package manager)

### System Requirements

- CPU: 4 cores minimum (8 recommended)
- RAM: 8 GB minimum (16 GB recommended)
- Disk: 20 GB free space

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/your-org/todo-app.git
cd todo-app
```

### 2. Start Minikube

```bash
# Start with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Verify
minikube status
```

### 3. Deploy Infrastructure

Run the automated deployment script:

```bash
./scripts/deploy-minikube.sh
```

**This script will**:
- Install Strimzi Kafka Operator
- Deploy Kafka cluster
- Create Kafka topics
- Install Dapr control plane
- Deploy Redis
- Build Docker images
- Deploy application with Helm

**Estimated time**: 20-30 minutes

### 4. Verify Deployment

```bash
# Check pods
kubectl get pods

# You should see:
# - todo-app-backend (2/2 Running)
# - todo-app-frontend (2/2 Running)
# - redis-master (1/1 Running)
# - Kafka pods (in kafka namespace)
# - Dapr pods (in dapr-system namespace)
```

### 5. Access Application

```bash
# Get frontend URL
minikube service todo-app-frontend --url

# Open in browser (example output):
# http://192.168.49.2:30000

# Port-forward backend API (alternative)
kubectl port-forward svc/todo-app-backend 8000:8000
```

## Development Workflow

### Backend Development

#### Setup Python Environment

```bash
cd backend

# Install UV (if not installed)
pip install uv

# Create virtual environment
uv venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Linux/Mac
# .venv\Scripts\activate  # On Windows

# Install dependencies
uv pip install --python .venv/bin/python -e .[dev]
```

#### Run Backend Locally (Standalone)

```bash
# Set environment variables
export DAPR_HTTP_PORT=3500
export DAPR_GRPC_PORT=50001

# Run with Dapr sidecar
dapr run --app-id backend \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --components-path ./dapr/components \
  -- uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Run Backend Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests (requires Kafka and Redis running)
pytest tests/integration/ -v

# E2E tests (requires full deployment)
pytest tests/e2e/ -v

# With coverage
pytest --cov=src --cov-report=html
```

#### Code Quality

```bash
# Linting
ruff check src/

# Formatting
black src/

# Type checking
mypy src/
```

### Frontend Development

#### Setup Node Environment

```bash
cd frontend

# Install dependencies
npm install

# or
yarn install
```

#### Run Frontend Locally

```bash
# Development mode
npm run dev

# Open http://localhost:3000
```

#### Run Frontend Tests

```bash
# Unit tests
npm test

# E2E tests (Playwright)
npm run test:e2e

# Linting
npm run lint
```

### Hot Reload in Minikube

For faster development iteration:

#### Backend Hot Reload

```bash
# Use skaffold or tilt for auto-rebuild and deploy
# Or manually:

# 1. Make code changes
# 2. Rebuild image
eval $(minikube docker-env)
cd backend
docker build -t todo-backend:dev .

# 3. Restart deployment
kubectl rollout restart deployment/todo-app-backend
```

#### Frontend Hot Reload

```bash
# Build and restart
eval $(minikube docker-env)
cd frontend
docker build -t todo-frontend:dev -f ../docker/frontend/Dockerfile .
kubectl rollout restart deployment/todo-app-frontend
```

## Testing Event Flow

### Create a Task

```bash
# Port-forward backend
kubectl port-forward svc/todo-app-backend 8000:8000

# Create task via API
curl -X POST http://localhost:8000/api/v1/events/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test-user",
    "title": "Test Event Flow",
    "priority": "high",
    "tags": ["test"],
    "dueDate": "2026-12-31T23:59:59Z"
  }'
```

### Verify Event Processing

```bash
# Check backend logs
kubectl logs -l app=backend -c backend --tail=50 -f

# You should see:
# ✅ Published event to topic 'todo-created'
# 📩 Received todo-created event
# ✅ Created task ... in State Store

# Check Kafka topics
./scripts/inspect-kafka-topics.sh
```

### Verify State Store

```bash
# Get task from Redis
TASK_ID="<task-id-from-create-response>"
kubectl exec -it redis-master-0 -- redis-cli GET "task:${TASK_ID}"
```

## Debugging

### View Logs

```bash
# Backend application logs
kubectl logs -l app=backend -c backend --tail=100 -f

# Backend Dapr sidecar logs
kubectl logs -l app=backend -c daprd --tail=100 -f

# Frontend logs
kubectl logs -l app=frontend -c frontend --tail=100 -f

# Kafka logs
kubectl logs -n kafka -l app.kubernetes.io/name=kafka --tail=100

# Redis logs
kubectl logs redis-master-0
```

### Debug Dapr Components

```bash
# Check component status
kubectl get components

# Describe component
kubectl describe component pubsub-kafka

# Test Pub/Sub directly
kubectl exec -it <backend-pod> -c daprd -- \
  curl -X POST http://localhost:3500/v1.0/publish/pubsub-kafka/todo-created \
  -H "Content-Type: application/json" \
  -d '{"eventId": "test", "todoId": "123", "userId": "user1", "payload": {}}'

# Test State Store
kubectl exec -it <backend-pod> -c daprd -- \
  curl http://localhost:3500/v1.0/state/statestore-redis/task:123
```

### Interactive Debugging

#### Backend (Python)

Add breakpoint in code:

```python
import debugpy

# In your code
debugpy.listen(("0.0.0.0", 5678))
print("Waiting for debugger...")
debugpy.wait_for_client()
```

Then:

```bash
# Port-forward debug port
kubectl port-forward <backend-pod> 5678:5678

# Attach VS Code debugger to localhost:5678
```

#### Frontend (Node.js)

```bash
# Run with inspect flag
kubectl exec -it <frontend-pod> -c frontend -- \
  node --inspect=0.0.0.0:9229 /app/server.js

# Port-forward
kubectl port-forward <frontend-pod> 9229:9229

# Attach Chrome DevTools to localhost:9229
```

## Common Issues

### Minikube Won't Start

```bash
# Delete and recreate
minikube delete
minikube start --cpus=4 --memory=8192 --driver=docker

# If using VirtualBox
minikube start --cpus=4 --memory=8192 --driver=virtualbox
```

### Pods Stuck in ImagePullBackOff

```bash
# Set Docker environment
eval $(minikube docker-env)

# Rebuild images
cd backend && docker build -t todo-backend:phase5 .
cd ../frontend && docker build -t todo-frontend:latest -f ../docker/frontend/Dockerfile .

# Verify images exist
minikube ssh docker images | grep todo
```

### Dapr Sidecar Not Injecting

```bash
# Check Dapr installation
dapr status -k

# Reinstall if needed
dapr uninstall --kubernetes
dapr init --kubernetes --wait

# Verify annotations on deployment
kubectl get deployment todo-app-backend -o yaml | grep dapr.io
```

### Kafka Connection Errors

```bash
# Check Kafka pods
kubectl get pods -n kafka

# Restart Kafka cluster
kubectl delete pod -n kafka -l app.kubernetes.io/name=kafka

# Recreate topics
KAFKA_POD=$(kubectl get pod -n kafka -l app.kubernetes.io/name=kafka -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n kafka $KAFKA_POD -- bin/kafka-topics.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --create --topic todo-created --partitions 1 --replication-factor 1
```

### Redis Connection Errors

```bash
# Check Redis pod
kubectl get pods -l app.kubernetes.io/name=redis

# Test connectivity
kubectl exec -it redis-master-0 -- redis-cli ping

# Restart Redis
helm uninstall redis
helm install redis bitnami/redis --set auth.enabled=false
```

## Running E2E Tests

### Setup

```bash
# Ensure backend is accessible
kubectl port-forward svc/todo-app-backend 8000:8000 &
```

### Run Tests

```bash
cd backend/tests/e2e

# Run all tests
bash run_all_tests.sh

# Run individual test
python test_event_flow_create.py
python test_event_flow_update.py
python test_event_flow_delete.py
python test_event_flow_reminder.py
python test_idempotency.py
python test_concurrency.py
```

## Clean Up

### Delete Application

```bash
helm uninstall todo-app
```

### Delete Infrastructure

```bash
# Delete Kafka
kubectl delete kafka my-cluster -n kafka
kubectl delete namespace kafka

# Delete Redis
helm uninstall redis

# Delete Dapr
dapr uninstall --kubernetes
```

### Stop Minikube

```bash
minikube stop

# Or delete completely
minikube delete
```

## Tips & Best Practices

### Performance

1. **Allocate enough resources** to Minikube (4 CPU, 8GB RAM minimum)
2. **Use local Docker images** to avoid pull delays
3. **Enable caching** for faster rebuilds
4. **Use skaffold or tilt** for automated rebuild/redeploy

### Development

1. **Use feature branches** for development
2. **Run tests locally** before committing
3. **Check logs** frequently during development
4. **Use Dapr dashboard** for visualization

### Troubleshooting

1. **Check pod status first**: `kubectl get pods`
2. **Read logs**: `kubectl logs <pod> -c <container>`
3. **Describe resources**: `kubectl describe pod <pod>`
4. **Use Dapr CLI**: `dapr logs -k -a backend`

## Additional Resources

- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Dapr Local Development](https://docs.dapr.io/operations/hosting/kubernetes/kubernetes-development/)
- [Kafka on Kubernetes](https://strimzi.io/docs/operators/latest/quickstart.html)
- [VS Code Kubernetes Extension](https://marketplace.visualstudio.com/items?itemName=ms-kubernetes-tools.vscode-kubernetes-tools)

## Next Steps

1. Set up IDE with Kubernetes extension
2. Configure debugger for backend and frontend
3. Write additional unit and integration tests
4. Implement new features following event-driven patterns
5. Deploy to staging/production (OKE)

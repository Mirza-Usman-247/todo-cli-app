# Quick Start Guide: Phase IV Local Kubernetes Deployment

**Feature**: 001-local-k8s-deploy
**Date**: 2026-01-21
**Audience**: Developers deploying Todo Chatbot to local Minikube

---

## Prerequisites

Before starting deployment, ensure the following tools are installed and configured:

### Required Tools

| Tool | Version | Installation | Verification |
|------|---------|--------------|--------------|
| **Docker Desktop** | Latest | [Download](https://www.docker.com/products/docker-desktop) | `docker --version` |
| **Minikube** | 1.28+ | [Installation Guide](https://minikube.sigs.k8s.io/docs/start/) | `minikube version` |
| **kubectl** | 1.28+ | Included with Docker Desktop or [standalone](https://kubernetes.io/docs/tasks/tools/) | `kubectl version --client` |
| **Helm** | 3.12+ | [Installation Guide](https://helm.sh/docs/intro/install/) | `helm version` |

### Optional AI DevOps Tools

| Tool | Purpose | Installation | Notes |
|------|---------|--------------|-------|
| **kubectl-ai** | AI-assisted kubectl commands | `kubectl krew install ai` | Requires OpenAI API key |
| **kagent** | Cluster health analysis | Via MCP server | Optional for advanced monitoring |
| **Gordon** | Docker AI agent | Docker Desktop AI (region-dependent) | Fallback: Claude Code generates Dockerfiles |

### System Requirements

```yaml
Minikube Configuration:
  CPU: 4 cores minimum
  Memory: 8GB minimum
  Disk: 30GB minimum
  Driver: docker (recommended for WSL2/native Docker)
```

**Configure Minikube resources**:
```bash
minikube config set cpus 4
minikube config set memory 8192
minikube config set disk-size 30g
```

---

## Deployment Workflow

### Phase 0: Environment Setup

#### Step 0.1: Verify Prerequisites

```bash
# Check Docker is running
docker ps

# Verify Minikube is installed
minikube version

# Verify kubectl is installed
kubectl version --client

# Verify Helm is installed
helm version
```

#### Step 0.2: Start Minikube

```bash
# Start Minikube cluster with appropriate resources
minikube start --cpus=4 --memory=8192 --disk-size=30g

# Verify cluster is running
minikube status

# Set kubectl context to minikube
kubectl config use-context minikube

# Verify connection
kubectl get nodes
# Expected output: minikube   Ready    control-plane   <age>
```

#### Step 0.3: Enable Optional Addons (Recommended)

```bash
# Enable metrics-server for resource monitoring
minikube addons enable metrics-server

# Verify addon status
minikube addons list | grep metrics-server
# Expected: metrics-server: enabled
```

---

### Phase 1: Build Container Images

#### Step 1.1: Configure Docker Environment for Minikube

```bash
# Point Docker client to Minikube's Docker daemon
# This ensures images are built directly in Minikube's registry
eval $(minikube docker-env)

# Verify Docker environment is set
echo $DOCKER_HOST
# Expected: tcp://127.0.0.1:<port> or similar
```

**Important**: Every new terminal session needs to run `eval $(minikube docker-env)` to use Minikube's Docker daemon.

#### Step 1.2: Build Frontend Container Image

**Option A: Using Claude Code (Recommended Fallback)**

1. Request Claude Code to generate a multi-stage Dockerfile for the Next.js frontend:
   ```
   User: Generate a production-ready multi-stage Dockerfile for the frontend Next.js application in ./frontend
   ```

2. Claude will create `docker/frontend/Dockerfile` with optimizations

3. Build the image:
   ```bash
   docker build -t todo-chatbot-frontend:latest -f docker/frontend/Dockerfile ./frontend
   ```

**Option B: Using Gordon (If Available)**

```bash
# Request Gordon to create optimized Dockerfile
# "Gordon, create a multi-stage Dockerfile for my Next.js frontend at ./frontend with production optimizations"

# Build image once Dockerfile is generated
docker build -t todo-chatbot-frontend:latest -f docker/frontend/Dockerfile ./frontend
```

**Validation**:
```bash
# Verify image was created
docker images | grep todo-chatbot-frontend

# Expected output:
# todo-chatbot-frontend   latest   <image-id>   <time>   <size>

# Verify image size is reasonable (< 500MB recommended)
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep todo-chatbot-frontend
```

#### Step 1.3: Build Backend Container Image

**Option A: Using Claude Code (Recommended Fallback)**

1. Request Claude Code to generate a Dockerfile for the Python backend:
   ```
   User: Generate a production-ready Dockerfile for the backend FastAPI application in ./backend using Python 3.13 and UV package manager
   ```

2. Claude will create `docker/backend/Dockerfile`

3. Build the image:
   ```bash
   docker build -t todo-chatbot-backend:latest -f docker/backend/Dockerfile ./backend
   ```

**Option B: Using Gordon (If Available)**

```bash
# Request Gordon to create optimized Dockerfile
# "Gordon, create a Dockerfile for my Python 3.13 FastAPI backend at ./backend using UV for dependency management"

# Build image once Dockerfile is generated
docker build -t todo-chatbot-backend:latest -f docker/backend/Dockerfile ./backend
```

**Validation**:
```bash
# Verify image was created
docker images | grep todo-chatbot-backend

# Expected output:
# todo-chatbot-backend   latest   <image-id>   <time>   <size>

# Verify image size is reasonable (< 800MB recommended)
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep todo-chatbot-backend
```

#### Step 1.4: Test Images Locally (Optional)

```bash
# Test frontend container
docker run --rm -p 3000:3000 todo-chatbot-frontend:latest
# Open browser: http://localhost:3000

# Test backend container (in separate terminal)
docker run --rm -p 8000:8000 \
  -e PORT=8000 \
  -e NODE_ENV=development \
  -e JWT_SECRET=test-secret \
  -e BETTER_AUTH_SECRET=test-secret \
  todo-chatbot-backend:latest
# Open browser: http://localhost:8000/health

# Stop containers: Ctrl+C in each terminal
```

---

### Phase 2: Create Helm Chart

#### Step 2.1: Create Helm Chart Structure

**Option A: Using Claude Code (Recommended)**

Request Claude Code to generate the complete Helm chart based on the contract specifications:
```
User: Generate Helm chart for todo-chatbot based on contracts in specs/001-local-k8s-deploy/contracts/
```

Claude will create:
- `helm/todo-chatbot/Chart.yaml`
- `helm/todo-chatbot/values.yaml`
- `helm/todo-chatbot/templates/` (all manifests)

**Option B: Manual Creation**

```bash
# Create chart scaffolding
helm create helm/todo-chatbot

# Replace default templates with contract-based manifests
# (See contracts/ directory for specifications)
```

#### Step 2.2: Validate Helm Chart

```bash
# Lint chart for syntax errors
helm lint ./helm/todo-chatbot

# Expected output:
# ==> Linting ./helm/todo-chatbot
# [INFO] Chart.yaml: icon is recommended
# 1 chart(s) linted, 0 chart(s) failed

# Test template rendering
helm template todo-chatbot ./helm/todo-chatbot

# Expected: Valid Kubernetes YAML manifests output

# Dry-run installation (validates against Kubernetes API)
helm install todo-chatbot ./helm/todo-chatbot -n todo-app --create-namespace --dry-run --debug

# Expected: No errors, shows resources that would be created
```

---

### Phase 3: Deploy to Minikube

#### Step 3.1: Install Helm Chart

```bash
# Install chart to todo-app namespace
helm install todo-chatbot ./helm/todo-chatbot -n todo-app --create-namespace

# Expected output:
# NAME: todo-chatbot
# LAST DEPLOYED: <timestamp>
# NAMESPACE: todo-app
# STATUS: deployed
# REVISION: 1
# TEST SUITE: None
# NOTES:
# <Post-install instructions from NOTES.txt>
```

#### Step 3.2: Verify Deployment

```bash
# Check Helm release status
helm status todo-chatbot -n todo-app

# Check all resources created
kubectl get all -n todo-app

# Expected output:
# NAME                                       READY   STATUS    RESTARTS   AGE
# pod/todo-chatbot-frontend-<hash>          1/1     Running   0          1m
# pod/todo-chatbot-backend-<hash>           1/1     Running   0          1m
#
# NAME                              TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
# service/todo-chatbot-frontend     LoadBalancer   10.96.xxx.xxx   <pending>     80:30001/TCP   1m
# service/todo-chatbot-backend      LoadBalancer   10.96.xxx.xxx   <pending>     80:30002/TCP   1m
#
# NAME                                    READY   UP-TO-DATE   AVAILABLE   AGE
# deployment.apps/todo-chatbot-frontend   1/1     1            1           1m
# deployment.apps/todo-chatbot-backend    1/1     1            1           1m

# Check pod logs for startup success
kubectl logs -n todo-app deployment/todo-chatbot-frontend --tail=20
kubectl logs -n todo-app deployment/todo-chatbot-backend --tail=20
```

**Troubleshooting Pod Issues**:
```bash
# If pods are not Running, describe them
kubectl describe pod <pod-name> -n todo-app

# Check events for errors
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Common issues:
# - ImagePullBackOff: Run `eval $(minikube docker-env)` and rebuild images
# - CrashLoopBackOff: Check logs with `kubectl logs <pod-name> -n todo-app`
# - Pending: Check resource constraints with `kubectl describe node minikube`
```

---

### Phase 4: Expose Services Locally

#### Step 4.1: Start Minikube Tunnel

```bash
# Start tunnel in a separate terminal (requires sudo on some systems)
minikube tunnel

# Expected output:
# Status:
# 	machine: minikube
# 	pid: <pid>
# 	route: 10.96.0.0/12 -> 192.168.xx.xx
# 	minikube: Running
# 	services: [todo-chatbot-frontend, todo-chatbot-backend]
#     errors:
# 		minikube: no errors
# 		router: no errors
# 		loadbalancer emulator: no errors
```

**Leave tunnel running** in this terminal for the duration of your development session.

#### Step 4.2: Verify Service Accessibility

```bash
# Check LoadBalancer external IPs (in new terminal)
kubectl get svc -n todo-app

# Expected output:
# NAME                      TYPE           CLUSTER-IP      EXTERNAL-IP      PORT(S)        AGE
# todo-chatbot-frontend     LoadBalancer   10.96.xxx.xxx   127.0.0.1        80:30001/TCP   5m
# todo-chatbot-backend      LoadBalancer   10.96.xxx.xxx   127.0.0.1        80:30002/TCP   5m

# Test frontend accessibility
curl -f http://localhost:3000
# Expected: HTTP 200 with HTML content

# Test backend health endpoint
curl -f http://localhost:8000/health
# Expected: HTTP 200 with health status JSON
```

#### Step 4.3: Access Application in Browser

1. **Frontend**: Open http://localhost:3000 in your browser
   - Should display Todo Chatbot UI
   - Test creating a todo item

2. **Backend API**: Open http://localhost:8000/health
   - Should return JSON: `{"status": "healthy"}` (or similar)

3. **Verify Frontend-Backend Communication**:
   - In frontend UI, create a new todo item
   - Verify it persists (indicating backend API is reachable)

---

### Phase 5: AI-Assisted Operations (Optional)

#### Step 5.1: kubectl-ai Usage Examples

**Prerequisites**: Install kubectl-ai and set OpenAI API key
```bash
# Install kubectl-ai via krew
kubectl krew install ai

# Set API key
export OPENAI_API_KEY=<your-key>
```

**Example Commands**:
```bash
# Scale frontend deployment
kubectl-ai "scale todo-chatbot-frontend deployment to 3 replicas in todo-app namespace"

# Debugging
kubectl-ai "why are my frontend pods not running in todo-app namespace?"

# Resource inspection
kubectl-ai "show me resource usage for all pods in todo-app namespace"

# Manual fallback for scaling:
kubectl scale deployment todo-chatbot-frontend --replicas=3 -n todo-app
```

#### Step 5.2: kagent Usage Examples (If Available)

```bash
# Analyze cluster health
kagent "analyze cluster health for todo-app namespace"

# Optimization suggestions
kagent "suggest resource limits for todo-chatbot-backend based on actual usage"

# Diagnostics
kagent "diagnose why backend pods are restarting in todo-app namespace"

# Manual fallback for diagnostics:
kubectl top pods -n todo-app
kubectl describe pod <pod-name> -n todo-app
kubectl logs <pod-name> -n todo-app --previous
```

---

## Testing & Validation

### Deployment Validation Tests

```bash
# Test 1: All pods are Running
kubectl get pods -n todo-app --field-selector=status.phase=Running
# Expected: Both frontend and backend pods listed

# Test 2: Zero restarts
kubectl get pods -n todo-app -o jsonpath='{.items[*].status.containerStatuses[*].restartCount}'
# Expected: 0 0 (all zeros)

# Test 3: Health checks passing
kubectl exec -n todo-app deployment/todo-chatbot-frontend -- curl -f http://localhost:3000/health
kubectl exec -n todo-app deployment/todo-chatbot-backend -- curl -f http://localhost:8000/health
# Expected: HTTP 200 for both

# Test 4: Services have external IPs
kubectl get svc -n todo-app -o jsonpath='{.items[*].status.loadBalancer.ingress[*].ip}'
# Expected: 127.0.0.1 127.0.0.1 (if minikube tunnel is running)

# Test 5: Resource limits enforced
kubectl describe deployment todo-chatbot-frontend -n todo-app | grep -A 5 "Limits"
kubectl describe deployment todo-chatbot-backend -n todo-app | grep -A 5 "Limits"
# Expected: CPU and memory limits as per spec
```

### Scaling Tests

```bash
# Scale frontend to 3 replicas
kubectl scale deployment todo-chatbot-frontend --replicas=3 -n todo-app

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=frontend -n todo-app --timeout=120s

# Verify 3 pods are running
kubectl get pods -n todo-app -l app.kubernetes.io/component=frontend
# Expected: 3 pods in Running state

# Scale back to 1 replica
kubectl scale deployment todo-chatbot-frontend --replicas=1 -n todo-app
```

### Pod Recovery Tests

```bash
# Delete a frontend pod
kubectl delete pod -n todo-app -l app.kubernetes.io/component=frontend --field-selector=status.phase=Running | head -1

# Wait for new pod to start
kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=frontend -n todo-app --timeout=120s

# Verify new pod is running
kubectl get pods -n todo-app -l app.kubernetes.io/component=frontend
# Expected: 1 pod in Running state (new pod with different hash)
```

---

## Common Operations

### Viewing Logs

```bash
# Stream frontend logs
kubectl logs -f -n todo-app deployment/todo-chatbot-frontend

# Stream backend logs
kubectl logs -f -n todo-app deployment/todo-chatbot-backend

# View logs from all pods
kubectl logs -n todo-app --all-containers=true --prefix=true -f
```

### Updating Configuration

```bash
# Edit values.yaml with new configuration
vim helm/todo-chatbot/values.yaml

# Upgrade Helm release with new values
helm upgrade todo-chatbot ./helm/todo-chatbot -n todo-app

# Rollback if needed
helm rollback todo-chatbot -n todo-app
```

### Rebuilding and Redeploying Images

```bash
# Ensure Docker env is set to Minikube
eval $(minikube docker-env)

# Rebuild frontend image
docker build -t todo-chatbot-frontend:latest -f docker/frontend/Dockerfile ./frontend

# Rebuild backend image
docker build -t todo-chatbot-backend:latest -f docker/backend/Dockerfile ./backend

# Restart deployments to pick up new images
kubectl rollout restart deployment/todo-chatbot-frontend -n todo-app
kubectl rollout restart deployment/todo-chatbot-backend -n todo-app

# Verify rollout status
kubectl rollout status deployment/todo-chatbot-frontend -n todo-app
kubectl rollout status deployment/todo-chatbot-backend -n todo-app
```

---

## Cleanup

### Uninstall Helm Release

```bash
# Uninstall todo-chatbot release
helm uninstall todo-chatbot -n todo-app

# Verify all resources removed
kubectl get all -n todo-app
# Expected: No resources found

# Delete namespace (optional)
kubectl delete namespace todo-app
```

### Stop Minikube Cluster

```bash
# Stop tunnel (Ctrl+C in tunnel terminal)

# Stop Minikube cluster (preserves cluster state)
minikube stop

# Delete Minikube cluster (removes all data)
minikube delete
```

### Reset Docker Environment

```bash
# Reset Docker environment to local (not Minikube)
eval $(minikube docker-env -u)

# Verify Docker is using local daemon
echo $DOCKER_HOST
# Expected: empty or local socket
```

---

## Troubleshooting Guide

### Issue: Pods Stuck in Pending

**Symptoms**:
```bash
kubectl get pods -n todo-app
# NAME                                   READY   STATUS    RESTARTS   AGE
# todo-chatbot-frontend-xxx             0/1     Pending   0          5m
```

**Diagnosis**:
```bash
kubectl describe pod <pod-name> -n todo-app | grep Events -A 10
```

**Common Causes & Solutions**:
1. **Insufficient resources**: Increase Minikube allocation
   ```bash
   minikube stop
   minikube config set memory 8192
   minikube config set cpus 4
   minikube start
   ```

2. **Node not ready**: Check node status
   ```bash
   kubectl get nodes
   minikube status
   ```

---

### Issue: Pods in CrashLoopBackOff

**Symptoms**:
```bash
kubectl get pods -n todo-app
# NAME                                   READY   STATUS             RESTARTS   AGE
# todo-chatbot-backend-xxx              0/1     CrashLoopBackOff   5          3m
```

**Diagnosis**:
```bash
# Check recent logs
kubectl logs <pod-name> -n todo-app --tail=50

# Check previous container logs (if restarted)
kubectl logs <pod-name> -n todo-app --previous
```

**Common Causes & Solutions**:
1. **Missing environment variables**: Verify ConfigMap and Secret
   ```bash
   kubectl get configmap todo-chatbot-config -n todo-app -o yaml
   kubectl get secret todo-chatbot-secret -n todo-app -o yaml
   ```

2. **Application startup error**: Check application logs for stack traces

3. **Health check failing too early**: Increase `initialDelaySeconds` in values.yaml

---

### Issue: ImagePullBackOff

**Symptoms**:
```bash
kubectl get pods -n todo-app
# NAME                                   READY   STATUS             RESTARTS   AGE
# todo-chatbot-frontend-xxx             0/1     ImagePullBackOff   0          2m
```

**Diagnosis**:
```bash
kubectl describe pod <pod-name> -n todo-app | grep "Failed to pull image"
```

**Solution**:
```bash
# Ensure Docker env is set to Minikube
eval $(minikube docker-env)

# Verify images exist in Minikube registry
docker images | grep todo-chatbot

# If missing, rebuild images
docker build -t todo-chatbot-frontend:latest -f docker/frontend/Dockerfile ./frontend
docker build -t todo-chatbot-backend:latest -f docker/backend/Dockerfile ./backend
```

---

### Issue: LoadBalancer Services Have No External IP

**Symptoms**:
```bash
kubectl get svc -n todo-app
# NAME                      TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
# todo-chatbot-frontend     LoadBalancer   10.96.xxx.xxx   <pending>     80:30001/TCP   5m
```

**Solution**:
```bash
# Start Minikube tunnel (in separate terminal)
minikube tunnel

# Verify external IPs assigned
kubectl get svc -n todo-app
# Expected: EXTERNAL-IP shows 127.0.0.1
```

---

## Next Steps

After successful deployment, proceed to:

1. **Explore AI-assisted operations**: Test kubectl-ai and kagent commands for deployment management
2. **Run validation tests**: Execute test cases from contracts/ specifications
3. **Generate tasks.md**: Use `/sp.tasks` to break down implementation into actionable tasks
4. **Implement Phase IV**: Follow tasks.md for complete deployment automation

---

## Quick Reference

### Essential Commands

```bash
# Minikube
minikube start --cpus=4 --memory=8192
minikube status
minikube tunnel
minikube stop
minikube delete

# Docker (Minikube context)
eval $(minikube docker-env)
docker build -t <image>:<tag> <path>
docker images | grep todo-chatbot

# Helm
helm install <release> <chart> -n <namespace> --create-namespace
helm upgrade <release> <chart> -n <namespace>
helm uninstall <release> -n <namespace>
helm lint <chart>
helm template <chart>

# kubectl
kubectl get all -n todo-app
kubectl get pods -n todo-app
kubectl logs -f deployment/<name> -n todo-app
kubectl describe pod <pod-name> -n todo-app
kubectl exec -it <pod-name> -n todo-app -- /bin/sh
kubectl scale deployment <name> --replicas=<count> -n todo-app
```

---

**Last Updated**: 2026-01-21
**Status**: Quickstart complete, ready for implementation

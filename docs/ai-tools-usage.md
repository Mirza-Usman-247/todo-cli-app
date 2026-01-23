# AI Tools Usage Guide - Phase IV Deployment

**Created**: 2026-01-23
**Phase**: IV - Local Kubernetes Deployment

## Overview

This document provides guidance on AI-assisted DevOps tooling for Phase IV deployment, including usage examples and manual fallback procedures for each tool.

## Tool Availability Status

### Gordon (Docker AI Agent)
**Status**: ❌ Not Available (Region-dependent feature in Docker Desktop)
**Fallback**: ✅ Claude Code-generated Dockerfiles (PRIMARY APPROACH)

**Implementation**: All Dockerfiles in `docker/frontend/Dockerfile` and `docker/backend/Dockerfile` were generated using Claude Code following Phase IV specifications.

### kubectl-ai (AI-Assisted Kubernetes Operations)
**Status**: ❌ Not Installed (Optional tool)
**Installation**: `kubectl krew install ai` (requires krew plugin manager)
**Fallback**: ✅ Manual kubectl commands (DOCUMENTED BELOW)

### kagent (Cluster Health Analysis)
**Status**: ❌ Not Installed (Optional tool)
**Integration**: MCP-based cluster analysis tool
**Fallback**: ✅ Manual kubectl top and inspection commands (DOCUMENTED BELOW)

---

## AI Tool Usage Examples with Manual Fallbacks

### 1. Container Image Generation

#### Gordon (Not Available)
```bash
# Gordon would be used like:
# gordon generate dockerfile for ./frontend
```

#### ✅ Fallback: Claude Code
**Approach**: Use Claude Code to generate production-ready Dockerfiles with specifications:
- Frontend: Multi-stage build with node:20-alpine
- Backend: Python 3.13-slim with UV package manager
- Non-root users, health checks, optimized layers

**Implementation**: See `docker/frontend/Dockerfile` and `docker/backend/Dockerfile`

---

### 2. Scaling Operations

#### kubectl-ai (Not Installed)
```bash
# kubectl-ai would be used like:
# kubectl-ai "scale todo-chatbot-frontend deployment to 3 replicas in todo-app namespace"
```

#### ✅ Fallback: Manual kubectl scale
```bash
# Scale frontend to 3 replicas
kubectl scale deployment todo-chatbot-frontend --replicas=3 -n todo-app

# Scale backend to 2 replicas
kubectl scale deployment todo-chatbot-backend --replicas=2 -n todo-app

# Verify scaling
kubectl get pods -n todo-app -l app.kubernetes.io/component=frontend
kubectl get pods -n todo-app -l app.kubernetes.io/component=backend

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=frontend -n todo-app --timeout=60s
```

---

### 3. Cluster Health Analysis

#### kagent (Not Installed)
```bash
# kagent would be used like:
# kagent "analyze cluster health for todo-app namespace"
# kagent "suggest resource limits for todo-chatbot-frontend based on usage"
```

#### ✅ Fallback: Manual kubectl inspection
```bash
# Get all resources in namespace
kubectl get all -n todo-app

# Check pod status
kubectl get pods -n todo-app -o wide

# View resource usage (requires metrics-server)
kubectl top nodes
kubectl top pods -n todo-app

# Check events for issues
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Inspect specific pod
kubectl describe pod <pod-name> -n todo-app

# View pod logs
kubectl logs <pod-name> -n todo-app --tail=50
kubectl logs <pod-name> -n todo-app --previous  # For crashed pods

# Resource usage comparison with limits
kubectl top pod -n todo-app -l app.kubernetes.io/component=frontend
kubectl describe deployment todo-chatbot-frontend -n todo-app | grep -A 10 "Limits"
```

---

### 4. Pod Failure Diagnosis

#### kubectl-ai (Not Installed)
```bash
# kubectl-ai would be used like:
# kubectl-ai "explain why pod <pod-name> might be in CrashLoopBackOff in todo-app namespace"
# kubectl-ai "debug connection error in todo-chatbot-backend pod"
```

#### ✅ Fallback: Manual troubleshooting
```bash
# Check pod status and events
kubectl describe pod <pod-name> -n todo-app

# View current logs
kubectl logs <pod-name> -n todo-app --tail=100

# View previous container logs (if restarted)
kubectl logs <pod-name> -n todo-app --previous

# Check environment variables
kubectl exec -it <pod-name> -n todo-app -- env

# Test connectivity from pod
kubectl exec -it <pod-name> -n todo-app -- wget -O- http://backend-service:8000/health

# Check ConfigMap and Secret references
kubectl get configmap -n todo-app -o yaml
kubectl describe secret -n todo-app
```

---

### 5. Resource Optimization

#### kagent (Not Installed)
```bash
# kagent would be used like:
# kagent "suggest resource limits for todo-chatbot-frontend based on usage"
```

#### ✅ Fallback: Manual analysis
```bash
# Enable metrics-server (if not already)
minikube addons enable metrics-server
kubectl wait --for=condition=available deployment/metrics-server -n kube-system --timeout=120s

# Get current resource usage
kubectl top pod -n todo-app

# Compare with current limits
kubectl describe deployment todo-chatbot-frontend -n todo-app | grep -A 10 "Limits"
kubectl describe deployment todo-chatbot-backend -n todo-app | grep -A 10 "Limits"

# Analyze usage patterns (run over time)
watch -n 5 'kubectl top pod -n todo-app'

# Export recommendations to file
echo "# Resource Usage Analysis" > docs/resource-optimization.md
echo "Generated: $(date)" >> docs/resource-optimization.md
echo "" >> docs/resource-optimization.md
kubectl top pod -n todo-app >> docs/resource-optimization.md
```

---

## Deployment Command Reference

### Docker Commands
```bash
# Configure Docker to use Minikube registry
eval $(minikube docker-env)

# Build images
docker build -t todo-chatbot-frontend:latest -f docker/frontend/Dockerfile ./frontend
docker build -t todo-chatbot-backend:latest -f docker/backend/Dockerfile ./backend

# Verify images
docker images | grep todo-chatbot

# Inspect image
docker inspect todo-chatbot-frontend:latest
docker inspect todo-chatbot-backend:latest
```

### Helm Commands
```bash
# Validate charts
helm lint helm/todo-chatbot

# Render templates
helm template todo-chatbot helm/todo-chatbot

# Dry-run install
helm install todo-chatbot helm/todo-chatbot -n todo-app --create-namespace --dry-run --debug

# Install chart
helm install todo-chatbot helm/todo-chatbot -n todo-app --create-namespace

# Upgrade chart
helm upgrade todo-chatbot helm/todo-chatbot -n todo-app

# View status
helm status todo-chatbot -n todo-app

# Uninstall
helm uninstall todo-chatbot -n todo-app
```

### Kubernetes Commands
```bash
# View deployments
kubectl get deployments -n todo-app

# View pods
kubectl get pods -n todo-app -o wide

# View services
kubectl get svc -n todo-app

# View ConfigMaps and Secrets
kubectl get configmap -n todo-app
kubectl get secret -n todo-app

# Start Minikube tunnel (for LoadBalancer access)
minikube tunnel  # Keep this running in separate terminal

# Port-forward (alternative to tunnel)
kubectl port-forward -n todo-app svc/todo-chatbot-frontend 3000:80
kubectl port-forward -n todo-app svc/todo-chatbot-backend 8000:80
```

---

## Testing Procedures

### Pod Restart Recovery Test
```bash
# Delete a frontend pod
kubectl delete pod -n todo-app -l app.kubernetes.io/component=frontend --field-selector=status.phase=Running | head -1

# Verify automatic recovery
kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=frontend -n todo-app --timeout=120s

# Check new pod is running
kubectl get pods -n todo-app -l app.kubernetes.io/component=frontend
```

### Scaling Test
```bash
# Scale up
kubectl scale deployment todo-chatbot-frontend --replicas=3 -n todo-app
kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=frontend -n todo-app --timeout=60s

# Verify all replicas running
kubectl get pods -n todo-app -l app.kubernetes.io/component=frontend

# Test traffic distribution
for i in {1..10}; do curl -s http://localhost:3000 > /dev/null && echo "Request $i successful"; done

# Scale down
kubectl scale deployment todo-chatbot-frontend --replicas=1 -n todo-app
```

### Health Check Test
```bash
# Frontend health
curl -f http://localhost:3000/health

# Backend health
curl -f http://localhost:8000/health

# Or via kubectl exec
kubectl exec -n todo-app deployment/todo-chatbot-frontend -- wget -O- http://localhost:3000/health
kubectl exec -n todo-app deployment/todo-chatbot-backend -- python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read())"
```

---

## Troubleshooting

For comprehensive troubleshooting procedures, see `docs/troubleshooting.md`.

**Common Issues**:
- **ImagePullBackOff**: Image not in Minikube registry → Run `eval $(minikube docker-env)` before building
- **CrashLoopBackOff**: Check logs with `kubectl logs <pod> -n todo-app --previous`
- **OOMKilled**: Increase memory limits in `helm/todo-chatbot/values.yaml`
- **Pending Pods**: Check resource availability with `kubectl describe pod <pod> -n todo-app`

---

## Summary

**Phase IV Strategy**: Manual kubectl/docker/helm commands with comprehensive documentation serve as the primary approach, with AI tools documented as optional enhancements when available.

All deployment operations in Phase IV can be performed using standard CLI tools without AI assistance.

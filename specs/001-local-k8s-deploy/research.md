# Phase 0: Research & Tooling Validation — Phase IV Local Kubernetes Deployment

**Feature**: 001-local-k8s-deploy
**Date**: 2026-01-21
**Status**: Research Complete

## Research Objectives

Validate AI DevOps tooling availability and resolve all "NEEDS CLARIFICATION" items from Technical Context before proceeding to Phase 1 design.

---

## 1. AI DevOps Tooling Validation

### 1.1 Gordon (Docker AI Agent)

**Decision**: Use Claude Code-generated Dockerfiles as PRIMARY approach (Gordon unavailable in region)

**Research Findings**:
- **Gordon Availability**: Gordon (Docker Desktop AI) is not available in all regions
- **MCP Context Status**: Gordon MCP server not accessible during Phase IV implementation
- **Fallback Strategy**: Claude Code will generate multi-stage Dockerfiles with AI-assisted optimization

**Alternative Approach**:
```yaml
Dockerfile Generation Strategy:
  Primary: Claude Code generates Dockerfiles
  Capabilities:
    - Multi-stage build optimization
    - Security best practices (non-root users, minimal base images)
    - Build caching strategies
    - Image size optimization
  Validation:
    - docker build test runs
    - Image size checks (< 500MB for frontend, < 800MB for backend)
    - Security scanning (if tools available)
```

**Rationale**: Claude Code has deep knowledge of Docker best practices and can generate production-ready Dockerfiles. The constitution allows fallback to "AI-generated Docker workflows via Claude Code" when Gordon is unavailable.

**References**:
- Docker multi-stage builds: https://docs.docker.com/build/building/multi-stage/
- Node.js Docker best practices: https://nodejs.org/en/docs/guides/nodejs-docker-webapp
- Python Docker best practices: https://docs.docker.com/language/python/

---

### 1.2 kubectl-ai (AI-Assisted Kubernetes Operations)

**Decision**: Use kubectl-ai for all Kubernetes operations with manual fallback commands documented

**Research Findings**:
- **Installation**: `kubectl krew install ai`
- **Requirements**: OpenAI API key (OPENAI_API_KEY environment variable)
- **Capabilities**: Natural language → kubectl commands, deployment creation, scaling, debugging

**Usage Patterns**:
```bash
# Deployment operations
kubectl-ai "deploy todo-chatbot-frontend with 2 replicas and expose on port 3000"

# Scaling operations
kubectl-ai "scale todo-chatbot-backend deployment to 3 replicas"

# Debugging operations
kubectl-ai "why is the frontend pod crashing?"
kubectl-ai "show me resource usage for all pods in todo-app namespace"

# Resource inspection
kubectl-ai "list all services in todo-app namespace with their endpoints"
```

**Manual Fallback Commands** (when kubectl-ai unavailable):
```bash
# Scaling
kubectl scale deployment todo-chatbot-frontend --replicas=3 -n todo-app

# Pod inspection
kubectl get pods -n todo-app -o wide
kubectl describe pod <pod-name> -n todo-app
kubectl logs <pod-name> -n todo-app --tail=100

# Resource usage
kubectl top pods -n todo-app
kubectl top nodes
```

**Rationale**: kubectl-ai accelerates operations with natural language interface while maintaining manual fallback for environments without API access.

**References**:
- kubectl-ai GitHub: https://github.com/sozercan/kubectl-ai
- kubectl krew: https://krew.sigs.k8s.io/

---

### 1.3 kagent (Cluster Health Analysis)

**Decision**: Use kagent for cluster health monitoring and optimization with manual kubectl fallbacks

**Research Findings**:
- **Capabilities**: Cluster health analysis, resource optimization, issue diagnosis
- **MCP Integration**: Uses MCP for Kubernetes context awareness
- **Limitations**: May require specific installation and configuration

**Usage Patterns**:
```bash
# Cluster health analysis
kagent "analyze cluster health for todo-app namespace"

# Resource optimization
kagent "suggest resource limits for todo-chatbot-frontend based on actual usage"
kagent "identify underutilized resources in todo-app namespace"

# Issue diagnosis
kagent "diagnose why backend pods are restarting"
kagent "check for network connectivity issues between services"
```

**Manual Fallback Analysis** (when kagent unavailable):
```bash
# Health checks
kubectl get pods -n todo-app --field-selector=status.phase!=Running
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Resource analysis
kubectl top pods -n todo-app
kubectl describe nodes

# Diagnostics
kubectl logs <pod-name> -n todo-app --previous  # Crashed pod logs
kubectl exec -it <pod-name> -n todo-app -- /bin/sh  # Pod debugging
```

**Rationale**: kagent provides intelligent cluster analysis that goes beyond raw kubectl output. Manual fallbacks ensure operations can continue without AI tools.

**References**:
- Kubernetes troubleshooting: https://kubernetes.io/docs/tasks/debug/

---

## 2. Container Base Image Selection

### 2.1 Frontend Container Base Image

**Decision**: `node:20-alpine` for multi-stage build (build + runtime stages)

**Alternatives Considered**:
1. **node:20-alpine** (SELECTED)
   - Size: ~180MB base
   - Benefits: Small footprint, official Node.js image, Alpine Linux security
   - Drawbacks: Requires native dependencies rebuild (bcrypt, etc.)

2. **node:20-slim**
   - Size: ~250MB base
   - Benefits: Debian-based, better compatibility
   - Drawbacks: Larger image size

3. **distroless/nodejs**
   - Size: ~150MB
   - Benefits: Minimal attack surface, no shell
   - Drawbacks: Harder to debug, limited ecosystem support

**Rationale**: `node:20-alpine` provides the best balance of size, compatibility, and debugging capability for local development. Multi-stage build will use full `node:20-alpine` for build stage, then copy artifacts to minimal runtime stage.

**Multi-Stage Build Strategy**:
```dockerfile
# Stage 1: Build stage (node:20-alpine)
- npm install (with build tools)
- npm run build
- Prune dev dependencies

# Stage 2: Runtime stage (nginx:alpine OR node:20-alpine slim)
- Copy build artifacts
- Expose port 3000
- Run as non-root user
```

---

### 2.2 Backend Container Base Image

**Decision**: `python:3.13-slim` with UV package manager

**Alternatives Considered**:
1. **python:3.13-slim** (SELECTED)
   - Size: ~150MB base
   - Benefits: Official Python image, Debian-based, good compatibility
   - Drawbacks: Slightly larger than alpine

2. **python:3.13-alpine**
   - Size: ~50MB base
   - Benefits: Smallest footprint
   - Drawbacks: Requires compiling many Python packages (slow builds, larger final image due to build dependencies)

3. **distroless/python3**
   - Size: ~100MB
   - Benefits: Minimal attack surface
   - Drawbacks: Harder to debug, limited UV support

**Rationale**: `python:3.13-slim` works best with UV package manager and provides faster builds than Alpine (no compilation needed). For local development, debugging capability outweighs minimal size gains.

**Container Build Strategy**:
```dockerfile
FROM python:3.13-slim
# Install UV
# Copy pyproject.toml and uv.lock
# uv sync --frozen (production dependencies only)
# Copy application code
# Run as non-root user (appuser)
# Expose port 8000
```

---

## 3. Kubernetes Service Exposure Strategy

### 3.1 Service Type Selection

**Decision**: LoadBalancer with Minikube tunnel for local access

**Alternatives Considered**:
1. **LoadBalancer with minikube tunnel** (SELECTED)
   - Access: `http://localhost:3000` (frontend), `http://localhost:8000` (backend)
   - Benefits: Simulates production LoadBalancer, clean localhost access
   - Drawbacks: Requires `minikube tunnel` running (requires sudo on some systems)

2. **NodePort**
   - Access: `http://<minikube-ip>:30001` (frontend), `http://<minikube-ip>:30002` (backend)
   - Benefits: No tunnel required, simple setup
   - Drawbacks: Non-standard ports, requires minikube IP lookup

3. **Ingress Controller**
   - Access: `http://todo.local` (with /etc/hosts entry)
   - Benefits: Production-like routing, hostname-based access
   - Drawbacks: Requires ingress addon, DNS configuration, overcomplicated for local development

**Rationale**: LoadBalancer with Minikube tunnel provides the most production-like experience while maintaining localhost convenience. Spec explicitly requires LoadBalancer service type (FR-005).

**Service Configuration**:
```yaml
Frontend Service:
  type: LoadBalancer
  port: 80 (external) → 3000 (container)

Backend Service:
  type: LoadBalancer
  port: 80 (external) → 8000 (container)

Access via minikube tunnel:
  Frontend: http://localhost:3000
  Backend: http://localhost:8000
```

---

## 4. AI Tool Fallback Strategy

### 4.1 Fallback Decision Matrix

**Decision**: AI-first with comprehensive manual fallback documentation

| Operation | Primary (AI Tool) | Fallback (Manual) | Documentation |
|-----------|-------------------|-------------------|---------------|
| **Dockerfile generation** | Claude Code | Manual Dockerfile writing | Multi-stage build templates |
| **Deployment** | kubectl-ai | `helm install` + `kubectl apply` | Helm chart README |
| **Scaling** | kubectl-ai | `kubectl scale` | Scaling guide in docs/ |
| **Debugging** | kubectl-ai + kagent | `kubectl logs/describe/exec` | Troubleshooting.md |
| **Health analysis** | kagent | `kubectl top` + metrics inspection | Health check guide |

**Rationale**: AI tools accelerate workflows but must not become single points of failure. Every AI operation has a documented manual equivalent for environments without API access or when AI tools are unavailable.

**Fallback Documentation Requirements**:
- All AI tool prompts must have manual command equivalents
- Troubleshooting guide must include non-AI debugging workflows
- Deployment guide must work with standard kubectl/helm (no AI required)

---

## 5. Resource Limit Tuning Approach

### 5.1 Resource Allocation Strategy

**Decision**: Static resource requests/limits (NO HPA for Phase IV)

**Alternatives Considered**:
1. **Static Limits** (SELECTED)
   - Frontend: requests 100m/128Mi, limits 200m/256Mi
   - Backend: requests 200m/256Mi, limits 500m/512Mi
   - Benefits: Predictable, simple, works on resource-constrained Minikube
   - Drawbacks: No automatic scaling under load

2. **Horizontal Pod Autoscaler (HPA)**
   - Auto-scale based on CPU/memory metrics
   - Benefits: Handles traffic spikes automatically
   - Drawbacks: Requires metrics-server, overcomplicated for local development, out of Phase IV scope

3. **Vertical Pod Autoscaler (VPA)**
   - Automatically adjusts resource requests/limits
   - Benefits: Optimizes resource usage over time
   - Drawbacks: Not suitable for local development, adds complexity

**Rationale**: Phase IV focuses on local development deployment. Static limits are sufficient for Minikube environments with predictable workloads. HPA/VPA are production concerns beyond current scope.

**Resource Tuning Guidelines**:
```yaml
Tuning Process:
  1. Start with conservative limits (as specified above)
  2. Monitor actual usage with: kubectl top pods -n todo-app
  3. Adjust limits if OOMKilled events occur
  4. Document recommended limits in values.yaml comments

Minikube Allocation:
  Cluster: 4 CPU, 8GB RAM minimum
  Overhead: ~1 CPU, 2GB RAM for system pods
  Available: ~3 CPU, 6GB RAM for application pods

Capacity Planning:
  2 frontend replicas: 400m CPU, 512Mi RAM total
  2 backend replicas: 1000m CPU, 1Gi RAM total
  Total application: ~1.4 CPU, 1.5Gi RAM (well within Minikube capacity)
```

---

## 6. Kubernetes Manifest Best Practices

### 6.1 Health Check Configuration

**Decision**: HTTP liveness and readiness probes at `/health` endpoint

```yaml
Liveness Probe (restart if failing):
  httpGet:
    path: /health
    port: 3000 (frontend) / 8000 (backend)
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

Readiness Probe (remove from service if failing):
  httpGet:
    path: /health
    port: 3000 (frontend) / 8000 (backend)
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
```

**Rationale**: Separate liveness and readiness probes ensure Kubernetes can detect unhealthy pods (liveness) and temporarily remove unready pods from service (readiness) without killing them.

---

### 6.2 ConfigMap and Secret Management

**Decision**: ConfigMap for non-sensitive config, Secrets for sensitive data

**ConfigMap Contents**:
```yaml
PORT: "8000" (backend), "3000" (frontend)
NODE_ENV: "development"
VITE_API_URL: "http://localhost:8000/api"
```

**Secret Contents** (base64 encoded):
```yaml
DATABASE_URL: <auto-generated or provided>
JWT_SECRET: <auto-generated on helm install>
BETTER_AUTH_SECRET: <auto-generated on helm install>
```

**Secret Generation Strategy**:
- Use Helm template functions to generate random secrets on first install
- Store secrets in Kubernetes Secrets resource (NOT in values.yaml)
- Document manual override process for custom secrets

---

## 7. Helm Chart Version Management

**Decision**: Semantic versioning starting at v0.1.0 for Phase IV

```yaml
Chart.yaml:
  apiVersion: v2
  name: todo-chatbot
  version: 0.1.0  # Chart version
  appVersion: "1.0.0"  # Application version (Phase III)
  description: "Local Kubernetes deployment for Todo Chatbot (Phase IV)"
```

**Versioning Strategy**:
- Chart version tracks deployment configuration changes
- App version tracks application code version (from Phase III)
- Major version bump: Breaking changes to Helm values schema
- Minor version bump: New Kubernetes resources or features
- Patch version bump: Bug fixes, optimization tweaks

---

## 8. Research Summary

### Resolved NEEDS CLARIFICATION Items

All Technical Context unknowns have been resolved:

✅ **Gordon Availability**: Use Claude Code-generated Dockerfiles (Gordon fallback)
✅ **kubectl-ai Setup**: Installation via krew, OpenAI API key required
✅ **kagent Configuration**: MCP-integrated cluster analysis tool
✅ **Container Base Images**: node:20-alpine (frontend), python:3.13-slim (backend)
✅ **Service Exposure**: LoadBalancer with Minikube tunnel
✅ **Resource Limits**: Static limits (no HPA for local dev)
✅ **Health Checks**: HTTP probes at /health endpoint
✅ **Secret Management**: Auto-generated secrets via Helm templates

### Key Architectural Decisions

1. **AI Tool Fallback**: AI-first approach with comprehensive manual fallbacks
2. **Service Exposure**: LoadBalancer + Minikube tunnel for localhost access
3. **Resource Strategy**: Static limits optimized for Minikube constraints
4. **Container Images**: Alpine-based for frontend, slim-based for backend

### Phase 0 Output Artifacts

- ✅ research.md (this file)
- ✅ All NEEDS CLARIFICATION resolved
- ✅ AI DevOps tooling strategy documented
- ✅ Container base image decisions made
- ✅ Service exposure approach defined

**Ready to proceed to Phase 1**: Data model, contracts, and quickstart guide generation.

---

**Last Updated**: 2026-01-21
**Status**: Research complete, ready for Phase 1 design

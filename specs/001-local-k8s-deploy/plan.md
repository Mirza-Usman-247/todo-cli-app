# Implementation Plan: Phase IV — Local Kubernetes Deployment

**Branch**: `001-local-k8s-deploy` | **Date**: 2026-01-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-local-k8s-deploy/spec.md`

**Note**: This plan executes deployment-only operations using AI-assisted DevOps tooling. NO APPLICATION CODE MODIFICATIONS ALLOWED.

## Summary

Deploy the existing Phase III Todo Chatbot (frontend + backend) to a local Kubernetes cluster using Minikube with AI-assisted DevOps tooling (Gordon for Docker, kubectl-ai for operations, kagent for cluster analysis). Deliverables include containerized applications, Helm charts, and complete deployment automation to enable local Kubernetes development with intelligent scaling, debugging, and optimization capabilities.

## Technical Context

### Application Stack (Phase III - IMMUTABLE)
**Frontend**: Next.js with React, TypeScript
**Backend**: Python 3.13+ with FastAPI, UV package manager
**Application Storage**: File-based JSON (`/db/todos.json`) - NO DATABASE
**Application Ports**: Frontend 3000, Backend 8000

### Deployment Stack (Phase IV - NEW)
**Container Runtime**: Docker Desktop (WSL2 on Windows / native on macOS/Linux)
**AI Docker Assistant**: Gordon (Docker AI Agent) OR Claude Code-generated Dockerfiles (fallback)
**Kubernetes Distribution**: Minikube 1.28+ (local development cluster only)
**Package Manager**: Helm 3.12+ for declarative Kubernetes deployments
**AI Operations Tools**:
- **kubectl-ai**: AI-assisted kubectl commands (installation: `kubectl krew install ai`)
- **kagent**: Cluster health analysis and optimization (MCP-integrated)

### Container Specifications
**Frontend Container**:
- Base image: `node:20-alpine` (multi-stage build required)
- Build stage: `npm install && npm run build`
- Runtime: nginx:alpine or node server
- Port: 3000 (configurable via PORT env var)
- User: Non-root (node/nginx)
- Resources: CPU 100m-200m, Memory 128Mi-256Mi

**Backend Container**:
- Base image: `python:3.13-slim`
- Package manager: UV for dependency installation
- Port: 8000 (configurable via PORT env var)
- User: Non-root (appuser)
- Resources: CPU 200m-500m, Memory 256Mi-512Mi

### Kubernetes Configuration
**Cluster Resources**: 4 CPU cores, 8GB RAM minimum (Minikube allocation)
**Service Type**: LoadBalancer (Minikube tunnel for local access)
**Replicas**: 1 frontend, 1 backend (scalable via kubectl-ai)
**Namespaces**: `todo-app` (deployment namespace)
**Storage**: Ephemeral container storage (NO persistent volumes)
**Health Checks**: Liveness/readiness probes at `/health` endpoint

### Testing Requirements
**Container Tests**: Docker build succeeds, image size validation
**Helm Tests**: `helm lint` and `helm template` validation
**Deployment Tests**: Pod Running state, 0 restarts, health checks pass
**Scaling Tests**: kubectl-ai replica changes, pod recovery (delete pod verification)
**Connectivity Tests**: Frontend → Backend service communication
**AI Tool Tests**: kubectl-ai and kagent query responses

**Project Type**: Deployment/Infrastructure (web application containers)
**Performance Goals**: Pod startup < 2 minutes, service accessibility < 30 seconds post-deployment
**Constraints**: Local Minikube only, NO cloud deployments, NO application code changes
**Scale/Scope**: 2 microservices (frontend + backend), 1 Helm chart, minimal resource footprint

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase IV Deployment Compliance Gates

| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| **I. SDD Mandate** | Spec → Plan → Tasks workflow | ✅ PASS | Following `/sp.plan` workflow with spec.md input |
| **II. Phase-Scoped Development** | NO application code changes | ✅ PASS | Deployment-only scope; frontend/backend immutable |
| **III. Test-First Deployment Validation** | TDD for Ops (Helm lint, dry-run, pod recovery) | ✅ PASS | Deployment validation tests defined in spec |
| **IV. Minimal Viable Simplicity** | No unnecessary abstractions | ✅ PASS | Single Helm chart, standard Kubernetes resources |
| **V. Containerized Storage Architecture** | Ephemeral storage, NO database | ✅ PASS | Container-native ephemeral storage only |
| **VI. Separation of Concerns** | Deployment artifacts separate from app code | ✅ PASS | docker/, helm/, k8s/ directories planned |
| **VII. AI DevOps Context-First** | MCP validation for Gordon, kubectl-ai, kagent | ⚠️ BLOCKING | Phase 0 MUST validate AI tool availability |
| **XIV. AI-Assisted DevOps Tooling** | Gordon/kubectl-ai/kagent usage mandatory | ⚠️ BLOCKING | Phase 0 MUST confirm tool installation |
| **XV. Container-First Design** | Multi-stage builds, non-root users, resource limits | ✅ PASS | Specified in Technical Context |
| **XVI. Declarative Over Imperative** | Helm charts for all resources | ✅ PASS | Helm-based deployment strategy |
| **XVII. Local Development Cluster Focus** | Minikube only, NO cloud deployments | ✅ PASS | Minikube explicitly scoped |
| **XVIII. AI Tool Observability** | Document all AI tool interactions | ✅ PASS | AI tool usage documentation required |

### Pre-Planning Gates Summary
- ✅ **7 gates PASSED**: Ready for Phase 0 research
- ⚠️ **2 gates BLOCKING**: AI DevOps tool validation required in Phase 0
- ❌ **0 gates FAILED**: No violations

**Gate Decision**: PROCEED to Phase 0 with BLOCKING requirement to validate AI DevOps tooling (Gordon, kubectl-ai, kagent) availability and MCP context access before implementation planning.

### Post-Design Re-evaluation
*To be completed after Phase 1 (data-model, contracts, quickstart)*

**Architectural Decisions Requiring ADR Evaluation**:
1. Container base image selection (node:20-alpine vs node:20-slim)
2. Service exposure strategy (LoadBalancer vs NodePort vs Ingress)
3. AI tool fallback strategy (manual kubectl vs AI-first with documented fallbacks)
4. Resource limit tuning approach (static vs HPA-based autoscaling)

**ADR Suggestion Criteria**: If ANY decision meets all three tests (Impact + Alternatives + Scope), suggest ADR creation with user consent.

## Project Structure

### Documentation (this feature)

```text
specs/001-local-k8s-deploy/
├── spec.md              # Feature specification (user stories, requirements)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output: AI DevOps tooling research
├── data-model.md        # Phase 1 output: Deployment entity model
├── quickstart.md        # Phase 1 output: Deployment guide
├── contracts/           # Phase 1 output: Helm chart specifications
│   ├── helm-chart-spec.yaml
│   ├── frontend-deployment-spec.yaml
│   └── backend-deployment-spec.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Deployment Artifacts (repository root - Phase IV NEW)

```text
# Application Code (Phase III - DO NOT MODIFY)
frontend/                # Next.js application (IMMUTABLE)
├── src/
│   ├── components/
│   ├── pages/
│   └── lib/
└── package.json

backend/                 # FastAPI application (IMMUTABLE)
├── src/
│   ├── api/
│   ├── models/
│   └── services/
├── pyproject.toml
└── uv.lock

# Phase IV Deployment Artifacts (NEW)
docker/
├── frontend/
│   └── Dockerfile       # Multi-stage build for Next.js
└── backend/
    └── Dockerfile       # Python 3.13 with UV

helm/
└── todo-chatbot/        # Main Helm chart
    ├── Chart.yaml       # Chart metadata (v0.1.0)
    ├── values.yaml      # Default configuration values
    └── templates/       # Kubernetes manifests
        ├── _helpers.tpl              # Template helpers
        ├── deployment-frontend.yaml  # Frontend Deployment
        ├── deployment-backend.yaml   # Backend Deployment
        ├── service-frontend.yaml     # Frontend LoadBalancer Service
        ├── service-backend.yaml      # Backend LoadBalancer Service
        ├── configmap.yaml            # Non-sensitive config (PORT, NODE_ENV, VITE_API_URL)
        └── secret.yaml               # Sensitive config (DATABASE_URL, JWT_SECRET, BETTER_AUTH_SECRET)

k8s/                     # Raw manifests (reference/debugging only)
├── namespace.yaml
└── README.md            # Explains Helm is primary, these are for reference

scripts/                 # Build and deployment automation
├── build-images.sh      # Build Docker images with Minikube Docker daemon
├── deploy-local.sh      # Helm install/upgrade wrapper
└── validate-deployment.sh  # Post-deployment validation tests

docs/                    # Phase IV documentation
├── deployment-guide.md  # Complete deployment workflow
├── ai-tools-usage.md    # Gordon, kubectl-ai, kagent examples
├── troubleshooting.md   # Common issues and solutions
└── architecture.md      # Phase IV architecture overview
```

**Structure Decision**: Web application deployment structure. Phase III application code (frontend/, backend/) remains untouched. Phase IV adds layered deployment artifacts (docker/, helm/, scripts/, docs/) that operate on the immutable application code. This maintains clear separation of concerns per Constitution Principle VI.

**Rationale for docker/ directory**: While Dockerfiles could live in application directories, separating them into docker/ emphasizes they are deployment artifacts, not application code. This prevents accidental coupling and makes the deployment boundary explicit.

**Rationale for Helm-first approach**: Raw k8s/ manifests are for reference only. All actual deployments use Helm charts for declarative, version-controlled, reproducible deployments per Constitution Principle XVI.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations identified.** All deployment artifacts follow constitution principles:
- Single Helm chart (no multi-chart complexity)
- Standard Kubernetes resources (Deployment, Service, ConfigMap, Secret)
- No custom operators or CRDs
- Minimal viable container configurations
- AI-assisted tooling as prescribed by constitution

**Complexity Justifications**: N/A

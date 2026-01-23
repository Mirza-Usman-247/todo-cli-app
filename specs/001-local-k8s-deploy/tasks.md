# Tasks: Phase IV — Local Kubernetes Deployment

**Input**: Design documents from `/specs/001-local-k8s-deploy/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Organization**: Tasks are grouped by user story (US1-US7) to enable independent implementation and testing of each deployment scenario.

**Constraints**:
- NO application code modifications (Phase III frontend/backend are IMMUTABLE)
- All tasks focus on deployment artifacts only
- Tasks must be verifiable on local Minikube cluster
- NO manual shell scripting beyond build/deploy commands

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US7 from spec.md)
- Exact file paths included in descriptions

## Path Conventions

Phase IV deployment artifacts structure:
```
docker/frontend/Dockerfile          # Frontend container definition
docker/backend/Dockerfile           # Backend container definition
helm/todo-chatbot/                  # Helm chart directory
scripts/                            # Build and deployment automation
docs/                               # Phase IV documentation
```

---

## Phase 0: AI DevOps Tool Validation (BLOCKING)

**Purpose**: Validate AI-assisted DevOps tooling availability before any deployment work

**⚠️ CRITICAL**: This phase MUST complete successfully before proceeding. Constitution gates require AI DevOps tool validation.

- [ ] T001 [US1] Verify Docker Desktop is installed and running
  - **Fulfills**: FR-001, FR-002 (prerequisite for containerization)
  - **Command**: `docker --version && docker ps`
  - **Acceptance**: Docker version displayed, daemon responds to ps command
  - **Fallback**: Install Docker Desktop from https://www.docker.com/products/docker-desktop

- [ ] T002 [US3] Verify Minikube is installed and can start
  - **Fulfills**: FR-009, FR-018 (prerequisite for Kubernetes deployment)
  - **Command**: `minikube version && minikube config set cpus 4 && minikube config set memory 8192`
  - **Acceptance**: Minikube version displayed, config updated successfully
  - **Fallback**: Install Minikube from https://minikube.sigs.k8s.io/docs/start/

- [ ] T003 [US3] Start Minikube cluster with Phase IV resource allocation
  - **Fulfills**: FR-018 (4 CPUs, 8GB RAM, 30GB disk)
  - **Command**: `minikube start --cpus=4 --memory=8192 --disk-size=30g`
  - **Acceptance**: Cluster status shows "Running", kubectl context set to minikube
  - **Validation**: `minikube status && kubectl get nodes`

- [ ] T004 [US2] Verify Helm 3+ is installed
  - **Fulfills**: FR-003 (prerequisite for Helm chart deployment)
  - **Command**: `helm version`
  - **Acceptance**: Helm version 3.12+ displayed
  - **Fallback**: Install Helm from https://helm.sh/docs/intro/install/

- [ ] T005 [P] [US5] Attempt kubectl-ai installation (optional)
  - **Fulfills**: FR-013 (AI-assisted scaling operations)
  - **Command**: `kubectl krew install ai || echo "kubectl-ai unavailable, will use manual kubectl"`
  - **Acceptance**: kubectl-ai installed OR fallback message logged
  - **Fallback**: Document manual kubectl commands in docs/ai-tools-usage.md

- [ ] T006 [P] [US6] Verify kagent availability via MCP (optional)
  - **Fulfills**: FR-014 (AI-assisted cluster health analysis)
  - **Command**: Check if kagent MCP server is accessible
  - **Acceptance**: kagent responds to test query OR fallback to manual kubectl top
  - **Fallback**: Document manual cluster inspection commands in docs/ai-tools-usage.md

- [ ] T007 [P] [US1] Document Gordon AI availability status
  - **Fulfills**: FR-001, FR-002 (Dockerfile generation strategy)
  - **Command**: Check Docker Desktop AI features (region-dependent)
  - **Acceptance**: Document "Gordon unavailable - using Claude Code-generated Dockerfiles" in docs/ai-tools-usage.md
  - **Fallback**: Claude Code will generate all Dockerfiles (primary approach)

**Checkpoint**: AI DevOps tooling validated - Constitution BLOCKING gates cleared

---

## Phase 1: User Story 1 - Docker Containerization (Priority: P1) 🎯 MVP

**Goal**: Containerize frontend and backend applications using Docker with AI-generated Dockerfiles

**Independent Test**: Container images can be built and verified with `docker images` command

### Implementation for User Story 1

- [ ] T008 [P] [US1] Create docker/frontend/ directory structure
  - **Fulfills**: FR-001 (frontend containerization)
  - **Command**: `mkdir -p docker/frontend`
  - **Acceptance**: Directory exists at `docker/frontend/`
  - **Note**: Separation per Constitution Principle VI (deployment artifacts separate from app code)

- [ ] T009 [P] [US1] Create docker/backend/ directory structure
  - **Fulfills**: FR-002 (backend containerization)
  - **Command**: `mkdir -p docker/backend`
  - **Acceptance**: Directory exists at `docker/backend/`
  - **Note**: Separation per Constitution Principle VI

- [ ] T010 [US1] Generate frontend Dockerfile using Claude Code
  - **Fulfills**: FR-001 (multi-stage build, port 3000, non-root user)
  - **File**: `docker/frontend/Dockerfile`
  - **Contract**: See `specs/001-local-k8s-deploy/contracts/frontend-deployment-spec.yaml` for full requirements
  - **Acceptance Criteria**:
    - Multi-stage build (builder + runtime stages)
    - Base image: node:20-alpine
    - Port 3000 exposed
    - Non-root user (node)
    - Health check endpoint at /health
  - **Validation**: Review Dockerfile content for compliance
  - **Example Claude Code Prompt**: "Generate a production-ready multi-stage Dockerfile for the Next.js frontend in ./frontend using node:20-alpine base image with port 3000 exposed and non-root user. Follow the specification in specs/001-local-k8s-deploy/contracts/frontend-deployment-spec.yaml."

- [ ] T011 [US1] Generate backend Dockerfile using Claude Code
  - **Fulfills**: FR-002 (Python 3.13 + UV, port 8000, non-root user)
  - **File**: `docker/backend/Dockerfile`
  - **Contract**: See `specs/001-local-k8s-deploy/contracts/backend-deployment-spec.yaml` for full requirements
  - **Acceptance Criteria**:
    - Base image: python:3.13-slim
    - UV package manager for dependency installation
    - Port 8000 exposed
    - Non-root user (appuser)
    - Health check endpoint at /health
  - **Validation**: Review Dockerfile content for compliance
  - **Example Claude Code Prompt**: "Generate a production-ready Dockerfile for the FastAPI backend in ./backend using python:3.13-slim and UV for dependency management with port 8000 exposed and non-root user. Follow the specification in specs/001-local-k8s-deploy/contracts/backend-deployment-spec.yaml."

- [ ] T012 [US1] Configure Docker environment for Minikube registry
  - **Fulfills**: FR-001, FR-002 (use Minikube's Docker daemon)
  - **Command**: `eval $(minikube docker-env)`
  - **Acceptance**: `echo $DOCKER_HOST` shows Minikube Docker daemon address
  - **Note**: This ensures images are built directly in Minikube's registry

- [ ] T013 [US1] Build frontend container image in Minikube registry
  - **Fulfills**: FR-001 (create frontend Docker image)
  - **Command**: `docker build -t todo-chatbot-frontend:latest -f docker/frontend/Dockerfile ./frontend`
  - **Acceptance Criteria**:
    - Image builds successfully
    - No errors in build output
    - Image size < 500MB (recommended)
  - **Validation**: `docker images | grep todo-chatbot-frontend`
  - **Expected Output**: `todo-chatbot-frontend   latest   <image-id>   <time>   <size>`

- [ ] T014 [US1] Build backend container image in Minikube registry
  - **Fulfills**: FR-002 (create backend Docker image)
  - **Command**: `docker build -t todo-chatbot-backend:latest -f docker/backend/Dockerfile ./backend`
  - **Acceptance Criteria**:
    - Image builds successfully
    - No errors in build output
    - Image size < 800MB (recommended)
  - **Validation**: `docker images | grep todo-chatbot-backend`
  - **Expected Output**: `todo-chatbot-backend   latest   <image-id>   <time>   <size>`

- [ ] T015 [US1] Verify frontend image is accessible in Minikube
  - **Fulfills**: SC-001 (frontend image available in local registry within 5 minutes)
  - **Command**: `docker images | grep todo-chatbot-frontend`
  - **Acceptance**: Frontend image listed with repository name `todo-chatbot-frontend:latest`
  - **Validation**: Image ID and creation timestamp displayed

- [ ] T016 [US1] Verify backend image is accessible in Minikube
  - **Fulfills**: SC-001 (backend image available in local registry within 5 minutes)
  - **Command**: `docker images | grep todo-chatbot-backend`
  - **Acceptance**: Backend image listed with repository name `todo-chatbot-backend:latest`
  - **Validation**: Image ID and creation timestamp displayed

**Checkpoint**: User Story 1 complete - Container images built and available in Minikube registry

---

## Phase 2: User Story 2 - Helm Chart Creation (Priority: P1) 🎯 MVP

**Goal**: Create Helm charts for Todo Chatbot with configurable parameters and easy upgrades

**Independent Test**: Helm charts can be validated using `helm lint` and `helm template` without deploying

### Implementation for User Story 2

- [ ] T017 [US2] Create Helm chart base structure
  - **Fulfills**: FR-003 (Helm chart structure with Chart.yaml, values.yaml, templates/)
  - **Command**: `mkdir -p helm/todo-chatbot/templates`
  - **Acceptance**: Directory structure exists: `helm/todo-chatbot/` with `templates/` subdirectory
  - **Note**: Will be populated with manifests in subsequent tasks

- [ ] T018 [US2] Generate Chart.yaml metadata file
  - **Fulfills**: FR-003 (Chart.yaml with metadata)
  - **File**: `helm/todo-chatbot/Chart.yaml`
  - **Content** (based on contracts/helm-chart-spec.yaml):
    ```yaml
    apiVersion: v2
    name: todo-chatbot
    version: 0.1.0
    appVersion: "1.0.0"
    description: "Local Kubernetes deployment for Todo Chatbot (Phase IV)"
    type: application
    ```
  - **Acceptance**: File exists and contains valid YAML with required fields
  - **Validation**: `helm lint helm/todo-chatbot` (will show errors until templates added)

- [ ] T019 [US2] Generate values.yaml configuration file
  - **Fulfills**: FR-008 (resource requests/limits configuration)
  - **File**: `helm/todo-chatbot/values.yaml`
  - **Content** (based on contracts/helm-chart-spec.yaml):
    - Frontend: replicas=1, image repo/tag, resources (100m/128Mi → 200m/256Mi)
    - Backend: replicas=1, image repo/tag, resources (200m/256Mi → 500m/512Mi)
    - ConfigMap data (PORT, NODE_ENV, VITE_API_URL)
    - Secrets (auto-generate flags for JWT_SECRET, BETTER_AUTH_SECRET)
  - **Acceptance**: File exists with all configuration sections
  - **Validation**: YAML syntax valid (can be parsed by helm)

- [ ] T020 [P] [US2] Generate _helpers.tpl template helper functions
  - **Fulfills**: FR-003 (Helm chart templates with helpers)
  - **File**: `helm/todo-chatbot/templates/_helpers.tpl`
  - **Required Functions**:
    - `todo-chatbot.name`: Chart name
    - `todo-chatbot.fullname`: Full resource name
    - `todo-chatbot.labels`: Common labels
    - `todo-chatbot.selectorLabels`: Pod selector labels
    - `todo-chatbot.generateSecret`: Random secret generation (32 chars)
  - **Acceptance**: File contains all required template helper functions
  - **Validation**: Functions can be referenced in other templates

- [ ] T021 [P] [US2] Generate ConfigMap manifest template
  - **Fulfills**: FR-006 (ConfigMap for non-sensitive config)
  - **File**: `helm/todo-chatbot/templates/configmap.yaml`
  - **Content**:
    - PORT: "8000"
    - NODE_ENV: "development"
    - VITE_API_URL: "http://localhost:8000/api"
  - **Acceptance**: Valid Kubernetes ConfigMap manifest with data from values.yaml
  - **Validation**: `helm template helm/todo-chatbot | grep -A 10 "kind: ConfigMap"`

- [ ] T022 [P] [US2] Generate Secret manifest template with auto-generation
  - **Fulfills**: FR-007 (Secret with JWT_SECRET, BETTER_AUTH_SECRET, auto-generated)
  - **File**: `helm/todo-chatbot/templates/secret.yaml`
  - **Content**:
    - jwtSecret: auto-generated 32-char string if empty
    - betterAuthSecret: auto-generated 32-char string if empty
    - databaseUrl: empty (no database in Phase IV)
  - **Acceptance**: Valid Kubernetes Secret manifest with base64-encoded values
  - **Validation**: `helm template helm/todo-chatbot | grep -A 10 "kind: Secret"`
  - **Note**: Use `randAlphaNum 32 | b64enc` for auto-generation

- [ ] T023 [US2] Generate frontend Deployment manifest template
  - **Fulfills**: FR-004 (frontend Deployment with health checks, resource limits)
  - **File**: `helm/todo-chatbot/templates/deployment-frontend.yaml`
  - **Content** (based on contracts/frontend-deployment-spec.yaml):
    - Replicas from values.yaml
    - Image: todo-chatbot-frontend:latest (IfNotPresent pull policy)
    - Container port: 3000
    - Resources: 100m/128Mi requests, 200m/256Mi limits
    - Liveness probe: HTTP GET /health on port 3000
    - Readiness probe: HTTP GET /health on port 3000
    - EnvFrom: ConfigMap reference
    - Security context: runAsNonRoot=true, runAsUser=1000
  - **Acceptance**: Valid Kubernetes Deployment manifest
  - **Validation**: `helm template helm/todo-chatbot | grep -A 50 "kind: Deployment" | grep frontend`

- [ ] T024 [US2] Generate backend Deployment manifest template
  - **Fulfills**: FR-004 (backend Deployment with health checks, resource limits)
  - **File**: `helm/todo-chatbot/templates/deployment-backend.yaml`
  - **Content** (based on contracts/backend-deployment-spec.yaml):
    - Replicas from values.yaml
    - Image: todo-chatbot-backend:latest (IfNotPresent pull policy)
    - Container port: 8000
    - Resources: 200m/256Mi requests, 500m/512Mi limits
    - Liveness probe: HTTP GET /health on port 8000
    - Readiness probe: HTTP GET /health on port 8000
    - Env: JWT_SECRET, BETTER_AUTH_SECRET from Secret
    - EnvFrom: ConfigMap reference
    - Security context: runAsNonRoot=true, runAsUser=1001
  - **Acceptance**: Valid Kubernetes Deployment manifest
  - **Validation**: `helm template helm/todo-chatbot | grep -A 50 "kind: Deployment" | grep backend`

- [ ] T025 [P] [US2] Generate frontend Service manifest template
  - **Fulfills**: FR-005 (frontend LoadBalancer Service, port 80→3000)
  - **File**: `helm/todo-chatbot/templates/service-frontend.yaml`
  - **Content**:
    - Type: LoadBalancer
    - Port: 80 (external) → TargetPort: 3000 (container)
    - Selector: app.kubernetes.io/component=frontend
  - **Acceptance**: Valid Kubernetes Service manifest with LoadBalancer type
  - **Validation**: `helm template helm/todo-chatbot | grep -A 10 "kind: Service" | grep frontend`

- [ ] T026 [P] [US2] Generate backend Service manifest template
  - **Fulfills**: FR-005 (backend LoadBalancer Service, port 80→8000)
  - **File**: `helm/todo-chatbot/templates/service-backend.yaml`
  - **Content**:
    - Type: LoadBalancer
    - Port: 80 (external) → TargetPort: 8000 (container)
    - Selector: app.kubernetes.io/component=backend
  - **Acceptance**: Valid Kubernetes Service manifest with LoadBalancer type
  - **Validation**: `helm template helm/todo-chatbot | grep -A 10 "kind: Service" | grep backend`

- [ ] T027 [P] [US2] Generate NOTES.txt post-install instructions
  - **Fulfills**: FR-017 (verification commands documentation)
  - **File**: `helm/todo-chatbot/templates/NOTES.txt`
  - **Content**:
    - Instructions to start minikube tunnel
    - Frontend access URL: http://localhost:3000
    - Backend access URL: http://localhost:8000
    - Verification commands: kubectl get pods, kubectl get svc
  - **Acceptance**: File contains user-friendly post-install instructions
  - **Validation**: `helm install todo-chatbot helm/todo-chatbot --dry-run` displays NOTES

- [ ] T028 [US2] Validate Helm chart with helm lint
  - **Fulfills**: SC-002 (Helm charts pass lint validation with 0 errors)
  - **Command**: `helm lint helm/todo-chatbot`
  - **Acceptance**: Output shows "0 chart(s) failed" (warnings acceptable)
  - **Expected Output**: `==> Linting helm/todo-chatbot ... 1 chart(s) linted, 0 chart(s) failed`

- [ ] T029 [US2] Validate Helm chart template rendering
  - **Fulfills**: SC-002 (helm template generates valid manifests)
  - **Command**: `helm template todo-chatbot helm/todo-chatbot > /tmp/rendered-manifests.yaml`
  - **Acceptance Criteria**:
    - No errors during rendering
    - Output contains: 2 Deployments, 2 Services, 1 ConfigMap, 1 Secret
  - **Validation**: `grep -c "kind: Deployment" /tmp/rendered-manifests.yaml` (expect: 2)

- [ ] T030 [US2] Validate Helm chart with dry-run install
  - **Fulfills**: FR-017 (verification commands)
  - **Command**: `helm install todo-chatbot helm/todo-chatbot -n todo-app --create-namespace --dry-run --debug`
  - **Acceptance**: No errors, manifests validate against Kubernetes API
  - **Expected Output**: Manifest preview with "STATUS: pending-install"

**Checkpoint**: User Story 2 complete - Helm charts validated and ready for deployment

---

## Phase 3: User Story 3 - Minikube Deployment (Priority: P1) 🎯 MVP

**Goal**: Deploy Todo Chatbot Helm charts to Minikube cluster and verify all pods reach Running state

**Independent Test**: Deployment can be verified using `kubectl get pods` without application-level testing

### Implementation for User Story 3

- [ ] T031 [US3] Install Helm chart to todo-app namespace
  - **Fulfills**: FR-009 (deploy Helm chart to Minikube)
  - **Command**: `helm install todo-chatbot helm/todo-chatbot -n todo-app --create-namespace`
  - **Acceptance Criteria**:
    - Helm release created successfully
    - STATUS: deployed
    - All resources created (Deployments, Services, ConfigMap, Secret)
  - **Validation**: `helm status todo-chatbot -n todo-app`
  - **Expected Output**: "STATUS: deployed"

- [ ] T032 [US3] Verify all Kubernetes resources are created
  - **Fulfills**: FR-017 (verification commands)
  - **Command**: `kubectl get all -n todo-app`
  - **Acceptance Criteria**:
    - 2 Deployments (frontend, backend)
    - 2 Services (frontend, backend)
    - 2 Pods (1 frontend, 1 backend)
    - 2 ReplicaSets
  - **Validation**: All resources listed with correct names

- [ ] T033 [US3] Wait for pods to reach Running state
  - **Fulfills**: FR-010, SC-003 (pods reach Running within 2 minutes)
  - **Command**: `kubectl wait --for=condition=ready pod --all -n todo-app --timeout=120s`
  - **Acceptance**: All pods reach "Ready" condition within 2 minutes
  - **Validation**: `kubectl get pods -n todo-app`
  - **Expected Output**: All pods show "1/1" in READY column and "Running" in STATUS

- [ ] T034 [US3] Verify zero pod restarts
  - **Fulfills**: FR-010, SC-003 (0 restarts within 2 minutes)
  - **Command**: `kubectl get pods -n todo-app -o jsonpath='{.items[*].status.containerStatuses[*].restartCount}'`
  - **Acceptance**: Output shows all zeros: "0 0"
  - **Validation**: No pod has restarted

- [ ] T035 [US3] Verify frontend pod is Running with health checks passing
  - **Fulfills**: FR-010 (frontend pod Running status)
  - **Command**: `kubectl get pods -n todo-app -l app.kubernetes.io/component=frontend`
  - **Acceptance Criteria**:
    - Pod status: Running
    - Ready: 1/1
    - Restarts: 0
  - **Validation**: `kubectl describe pod <frontend-pod> -n todo-app | grep -E "(Liveness|Readiness)"`
  - **Expected**: Both probes show success

- [ ] T036 [US3] Verify backend pod is Running with health checks passing
  - **Fulfills**: FR-010 (backend pod Running status)
  - **Command**: `kubectl get pods -n todo-app -l app.kubernetes.io/component=backend`
  - **Acceptance Criteria**:
    - Pod status: Running
    - Ready: 1/1
    - Restarts: 0
  - **Validation**: `kubectl describe pod <backend-pod> -n todo-app | grep -E "(Liveness|Readiness)"`
  - **Expected**: Both probes show success

- [ ] T037 [US3] Inspect frontend pod logs for startup success
  - **Fulfills**: FR-010 (verify startup without critical errors)
  - **Command**: `kubectl logs -n todo-app deployment/todo-chatbot-frontend --tail=20`
  - **Acceptance**: Logs show application started successfully, no errors
  - **Expected Keywords**: Server listening, ready, started (application-specific)

- [ ] T038 [US3] Inspect backend pod logs for startup success
  - **Fulfills**: FR-010 (verify startup without critical errors)
  - **Command**: `kubectl logs -n todo-app deployment/todo-chatbot-backend --tail=20`
  - **Acceptance**: Logs show application started successfully, health endpoint responding
  - **Expected Keywords**: Uvicorn running, Application startup complete (application-specific)

**Checkpoint**: User Story 3 complete - Application deployed to Minikube with all pods Running

---

## Phase 4: User Story 4 - Local Application Access (Priority: P1) 🎯 MVP

**Goal**: Access Todo Chatbot frontend from local machine via Minikube tunnel

**Independent Test**: Frontend can be accessed using browser or curl to verify deployment accessibility

### Implementation for User Story 4

- [ ] T039 [US4] Start Minikube tunnel for LoadBalancer access
  - **Fulfills**: FR-011, FR-012 (enable local access via minikube tunnel)
  - **Command**: `minikube tunnel` (run in separate terminal, keep running)
  - **Acceptance**: Tunnel starts successfully, LoadBalancer IPs assigned
  - **Expected Output**: "Tunnel successfully started" or similar
  - **Note**: This terminal must remain open for the duration of local access

- [ ] T040 [US4] Verify LoadBalancer external IPs are assigned
  - **Fulfills**: FR-011, FR-012 (LoadBalancer accessible at localhost)
  - **Command**: `kubectl get svc -n todo-app`
  - **Acceptance Criteria**:
    - Frontend service EXTERNAL-IP: 127.0.0.1
    - Backend service EXTERNAL-IP: 127.0.0.1
  - **Validation**: Both services show external IPs (not <pending>)

- [ ] T041 [US4] Test frontend accessibility via curl
  - **Fulfills**: SC-004 (frontend accessible at http://localhost:3000 within 30s)
  - **Command**: `curl -f http://localhost:3000`
  - **Acceptance Criteria**:
    - HTTP 200 status
    - HTML content returned
    - No connection errors
  - **Validation**: Output contains HTML (e.g., `<html>`, `<title>`)

- [ ] T042 [US4] Test backend health endpoint via curl
  - **Fulfills**: SC-005 (backend /health responds HTTP 200 within 30s)
  - **Command**: `curl -f http://localhost:8000/health`
  - **Acceptance Criteria**:
    - HTTP 200 status
    - JSON health status returned
    - Response indicates service is healthy
  - **Validation**: Output contains health status JSON

- [ ] T043 [US4] Access frontend in browser and verify UI loads
  - **Fulfills**: SC-004 (frontend UI loads successfully)
  - **Action**: Open http://localhost:3000 in browser
  - **Acceptance Criteria**:
    - Todo Chatbot UI displays
    - No JavaScript errors in console
    - Page fully renders
  - **Validation**: Visual inspection - UI matches Phase III Todo Chatbot interface

- [ ] T044 [US4] Test frontend-backend communication via UI
  - **Fulfills**: FR-019, SC-010 (deployed app behaves identically to non-containerized version)
  - **Action**: In frontend UI, create a new todo item
  - **Acceptance Criteria**:
    - Todo item can be created
    - Item persists (indicates backend API is reachable)
    - No network errors in browser console
  - **Validation**: Created todo appears in UI (full CRUD not required, just connectivity)

**Checkpoint**: User Story 4 complete - Application accessible from localhost via Minikube tunnel

---

## Phase 5: User Story 5 - Application Scaling (Priority: P2)

**Goal**: Scale Todo Chatbot horizontally by increasing replicas to handle higher load

**Independent Test**: Scaling can be verified using kubectl commands without application functionality testing

### Implementation for User Story 5

- [ ] T045 [US5] Scale frontend deployment to 3 replicas using kubectl-ai (if available)
  - **Fulfills**: FR-013, SC-006 (kubectl-ai scale operation)
  - **Command**: `kubectl-ai "scale todo-chatbot-frontend deployment to 3 replicas in todo-app namespace"` OR fallback: `kubectl scale deployment todo-chatbot-frontend --replicas=3 -n todo-app`
  - **Acceptance Criteria**:
    - Deployment scaled to 3 replicas
    - All 3 pods enter Running state within 1 minute
  - **Validation**: `kubectl get pods -n todo-app -l app.kubernetes.io/component=frontend`
  - **Expected**: 3 pods listed, all Running

- [ ] T046 [US5] Verify all 3 frontend pods are Ready
  - **Fulfills**: SC-006 (all scaled replicas Ready within 30 seconds)
  - **Command**: `kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=frontend -n todo-app --timeout=60s`
  - **Acceptance**: All 3 frontend pods reach Ready condition
  - **Validation**: `kubectl get pods -n todo-app -l app.kubernetes.io/component=frontend -o wide`

- [ ] T047 [US5] Test traffic distribution across frontend replicas
  - **Fulfills**: User Story 5 Acceptance Scenario 3 (LoadBalancer distributes traffic)
  - **Command**: `for i in {1..10}; do curl -s http://localhost:3000 > /dev/null && echo "Request $i successful"; done`
  - **Acceptance Criteria**:
    - All requests succeed (10/10)
    - Traffic distributed by LoadBalancer (may not be visible without tracing, but service routing works)
  - **Validation**: All 10 requests return HTTP 200

- [ ] T048 [US5] Scale backend deployment to 2 replicas (manual kubectl)
  - **Fulfills**: FR-013 (scaling operations support)
  - **Command**: `kubectl scale deployment todo-chatbot-backend --replicas=2 -n todo-app`
  - **Acceptance**: Deployment scaled to 2 replicas, both Running
  - **Validation**: `kubectl get pods -n todo-app -l app.kubernetes.io/component=backend`
  - **Expected**: 2 pods listed, all Running

- [ ] T049 [US5] Verify scaled backend replicas are Ready and serving traffic
  - **Fulfills**: FR-013 (verify scaling works)
  - **Command**: `kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=backend -n todo-app --timeout=60s`
  - **Acceptance**: Both backend pods reach Ready condition
  - **Validation**: `curl -f http://localhost:8000/health` (succeeds, routed to one of 2 backends)

- [ ] T050 [US5] Scale frontend back to 1 replica
  - **Fulfills**: FR-013 (scale down operation)
  - **Command**: `kubectl scale deployment todo-chatbot-frontend --replicas=1 -n todo-app`
  - **Acceptance**: Deployment scaled down to 1 replica, excess pods terminated gracefully
  - **Validation**: `kubectl get pods -n todo-app -l app.kubernetes.io/component=frontend`
  - **Expected**: 1 pod Running, 2 pods terminated

**Checkpoint**: User Story 5 complete - Scaling operations validated (up and down)

---

## Phase 6: User Story 6 - Cluster Health and Optimization Analysis (Priority: P2)

**Goal**: Analyze cluster health and optimize resource allocation using AI tools

**Independent Test**: Cluster health can be assessed using kubectl metrics without application-specific tests

### Implementation for User Story 6

- [ ] T051 [US6] Enable metrics-server addon in Minikube (if not already enabled)
  - **Fulfills**: FR-014 prerequisite (resource usage metrics)
  - **Command**: `minikube addons enable metrics-server`
  - **Acceptance**: Addon enabled successfully
  - **Validation**: `minikube addons list | grep metrics-server` shows "enabled"

- [ ] T052 [US6] Wait for metrics-server to be ready
  - **Fulfills**: FR-014 prerequisite
  - **Command**: `kubectl wait --for=condition=available deployment/metrics-server -n kube-system --timeout=120s`
  - **Acceptance**: Metrics-server deployment is available
  - **Validation**: `kubectl top nodes` returns data (not "error: Metrics API not available")

- [ ] T053 [US6] Analyze cluster health using kagent (if available)
  - **Fulfills**: FR-014, SC-007 (kagent cluster health analysis within 30 seconds)
  - **Command**: `kagent "analyze cluster health for todo-app namespace"` OR fallback: Manual inspection
  - **Acceptance Criteria**:
    - Report generated within 30 seconds
    - Pod status summary included
    - Resource usage summary included
    - Any detected issues highlighted
  - **Fallback**: `kubectl get pods -n todo-app && kubectl top pods -n todo-app && kubectl get events -n todo-app --sort-by='.lastTimestamp'`

- [ ] T054 [US6] Get resource usage metrics for frontend pods
  - **Fulfills**: SC-007 (frontend CPU under 50%, backend under 70%)
  - **Command**: `kubectl top pod -n todo-app -l app.kubernetes.io/component=frontend`
  - **Acceptance Criteria**:
    - CPU usage displayed (e.g., 20m out of 200m limit)
    - Memory usage displayed (e.g., 100Mi out of 256Mi limit)
    - Both under limits (no OOMKilled events)
  - **Validation**: CPU < 100m (50% of 200m limit), Memory < 128Mi (50% of 256Mi limit)

- [ ] T055 [US6] Get resource usage metrics for backend pods
  - **Fulfills**: SC-007 (backend CPU usage)
  - **Command**: `kubectl top pod -n todo-app -l app.kubernetes.io/component=backend`
  - **Acceptance Criteria**:
    - CPU usage displayed (e.g., 150m out of 500m limit)
    - Memory usage displayed (e.g., 200Mi out of 512Mi limit)
    - Both under limits
  - **Validation**: CPU < 350m (70% of 500m limit), Memory < 358Mi (70% of 512Mi limit)

- [ ] T056 [US6] Request resource limit optimization suggestions using kagent (if available)
  - **Fulfills**: SC-007 (kagent recommendations within 30 seconds)
  - **Command**: `kagent "suggest resource limits for todo-chatbot-frontend based on usage"` OR fallback: Manual analysis
  - **Acceptance Criteria**:
    - Recommendations provided within 30 seconds
    - Suggestions for CPU and memory limits
    - Based on actual usage patterns
  - **Fallback**: Compare `kubectl top pod` output with current limits in `kubectl describe deployment`

- [ ] T057 [US6] Document resource optimization findings
  - **Fulfills**: FR-020 (optimization documentation)
  - **File**: `docs/resource-optimization.md`
  - **Content**:
    - Current resource usage (CPU, memory per component)
    - Recommendations from kagent or manual analysis
    - Potential adjustments to values.yaml
  - **Acceptance**: File created with analysis and recommendations

**Checkpoint**: User Story 6 complete - Cluster health analyzed and optimization recommendations documented

---

## Phase 7: User Story 7 - Pod Failure Diagnosis (Priority: P3)

**Goal**: Diagnose and troubleshoot pod failures using AI-assisted tools

**Independent Test**: Failure scenarios can be simulated and diagnosed using kubectl/kagent without fixing application code

### Implementation for User Story 7

- [ ] T058 [US7] Simulate pod failure by deleting a frontend pod
  - **Fulfills**: FR-015 (pod failure diagnosis capability)
  - **Command**: `kubectl delete pod -n todo-app -l app.kubernetes.io/component=frontend --field-selector=status.phase=Running | head -1`
  - **Acceptance**: Pod deleted, Deployment controller creates replacement pod
  - **Validation**: `kubectl get pods -n todo-app -l app.kubernetes.io/component=frontend` shows new pod starting

- [ ] T059 [US7] Verify automatic pod recovery (Deployment creates new pod)
  - **Fulfills**: FR-010 (pod restart recovery)
  - **Command**: `kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=frontend -n todo-app --timeout=120s`
  - **Acceptance Criteria**:
    - New pod created by Deployment controller
    - New pod reaches Running state within 2 minutes
    - Application remains accessible during recovery
  - **Validation**: `kubectl get pods -n todo-app -l app.kubernetes.io/component=frontend` shows 1 pod Running (with new pod name)

- [ ] T060 [US7] Diagnose a CrashLoopBackOff scenario using kubectl-ai (simulated)
  - **Fulfills**: FR-015, SC-008 (kubectl-ai pod failure diagnosis within 2 minutes)
  - **Command**: `kubectl-ai "explain why pod <pod-name> might be in CrashLoopBackOff in todo-app namespace"` OR fallback: `kubectl describe pod <pod-name> -n todo-app && kubectl logs <pod-name> -n todo-app --previous`
  - **Acceptance Criteria**:
    - kubectl-ai provides specific reasons (e.g., missing env var, failed health check)
    - Remediation steps suggested (e.g., add PORT to ConfigMap)
  - **Fallback**: Manual inspection of Events and logs
  - **Note**: This is a hypothetical scenario; actual pods should be Running

- [ ] T061 [US7] Diagnose OOMKilled scenario using kagent (simulated)
  - **Fulfills**: SC-008 (kagent diagnosis with recommendations)
  - **Command**: `kagent "diagnose todo-chatbot-frontend pod startup failure due to OOMKilled"` OR fallback: `kubectl describe pod <pod-name> -n todo-app | grep -A 5 "Last State"`
  - **Acceptance Criteria**:
    - kagent identifies OOMKilled events in pod history
    - Recommends increasing memory limits (e.g., from 256Mi to 512Mi)
  - **Fallback**: `kubectl describe pod` shows "Reason: OOMKilled" in Last State
  - **Note**: Simulated scenario for diagnosis practice

- [ ] T062 [US7] Test debugging connection errors using kubectl-ai (simulated)
  - **Fulfills**: SC-008 (kubectl-ai debugging guidance)
  - **Command**: `kubectl-ai "debug connection error in todo-chatbot-backend pod"` OR fallback: Manual troubleshooting steps
  - **Acceptance Criteria**:
    - kubectl-ai suggests checking DATABASE_URL environment variable
    - Suggests verifying database service accessibility
    - Provides commands to test connectivity
  - **Fallback**: `kubectl exec -it <backend-pod> -n todo-app -- env | grep DATABASE_URL`
  - **Note**: Educational scenario (no actual database in Phase IV)

- [ ] T063 [US7] Document troubleshooting procedures in docs/
  - **Fulfills**: FR-016, FR-020 (fallback CLI commands documentation)
  - **File**: `docs/troubleshooting.md`
  - **Content**:
    - **Pod failure modes**: CrashLoopBackOff (check env vars, logs), OOMKilled (increase memory limits), Pending (check resources)
    - **Image issues**: ImagePullBackOff (check image existence, pull policy), ErrImagePull (verify image name)
    - **Port conflicts**: Minikube tunnel port conflicts (use alternative ports or stop conflicting services)
    - **Diagnosis commands**: kubectl describe, logs, events, get pods
    - **AI tool usage examples**: kubectl-ai debugging, kagent cluster analysis
    - **Manual fallback procedures**: Direct kubectl/docker commands for each AI tool operation
  - **Acceptance**: File created covering ALL FR-020 troubleshooting topics (OOMKilled, ImagePullBackOff, CrashLoopBackOff, port conflicts)

**Checkpoint**: User Story 7 complete - Pod failure diagnosis procedures validated and documented

---

## Phase 8: Documentation and Validation (Cross-Cutting)

**Purpose**: Final documentation and end-to-end validation of deployment

- [ ] T064 [P] Create deployment guide documentation
  - **Fulfills**: FR-016 (verification commands documentation)
  - **File**: `docs/deployment-guide.md`
  - **Content**:
    - Prerequisites checklist
    - Step-by-step deployment instructions
    - Verification commands at each step
    - Troubleshooting references
  - **Acceptance**: Complete deployment workflow documented
  - **Source**: Based on quickstart.md from specs/

- [ ] T065 [P] Create AI tools usage guide
  - **Fulfills**: FR-016 (AI tool fallback documentation)
  - **File**: `docs/ai-tools-usage.md`
  - **Content**:
    - Gordon usage examples (or fallback: Claude Code Dockerfile generation)
    - kubectl-ai command examples with manual equivalents
    - kagent analysis examples with manual kubectl fallbacks
  - **Acceptance**: All AI tools documented with fallback procedures

- [ ] T065a Validate AI tool fallback commands are tested and functional
  - **Fulfills**: FR-016 (AI tool fallback validation)
  - **Command**: Test each fallback command documented in `docs/ai-tools-usage.md`
  - **Acceptance Criteria**:
    - All manual kubectl commands work (scale, describe, logs, top)
    - All manual docker commands work (build, images, run)
    - All manual helm commands work (lint, template, install)
    - Fallback procedures produce same outcomes as AI tools
  - **Validation**: Execute at least 3 fallback commands and verify success
  - **Note**: Ensures operators can function without AI tools

- [ ] T066 [P] Create architecture documentation
  - **Fulfills**: Phase IV architecture overview
  - **File**: `docs/architecture.md`
  - **Content**:
    - Deployment architecture diagram (conceptual)
    - Component relationships (frontend, backend, services, ingress)
    - Resource flow (Minikube → Docker daemon → Helm → Kubernetes resources)
  - **Acceptance**: Architecture clearly documented for Phase IV

- [ ] T067 Run complete end-to-end validation following quickstart.md
  - **Fulfills**: SC-010 (deployed app behaves identically to non-containerized version)
  - **Reference**: Follow complete validation checklist in `specs/001-local-k8s-deploy/quickstart.md` Phase 5
  - **Procedure**:
    1. Verify all pods Running: `kubectl get pods -n todo-app`
    2. Verify services exposed: `kubectl get svc -n todo-app`
    3. Access frontend: http://localhost:3000
    4. Access backend health: http://localhost:8000/health
    5. Test CRUD functionality in UI (create, read, update, delete todos)
  - **Acceptance Criteria**:
    - All verification commands succeed
    - Application fully functional
    - No behavioral differences from Phase III
    - All quickstart.md validation steps pass
  - **Validation**: Manual testing following quickstart.md Phase 5 validation checklist

- [ ] T068 Verify deployment configuration is documented in values.yaml
  - **Fulfills**: FR-008 (resource requests/limits documented)
  - **Command**: `cat helm/todo-chatbot/values.yaml`
  - **Acceptance Criteria**:
    - All configuration options documented with comments
    - Default values match spec requirements
    - Resource limits clearly specified
  - **Validation**: values.yaml is self-documenting

- [ ] T069 Create Phase IV completion checklist
  - **Fulfills**: Overall Phase IV success criteria
  - **File**: `docs/phase-iv-checklist.md`
  - **Content**:
    - All success criteria from SC-001 to SC-010
    - Checkbox for each criterion
    - Verification commands
  - **Acceptance**: Complete checklist for Phase IV sign-off

**Checkpoint**: Documentation complete - Phase IV ready for delivery

---

## Phase 9: Cleanup and Uninstall Testing (Optional)

**Purpose**: Validate cleanup procedures and resource removal

- [ ] T070 Test Helm uninstall and resource cleanup
  - **Fulfills**: FR-017 (cleanup testing)
  - **Command**: `helm uninstall todo-chatbot -n todo-app`
  - **Acceptance Criteria**:
    - Helm release removed successfully
    - All Kubernetes resources deleted (Deployments, Services, ConfigMap, Secret, Pods)
  - **Validation**: `kubectl get all -n todo-app` returns "No resources found"

- [ ] T071 Delete todo-app namespace
  - **Fulfills**: Complete cleanup
  - **Command**: `kubectl delete namespace todo-app`
  - **Acceptance**: Namespace deleted, all resources within removed
  - **Validation**: `kubectl get namespace` does not list todo-app

- [ ] T072 Stop Minikube cluster (optional, for cleanup)
  - **Fulfills**: Environment teardown
  - **Command**: `minikube stop`
  - **Acceptance**: Cluster stopped, resources preserved
  - **Validation**: `minikube status` shows "Stopped"

- [ ] T073 Delete Minikube cluster (optional, for full cleanup)
  - **Fulfills**: Complete environment removal
  - **Command**: `minikube delete`
  - **Acceptance**: Cluster deleted, all data removed
  - **Validation**: `minikube status` shows cluster does not exist

**Checkpoint**: Cleanup procedures validated

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 0 (AI DevOps Tool Validation)**: No dependencies - MUST complete first (BLOCKING)
- **Phase 1 (User Story 1 - Containerization)**: Depends on Phase 0 completion
- **Phase 2 (User Story 2 - Helm Charts)**: Depends on Phase 1 (requires container images built)
- **Phase 3 (User Story 3 - Deployment)**: Depends on Phase 2 (requires Helm charts)
- **Phase 4 (User Story 4 - Local Access)**: Depends on Phase 3 (requires deployment running)
- **Phase 5 (User Story 5 - Scaling)**: Depends on Phase 4 (requires accessible deployment)
- **Phase 6 (User Story 6 - Health Analysis)**: Depends on Phase 4 (requires running deployment)
- **Phase 7 (User Story 7 - Failure Diagnosis)**: Depends on Phase 4 (requires running deployment)
- **Phase 8 (Documentation)**: Can run in parallel with other phases (marked [P])
- **Phase 9 (Cleanup)**: Depends on all testing phases completion

### Within Each Phase

- Tasks marked [P] can run in parallel (different files, no dependencies)
- Tasks without [P] must run sequentially within their phase
- Test tasks (T067-T073) depend on implementation tasks completion

### User Story Independence

- **US1 (Containerization)**: Independently testable - images can be verified with `docker images`
- **US2 (Helm Charts)**: Independently testable - charts can be linted and rendered without deployment
- **US3 (Deployment)**: Depends on US1 + US2, independently testable with `kubectl get pods`
- **US4 (Local Access)**: Depends on US3, independently testable with `curl`
- **US5 (Scaling)**: Depends on US4, independently testable with `kubectl get pods`
- **US6 (Health Analysis)**: Depends on US4, independently testable with `kubectl top`
- **US7 (Failure Diagnosis)**: Depends on US4, independently testable with simulated failures

### Parallel Opportunities

- Within Phase 0: T005, T006, T007 can run in parallel
- Within Phase 1: T008, T009 can run in parallel
- Within Phase 2: T020, T021, T022 can run in parallel; T025, T026, T027 can run in parallel
- Within Phase 8: T064, T065, T066 can run in parallel

---

## Implementation Strategy

### MVP First (Critical Path)

1. **Phase 0**: AI DevOps Tool Validation (T001-T007) → BLOCKING
2. **Phase 1**: Containerization (T008-T016) → Docker images built
3. **Phase 2**: Helm Charts (T017-T030) → Charts validated
4. **Phase 3**: Deployment (T031-T038) → Application deployed
5. **Phase 4**: Local Access (T039-T044) → Application accessible
6. **STOP and VALIDATE**: Test complete user workflow

**MVP Delivery**: At this point, Phase IV core objectives are met (containerization + Helm deployment + local access)

### Incremental Additions

7. **Phase 5**: Scaling (T045-T050) → Horizontal scaling validated
8. **Phase 6**: Health Analysis (T051-T057) → Cluster monitoring enabled
9. **Phase 7**: Failure Diagnosis (T058-T063) → Troubleshooting procedures validated
10. **Phase 8**: Documentation (T064-T069) → Complete guides created

### Cleanup Testing

11. **Phase 9**: Cleanup (T070-T073) → Uninstall procedures validated

---

## Notes

- **NO APPLICATION CODE CHANGES**: All tasks operate on deployment artifacts only (docker/, helm/, scripts/, docs/)
- **Phase IV Scope Boundary**: Constitution Principle II strictly enforced - any task modifying frontend/ or backend/ application code is OUT OF SCOPE
- **AI Tool Fallbacks**: Every AI-assisted task (kubectl-ai, kagent) has documented manual fallback commands
- **Minikube-Only**: All tasks target local Minikube cluster; cloud deployments are out of scope
- **Declarative Deployments**: All Kubernetes resources managed via Helm (no imperative kubectl create commands)
- **Verification at Each Step**: Every phase has validation commands to confirm success before proceeding
- **Independent User Stories**: Each US can be tested independently per spec requirements
- **Commit Strategy**: Commit after each phase completion (logical groupings: T001-T007, T008-T016, T017-T030, etc.)

---

## Success Criteria Mapping

| Success Criterion | Fulfilled By Tasks |
|-------------------|-------------------|
| SC-001 (Container images built < 5 min) | T013, T014, T015, T016 |
| SC-002 (Helm charts pass lint/template) | T028, T029, T030 |
| SC-003 (Deployment completes < 10 min, pods Running) | T031, T032, T033, T034 |
| SC-004 (Frontend accessible < 30s) | T041, T043 |
| SC-005 (Backend health check < 30s) | T042 |
| SC-006 (Scaling completes < 1 min) | T045, T046, T047 |
| SC-007 (Cluster health analysis < 30s) | T053, T054, T055, T056 |
| SC-008 (Pod failure diagnosis < 2 min) | T060, T061, T062 |
| SC-009 (Deployment configs verified) | T068, T069 |
| SC-010 (App maintains functional parity) | T044, T067 |

---

**Total Tasks**: 73
**Estimated Duration**: 4-6 hours (including validation and documentation)
**Critical Path**: Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 (MVP: ~2-3 hours)

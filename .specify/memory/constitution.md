<!--
Sync Impact Report (2026-01-21)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Version Change: 3.0.0 → 4.0.0
Rationale: Major backward-incompatible evolution from Phase III (AI-Powered Chatbot with MCP/Agents SDK)
to Phase IV (Local Kubernetes Deployment with AI-Assisted DevOps)

Modified Principles:
  - II. Phase-Scoped Development: AI Chatbot → AI-Assisted Local Kubernetes Deployment
  - V. Persistent Database Architecture: Replaced with Containerized Storage Architecture
  - VI. Separation of Concerns: Updated for DevOps/deployment layers
  - VII. MCP Context-First Development: Expanded to include AI DevOps tools
  - X. Automated Deployment via CI/CD: Replaced with AI-Assisted Local Deployment

Added Principles:
  - XIV. AI-Assisted DevOps Tooling (Hard Rule)
  - XV. Container-First Design
  - XVI. Declarative Over Imperative Operations
  - XVII. Local Development Cluster Focus
  - XVIII. AI Tool Observability and Debugging

Updated Sections:
  - Phase IV Technical Constraints (Kubernetes, Helm, Docker, Gordon, kubectl-ai, kagent)
  - Development Workflow: MCP Context Validation now includes AI DevOps tooling
  - Governance: Updated compliance requirements for AI-assisted deployment

Removed Sections:
  - X. Automated Deployment via CI/CD (replaced with AI-Assisted Local Deployment)
  - Phase III AI/chatbot specific technical constraints (retained for reference in old versions)
  - All database/Neon PostgreSQL references

Templates Status:
  ✅ .specify/templates/plan-template.md - AI DevOps context check needed
  ✅ .specify/templates/spec-template.md - Deployment specifications support
  ✅ .specify/templates/tasks-template.md - Helm chart and Kubernetes tasks
  ⚠ CLAUDE.md - Update to emphasize AI DevOps tooling and Helm chart creation

Follow-up TODOs:
  - Validate AI DevOps tooling availability (Gordon, kubectl-ai, kagent)
  - Create Helm chart specifications for frontend/backend
  - Document Minikube local access setup
  - Define resource limits and scaling tests
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-->

# The Evolution of Todo - Phase IV Constitution (AI-Assisted DevOps)

## Core Principles

### I. Spec-Driven Development (SDD) Mandate

All development MUST follow the Agentic Dev Stack workflow with mandatory MCP context validation:

1. Validate MCP Context Server access and fetch documentation
2. Write specification using `/sp.specify`
3. Generate implementation plan using `/sp.plan` (with MCP context)
4. Break into actionable tasks using `/sp.tasks`
5. Implement via Claude Code following generated artifacts

**Rationale**: Ensures every code change is traceable to documented requirements and validated against current official documentation, preventing scope creep, deprecated API usage, and maintaining alignment with project goals.

**Non-negotiable rules**:
- NEVER write code without a corresponding spec
- NEVER skip MCP context validation before planning
- NEVER rely on training data for framework APIs (OpenAI Agents SDK, MCP SDK, FastAPI, SQLModel, etc.)
- NEVER skip planning or task generation steps
- STOP immediately if requirements are unclear and request clarification
- Every feature MUST have artifacts in `/specs/<feature>/` (spec.md, plan.md, tasks.md)

### II. Phase-Scoped Development

Phase IV scope is strictly limited to local Kubernetes deployment of the existing Todo Chatbot application using AI-assisted DevOps tooling. NO APPLICATION CODE CHANGES ARE ALLOWED.

**In Scope**:
- Containerization of frontend and backend using Docker
- Helm chart creation for Kubernetes deployment
- Minikube cluster deployment (local only)
- AI-assisted tooling: Gordon (Docker AI), kubectl-ai, kagent
- Kubernetes deployments, services, ConfigMaps, and Secrets
- Resource requests and limits configuration
- Scaling configurations (replica management)
- Local access setup and port forwarding
- Pod restart recovery and health checks
- Container image optimization
- AI tool observability and debugging

**Out of Scope** (Failure conditions):
- Application code modifications or feature additions
- API refactoring or database schema changes
- Cloud deployments (AWS, GCP, Azure, etc.)
- Production-grade ingress or external load balancers
- Persistent volume management beyond basic mounting
- Helm chart templating complexity beyond requirements
- Multi-cluster or production networking setup
- Authentication/authorization changes
- Any application logic changes in frontend or backend
- **CRITICAL**: Any code change that modifies application behavior

**Rationale**: Phase IV is pure deployment/orchestration focused, ensuring operational excellence with AI assistance without disrupting the working application. The existing Phase III Todo Chatbot (frontend + backend) is treated as a stable artifact for deployment.

**Non-negotiable rules**:
- REJECT any application code changes or feature additions
- REJECT cloud deployments beyond local Minikube
- REJECT scope expansion to production environments
- REJECT database migrations or schema changes
- DOCUMENT all AI DevOps tool usage (Gordon, kubectl-ai, kagent)
- ENSURE replicable, reproducible deployment via Helm charts
- VALIDATE zero application behavior changes in deployment process
- REQUEST immediate clarification if any requirement could modify application logic
- FAIL deployment if testing reveals changed application behavior

**Deployment Boundary Rule**: The deployed application must behave identically to the non-containerized version. Any behavioral discrepancy is a Phase IV failure.

### III. Test-First Deployment Validation (TDD for Ops)

Test-Driven validation is MANDATORY for all deployment configurations, including Helm charts and Kubernetes manifests.

**Red-Green-Refactor cycle for deployment**:
1. **Red**: Define deployment failure scenarios and expected behaviors
2. **Green**: Implement Helm charts and configs that pass validation
3. **Refactor**: Optimize configurations while maintaining validation

**AI-Ops testing requirements**:
- Helm chart validation tests (syntax, templating, values)
- Kubernetes manifest validation (kubectl apply --dry-run)
- Container build tests (Dockerfile syntax, image builds)
- Pod restart recovery tests (simulate failures)
- Scaling tests (replica changes, HPA if configured)
- Local access tests (port forwarding, service connectivity)
- AI tool command validation (kubectl-ai, kagent queries)

**Rationale**: TDD prevents deployment failures, ensures reproducible infrastructure, and validates AI-assisted operations work correctly in local environments.

**Non-negotiable rules**:
- VALIDATE Helm charts BEFORE applying to cluster
- TEST pod recovery by manually deleting pods
- VERIFY scaling works with kubectl-ai commands
- VALIDATE frontend/backend connectivity via services
- DOCUMENT all AI DevOps tool interactions
- FAIL deployment if any test reveals application behavior change
- USE kagent for cluster health validation before considering complete

**Deployment Boundary Test**: MUST verify deployed application behaves identically to non-containerized version.

### IV. Minimal Viable Simplicity

Start with the simplest solution. Complexity requires explicit justification.

**YAGNI (You Aren't Gonna Need It) principles**:
- No abstractions for single use cases
- No architectural patterns without proven need
- No "future-proofing" beyond Phase III requirements
- No external dependencies unless absolutely necessary
- Single task-oriented agent (no multi-agent orchestration)

**Rationale**: Premature abstraction creates maintenance burden and obscures intent. Simple code is easier to test, understand, and modify, especially in AI systems.

**Non-negotiable rules**:
- JUSTIFY any abstraction (repository pattern, dependency injection, etc.)
- REJECT unnecessary design patterns
- PREFER inline code over premature extraction
- DOCUMENT complexity violations in plan.md Complexity Tracking table
- USE single agent architecture unless multi-agent explicitly required

### V. Containerized Storage Architecture

Applications use ephemeral, container-appropriate storage patterns. NO persistent database for Phase IV.

**Data flow**:
- Application runs in isolated containers with filesystem storage
- Frontend serves static files from container filesystem
- Backend uses in-memory or mounted volume storage
- NO external database connections (Neon PostgreSQL NOT USED in Phase IV)
- Application state is ephemeral by design
- Container restarts reset to clean state (expected behavior)

**Container storage patterns**:
- Ephemeral data storage within containers
- ConfigMaps for application configuration
- Secrets for sensitive values (never hardcoded)
- Frontend static files packaged in container layers
- Backend state managed via environment variables and mounted files

**Rationale**: Phase IV focuses on deployment orchestration with ephemeral containers, not persistent data architectures. Removing database complexity simplifies Kubernetes deployment and aligns with local development cluster use cases.

**Non-negotiable rules**:
- NO Neon PostgreSQL or external database connections
- NO SQLModel or database migrations in Phase IV
- NO persistent volume claims for production database simulation
- Secrets MUST be managed via Kubernetes Secrets (not application configs)
- ConfigMaps MUST be used for non-sensitive application configuration
- CONTAINER data is ephemeral by design - state loss on restart is acceptable
- DOCUMENT all storage assumptions and limitations for Phase IV scope

**Storage Boundary Rule**: Phase IV does NOT replicate Phase III's database functionality. Ephemeral storage only.

### VI. Separation of Concerns (Deployment Layers)

Clean separation between application code, containerization, and orchestration layers:

**Required structure**:
```
# Application code (Phase III - DO NOT MODIFY)
frontend/            # Next.js application (untouched)
backend/             # FastAPI application (untouched)

# Phase IV Deployment Artifacts
docker/
├── frontend/
│   └── Dockerfile   # Frontend container definition
├── backend/
    └── Dockerfile   # Backend container definition

helm/
├── todo-app/        # Main Helm chart
│   ├── Chart.yaml   # Chart metadata
│   ├── values.yaml  # Default configuration values
│   └── templates/   # Kubernetes manifests
│       ├── deployment-frontend.yaml
│       ├── deployment-backend.yaml
│       ├── service-frontend.yaml
│       ├── service-backend.yaml
│       ├── configmap.yaml
│       └── secret.yaml

k8s/                 # Optional: Raw manifests for reference
├── manifests/

scripts/             # Build and deployment scripts (if needed)
├── build-images.sh
└── deploy-local.sh

docs/                # Phase IV documentation
├── deployment-guide.md
├── ai-tools-usage.md
└── troubleshooting.md
```

**Rationale**: Clear separation enables independent application development (Phase III) from deployment concerns (Phase IV). Application code remains untouched while deployment artifacts are layered on top.

**Non-negotiable rules**:
- DO NOT MODIFY application code in frontend/ or backend/
- Deployment configs MUST be separate from application code
- Helm charts MUST be self-contained and reusable
- Container images MUST be built from unmodified application code
- DO NOT embed deployment logic in application source files
- Keep application and deployment concerns completely separate
- DOCUMENT any application limitations discovered during containerization

**Container Boundary Rule**: Application containers are immutable deployment artifacts. No runtime code modifications allowed.

### VII. AI DevOps Context-First Development

Before any deployment implementation, the agent MUST connect to MCP Context Server and fetch latest official documentation for AI-assisted DevOps tools.

**Required MCP Context Validations (Phase IV)**:
1. **Docker Desktop + Gordon** - Verify Gordon AI agent capabilities, Dockerfile generation
2. **Minikube** - Verify local Kubernetes cluster setup, networking, storage
3. **kubectl-ai** - Verify AI-assisted kubectl commands for deployments, scaling, debugging
4. **kagent** - Verify cluster health analysis, resource optimization capabilities
5. **Helm** - Verify chart creation, templating, values management
6. **Kubernetes** - Verify deployments, services, ConfigMaps, Secrets, resource management

**MCP AI DevOps Tool Usage Validation**:
For each AI DevOps tool, MUST document:
- Tool availability and installation status
- MCP context server connection success
- Sample queries/commands validated
- Limitations and alternative approaches documented

**Rationale**: AI-assisted DevOps tooling evolves rapidly. MCP context ensures we're using current best practices and AI capabilities, not outdated training data.

**Non-negotiable rules**:
- NEVER deploy without validating AI DevOps tool MCP context
- ALWAYS test Gordon with Docker AI prompts before Dockerfile generation
- ALWAYS validate kubectl-ai commands with --dry-run where possible
- USE kagent for cluster analysis at least once in each deployment task
- DOCUMENT all AI tool interactions and their outcomes
- FAIL planning phase if AI DevOps tools cannot be validated via MCP
- VERIFY Helm chart syntax with helm lint before applying to cluster

**AI DevOps Tool Coverage Rule**: At least one meaningful operation must be performed with kubectl-ai AND kagent in each deployment feature.

### VIII. AI-Assisted DevOps Operations

All Kubernetes operations MUST be performed using AI-assisted tools (kubectl-ai, kagent) with documented manual fallback procedures.

**AI Tool Usage Patterns**:
- **kubectl-ai**: Primary tool for deployments, scaling, resource inspection, debugging
  - Example: "kubectl-ai deploy myapp with 3 replicas and 1GB memory limit"
  - Example: "kubectl-ai scale deployment backend to 5 replicas"
  - Example: "kubectl-ai what pods are failing and why?"
- **kagent**: Primary tool for cluster health analysis and optimizations
  - Example: "kagent analyze cluster resource usage"
  - Example: "kagent suggest optimizations for my deployment"
  - Example: "kagent identify potential issues in my namespace"
- **Gordon**: Primary tool for Docker operations
  - Example: "Gordon, build an optimized image for my Node.js frontend"
  - Example: "Gordon, create a multi-stage Dockerfile for Python backend"

**AI Command Documentation**:
For each AI-assisted command, document:
- The natural language prompt used
- AI-generated kubectl/helm/docker commands
- Verification steps performed
- Outcome and success criteria
- Any manual corrections needed

**Rationale**: AI-assisted DevOps tools accelerate operations while learning modern Kubernetes workflows, providing natural language interfaces to complex command-line operations.

**Non-negotiable rules**:
- PREFER kubectl-ai over direct kubectl commands
- PREFER kagent over manual cluster inspection
- PREFER Gordon over manual Dockerfile writing
- ALWAYS document AI tool prompts and outcomes
- NEVER rely on AI tools without verification
- VALIDATE AI-generated commands with --dry-run when available
- TEST AI-assisted scaling/updates in staging before production environments

**AI Tool Coverage Rule**: Must use at least 3 different AI-assisted operations per deployment feature.

### IX. AI-Assisted DevOps Operations

All Kubernetes operations MUST be performed using AI-assisted tools (kubectl-ai, kagent) with documented manual fallback procedures.

**AI Tool Usage Patterns**:
- **kubectl-ai**: Primary tool for deployments, scaling, resource inspection, debugging
  - Example: "kubectl-ai deploy myapp with 3 replicas and 1GB memory limit"
  - Example: "kubectl-ai scale deployment backend to 5 replicas"
  - Example: "kubectl-ai what pods are failing and why?"
- **kagent**: Primary tool for cluster health analysis and optimizations
  - Example: "kagent analyze cluster resource usage"
  - Example: "kagent suggest optimizations for my deployment"
  - Example: "kagent identify potential issues in my namespace"
- **Gordon**: Primary tool for Docker operations
  - Example: "Gordon, build an optimized image for my Node.js frontend"
  - Example: "Gordon, create a multi-stage Dockerfile for Python backend"

**AI Command Documentation**:
For each AI-assisted command, document:
- The natural language prompt used
- AI-generated kubectl/helm/docker commands
- Verification steps performed
- Outcome and success criteria
- Any manual corrections needed

**Rationale**: AI-assisted DevOps tools accelerate operations while learning modern Kubernetes workflows, providing natural language interfaces to complex command-line operations.

**Non-negotiable rules**:
- PREFER kubectl-ai over direct kubectl commands
- PREFER kagent over manual cluster inspection
- PREFER Gordon over manual Dockerfile writing
- ALWAYS document AI tool prompts and outcomes
- NEVER rely on AI tools without verification
- VALIDATE AI-generated commands with --dry-run when available
- TEST AI-assisted scaling/updates in staging before production environments

**AI Tool Coverage Rule**: Must use at least 3 different AI-assisted operations per deployment feature.

### XIV. AI-Assisted DevOps Tooling (Hard Rule)

The AI agent MUST use AI-assisted DevOps tools exclusively for all Kubernetes operations. Direct kubectl/docker commands without AI assistance are DISCOURAGED.

**Mandatory AI DevOps Tools**:
- **Gordon (Docker AI)**: Dockerfile generation, image optimization, build/run commands
- **kubectl-ai**: Natural language kubectl commands for deployments, scaling, debugging
- **kagent**: Cluster health analysis, resource optimization, operational insights

**Tool Availability Checklist** (Phase 0 - BLOCKING):
- Gordon installed and accessible via MCP
- kubectl-ai installed and configured
- kagent installed and connected to Minikube
- Minikube cluster running and kubectl context set
- Docker Desktop running with Kubernetes enabled

**AI Tool Usage Tracking**:
For each deployment feature, document:
- Gordon prompts used (Dockerfile generation, optimization suggestions)
- kubectl-ai commands used (with natural language prompts and generated kubectl commands)
- kagent analysis results (cluster health, optimization recommendations)
- AI tool success rate and manual fallback count

**Rationale**: AI-assisted DevOps tools accelerate learning, reduce operational errors, and provide intelligent guidance for Kubernetes operations.

**Non-negotiable rules**:
- PREFER Gordon over manual Dockerfile writing
- PREFER kubectl-ai over direct kubectl commands
- PREFER kagent over manual cluster inspection
- DOCUMENT every AI tool interaction (prompt, result, verification)
- VERIFY AI-generated commands before execution (especially destructive operations)
- TRACK AI tool coverage (at least one meaningful operation per tool per deployment feature)
- REPORT AI tool limitations or failures immediately
- USE AI tools for debugging failing pods (kubectl-ai first, then kagent for deep analysis)

**Coverage Enforcement**: Each Phase IV deployment feature MUST include documented usage of at least two AI DevOps tools.

### XV. Container-First Design

All deployment artifacts MUST be container-native and follow Docker/Kubernetes best practices.

**Container Design Principles**:
- **Multi-stage builds**: Optimize image size with build and runtime stages
- **Minimal base images**: Use distroless or alpine where appropriate
- **Non-root containers**: Run applications as non-root users
- **Health checks**: Define liveness and readiness probes
- **Resource limits**: Set CPU and memory requests/limits
- **Immutable containers**: No runtime modifications or volume mounts for code

**Frontend Container Requirements**:
- Node.js 18+ base image for build stage
- Nginx or static file server for runtime
- Optimized production build (npm run build output)
- Multi-stage build to minimize final image size
- PORT environment variable configuration

**Backend Container Requirements**:
- Python 3.13+ base image
- UV package manager for dependency installation
- Non-root user execution
- PORT environment variable configuration
- Health check endpoint (root path returns 200)

**Rationale**: Container-first design ensures consistent environments from local development to production, improves security, and enables proper resource management in Kubernetes.

**Non-negotiable rules**:
- ALWAYS use multi-stage builds for frontend containers
- ALWAYS run containers as non-root users
- ALWAYS define health checks in Kubernetes manifests
- ALWAYS set resource requests and limits
- NEVER hardcode configuration in container images
- NEVER store secrets in container layers
- OPTIMIZE for image size and security

**Container Security Rule**: No container should run as root. All containers must have defined resource limits.

### XVI. Declarative Over Imperative Operations

Kubernetes deployments MUST use declarative configuration (Helm charts) over imperative commands.

**Declarative Principles**:
- **Helm charts**: All Kubernetes resources defined as templates
- **Version control**: All deployment configurations in Git
- **Values-driven**: Configuration via Helm values.yaml, not direct edits
- **Reproducible**: Same chart produces identical deployments
- **Reviewable**: PR reviews for infrastructure changes

**Declarative vs Imperative**:
```bash
# ❌ IMPERATIVE (FORBIDDEN without documentation)
kubectl create deployment frontend --image=frontend:v1
kubectl expose deployment frontend --port=3000 --type=NodePort

# ✅ DECLARATIVE (REQUIRED)
# Define in Helm template/deployment-frontend.yaml
# Apply with: helm install todo-app ./helm/todo-app
```

**Helm Chart Standards**:
- All resources in templates/ directory
- Configurable via values.yaml
- Resource names use chart templates ({{- define "name" -}})
- ConfigMaps for non-sensitive config
- Secrets for sensitive data (base64 encoded)
- Services for inter-pod communication
- Proper labels and selectors for all resources

**Rationale**: Declarative configurations enable GitOps, reproducible deployments, rollbacks, and infrastructure as code best practices.

**Non-negotiable rules**:
- ALL Kubernetes resources MUST be in Helm templates
- NEVER use kubectl create/patch without Helm chart equivalent
- ALWAYS version control Helm charts and values
- ALWAYS use helm install/upgrade, not direct kubectl for deployments
- DOCUMENT all values and their purposes in values.yaml comments

### XVII. Local Development Cluster Focus

All deployments MUST target local Minikube cluster to ensure development-friendly workflows.

**Minikube Configuration**:
- **Single-node cluster**: Sufficient for local development
- **Resource allocation**: 4 CPU cores, 8GB RAM minimum
- **Storage**: Default storage class for PVCs
- **Networking**: NodePort services for local access
- **Addons**: ingress-dns, metrics-server (optional)

**Local Access Setup**:
- Frontend: NodePort service (e.g., 30001)
- Backend: NodePort service (e.g., 30002)
- Port forwarding for development: kubectl port-forward
- Minikube tunnel for LoadBalancer services (if needed)

**Development Workflow**:
1. Start Minikube: `minikube start --cpus=4 --memory=8g`
2. Build images: `eval $(minikube docker-env) && docker build ...`
3. Deploy with Helm: `helm install todo-app ./helm/todo-app`
4. Access services: `minikube service todo-app-frontend --url`
5. Test scaling: `kubectl-ai scale deployment backend to 5 replicas`
6. Debug with kagent: `kagent check pod health in default namespace`

**Rationale**: Local Kubernetes development enables rapid iteration, offline work, and safe experimentation without cloud costs or infrastructure complexity.

**Non-negotiable rules**:
- DO NOT target cloud Kubernetes clusters (EKS, GKE, AKS)
- DO NOT configure production-grade persistent volumes
- DO NOT use LoadBalancer services (use NodePort instead)
- DO NOT configure production ingress controllers
- ALWAYS use minikube for Phase IV development and testing
- ALWAYS test pod recovery with kubectl delete pod
- ALWAYS validate scaling within local resource constraints

**Local Cluster Boundary Rule**: Phase IV deployments are for local development only. Production considerations are out of scope.

### XVIII. AI Tool Observability and Debugging

All AI DevOps tool interactions MUST be observable, documented, and debuggable.

**Observability Requirements**:
- **Prompt logging**: Every AI tool prompt and response logged
- **Command verification**: AI-generated commands validated before execution
- **Outcome tracking**: Success/failure rates for AI-assisted operations
- **Fallback documentation**: Manual fallback procedures when AI tools fail

**Debugging Workflow**:
1. **Detection**: Identify deployment issue or unexpected behavior
2. **kubectl-ai query**: "kubectl-ai what's wrong with frontend pod?"
3. **kagent analysis**: "kagent diagnose backend deployment issues"
4. **Manual verification**: Validate AI findings with kubectl describe/logs
5. **Resolution**: Apply fix via AI tool or Helm chart update
6. **Documentation**: Log issue, AI tool response, resolution

**AI Tool Failure Modes**:
- **Misunderstanding prompt**: Reformulate with clearer language
- **Invalid command generation**: Use --dry-run to validate, correct manually
- **Tool unavailability**: Document and use fallback kubectl/docker commands
- **Context limitations**: Provide more context about cluster state

**Rationale**: Observability ensures AI-assisted operations are traceable, debuggable, and improvable. Documentation helps identify AI tool limitations and patterns.

**Non-negotiable rules**:
- LOG every AI tool prompt and response
- DOCUMENT AI tool failures and manual fallbacks
- VALIDATE all AI-generated commands before execution
- USE kubectl-ai first for pod debugging
- USE kagent for cluster-level issue diagnosis
- CREATE troubleshooting guide from AI tool interactions
- NEVER proceed with AI-generated commands that could cause data loss without verification

**AI Tool Failure Rule**: If AI tools fail, document the failure mode and use manual kubectl/docker commands, then report the issue to improve AI tool usage.

## Phase IV Technical Constraints

### Containerization

- **Docker Runtime**: Docker Desktop (WSL2 on Windows, native on macOS/Linux)
- **AI Assistant**: Gordon (Docker AI Agent) - PRIMARY FOR Dockerfile generation
- **Fallback**: Standard Docker CLI commands (if Gordon unavailable)
- **Multi-stage builds**: REQUIRED for frontend optimization
- **Base Images**: Official Node.js 18+ and Python 3.13+ images
- **Image Registry**: Local Docker daemon (eval $(minikube docker-env))

### Kubernetes Runtime

- **Distribution**: Minikube (local development cluster only)
- **Version**: Latest stable (1.28+)
- **Resources**: 4 CPU cores, 8GB RAM minimum allocation
- **Storage**: Default storage class (ephemeral)
- **Networking**: NodePort services for local access
- **Addons**: ingress-dns (optional), metrics-server (optional)
- **kubectl Context**: Must point to minikube before any operations

### AI DevOps Tooling

- **Gordon**: Docker AI Agent for Dockerfile generation and optimization
  - MCP context: Docker Desktop integration, Dockerfile best practices
  - Usage: Natural language prompts for Dockerfile creation

- **kubectl-ai**: AI-assisted kubectl commands
  - Installation: `kubectl krew install ai`
  - Usage: "kubectl-ai <natural language query>"
  - Examples: deployment creation, scaling, debugging, resource inspection

- **kagent**: Cluster health analysis and optimization
  - MCP context: Kubernetes cluster analysis, resource optimization
  - Usage: "kagent <analysis query>"
  - Examples: pod health, resource usage, optimization suggestions

### Helm (Package Manager)

- **Version**: Helm 3.12+ (latest stable)
- **Chart Structure**:
  - Chart.yaml: Metadata (name, version, dependencies)
  - values.yaml: Default configuration values
  - templates/: Kubernetes manifests (deployments, services, configmaps, secrets)
- **Templating**: Go templates with Sprig functions
- **Values Management**: Environment-specific values files (values-dev.yaml)
- **Chart Dependencies**: None (single chart for simplicity)

### Application Container Requirements

#### Frontend Container
- **Base Image**: node:18-alpine
- **Build Stage**: npm install && npm run build
- **Runtime**: nginx:alpine or node server
- **Port**: 3000 (configurable via PORT env var)
- **Health Check**: GET / returns 200
- **User**: Non-root user (node or nginx)
- **Resources**: CPU request: 100m, limit: 500m; Memory request: 128Mi, limit: 512Mi

#### Backend Container
- **Base Image**: python:3.13-slim
- **Package Manager**: UV for dependency installation
- **UV sync**: Install dependencies in container
- **Port**: 8000 (configurable via PORT env var)
- **Health Check**: GET / returns 200
- **User**: Non-root user (appuser)
- **Resources**: CPU request: 200m, limit: 1000m; Memory request: 256Mi, limit: 1Gi

### Kubernetes Resource Requirements

#### Frontend Deployment
- **Replicas**: 2 (configurable via Helm values)
- **Image**: todo-frontend:latest (from local Docker)
- **Service**: NodePort (port 30001)
- **ConfigMap**: Frontend configuration
c- **Resources**: CPU: 100m-500m, Memory: 128Mi-512Mi

#### Backend Deployment
- **Replicas**: 2 (configurable via Helm values)
- **Image**: todo-backend:latest (from local Docker)
- **Service**: NodePort (port 30002)
- **ConfigMap**: Backend configuration
- **Secrets**: (if any sensitive config)
- **Resources**: CPU: 200m-1000m, Memory: 256Mi-1Gi

### AI DevOps Tool Usage Patterns

#### Gordon (Docker AI)
- "Gordon, create a multi-stage Dockerfile for my Next.js frontend"
- "Gordon, optimize my Python backend Dockerfile for size"
- "Gordon, how do I build and run these containers?"

#### kubectl-ai Examples
- "kubectl-ai deploy frontend with 2 replicas and expose on NodePort 30001"
- "kubectl-ai scale backend deployment to 5 replicas"
- "kubectl-ai what's causing frontend pods to crash?"
- "kubectl-ai show me resource usage for all pods"

#### kagent Examples
- "kagent analyze my cluster for optimization opportunities"
- "kagent check pod health and suggest fixes"
- "kagent what resources are being underutilized?"
- "kagent diagnose backend service connectivity issues"

### Local Access Configuration

- **Frontend Access**: http://localhost:30001 (or minikube service)
- **Backend Access**: http://localhost:30002 (or minikube service)
- **Service Discovery**: Kubernetes DNS for inter-service communication
- **Port Forwarding**: Optional for direct pod access
- **Minikube Service**: `minikube service <service-name> --url`

### Testing Requirements (Deployment TDD)

- **Container Build Tests**: docker build succeeds, image size < 500MB
- **Helm Validation**: helm lint passes, templates render correctly
- **Dry Run**: helm install --dry-run --debug validates manifests
- **Pod Recovery**: Delete pods, verify automatic restart
- **Scaling Tests**: Change replica count, verify all pods run
- **Service Connectivity**: Frontend can reach backend via service
- **AI Tool Tests**: kubectl-ai and kagent respond to queries
- **Health Checks**: Probes return success for running pods
- **Resource Limits**: Stress test to validate limits prevent node issues
- **Cleanup Test**: helm uninstall removes all resources

### Development Workflow

**Phase 0 - AI DevOps Tool Validation** (BLOCKING):
- Verify Gordon accessible: Test Dockerfile generation prompt
- Verify kubectl-ai: `kubectl-ai --version`
- Verify kagent: `kagent check cluster`
- Verify Minikube: `minikube status` shows running
- Verify Helm: `helm version` shows v3.x
- Connect to MCP context for all tools

**Phase 1 - Containerization**:
- Gordon generates Dockerfiles (document all prompts)
- Build frontend/backend images (eval $(minikube docker-env))
- Test containers locally (docker run -p ...)
- Optimize image sizes

**Phase 2 - Helm Chart Creation**:
- Create chart structure: helm create todo-app
- Define templated manifests (deployment, service, configmap, secret)
- Configure values.yaml with appropriate defaults
- Test templating: helm template .
- Validate with helm lint

**Phase 3 - Deployment**:
- Deploy to Minikube: helm install todo-app ./helm/todo-app
- Verify pods: kubectl-ai check pod status for todo-app
- Test scaling: kubectl-ai scale deployment frontend to 5 replicas
- Test recovery: Delete pods, verify restart
- Service connectivity: Verify frontend reaches backend

**Phase 4 - AI Tool Usage**:
- Use kagent: "kagent analyze deployment health"
- Use kubectl-ai: "kubectl-ai optimize resource allocation"
- Debug issues: "kubectl-ai why is backend pod crashing?"
- Document all AI tool interactions

**Phase 5 - Validation**:
- Access frontend via Minikube service
- Verify application functionality unchanged
- Test backend API connectivity
- Validate scaling behavior
- Test pod recovery
- Run cleanup test (helm uninstall)

## Development Workflow

### 0. MCP Context Validation (Phase 0 - BLOCKING)

```bash
# Validate AI DevOps Tooling MCP Context Server access
# Fetch documentation for:
# - Docker Desktop + Gordon (Docker AI)
# - Minikube (local Kubernetes)
# - kubectl-ai (AI-assisted kubectl)
# - kagent (cluster analysis)
# - Helm (package manager)
# - Kubernetes resources (deployments, services, configmaps, secrets)

# GATE: Cannot proceed to planning without successful MCP context validation
# All AI DevOps tools must be validated as available and functioning
```

**Output**: AI DevOps tooling validation report in plan.md Phase 0

### 1. Feature Initiation

```bash
/sp.specify <deployment-feature-description>
```

**Output**: `/specs/<feature>/spec.md` with:
- User stories for deployment scenarios (P1: containerization, P2: Helm charts, P3: AI tool usage)
- Acceptance scenarios (Given/When/Then format)
- Deployment requirements (container specs, resource limits, scaling configs)
- Success criteria (application runs unchanged, local access works)

### 2. Planning

```bash
/sp.plan
```

**Output**: `/specs/<feature>/plan.md` with:
- AI DevOps tool validation status (Phase 0)
- Technical context (Gordon, kubectl-ai, kagent, Helm, Minikube, Docker)
- Constitution check (validates Phase IV deployment compliance)
- Project structure (docker/, helm/, k8s/, docs/)
- AI tool interaction plan (how kubectl-ai and kagent will be used)
- Complexity justifications (if any deployment complexity introduced)

### 3. Task Breakdown

```bash
/sp.tasks
```

**Output**: `/specs/<feature>/tasks.md` with:
- Setup tasks (Minikube start, Docker Desktop, tool installations)
- Containerization tasks (Gordon prompts, Dockerfile creation, image builds)
- Helm chart tasks (chart creation, templating, values configuration)
- Deployment tasks (helm install, service exposure, scaling tests)
- AI tool tasks (kubectl-ai operations, kagent analysis, documentation)
- Validation tasks (TDD for deployment, pod recovery, scaling verification)

### 4. Implementation

```bash
/sp.implement
```

**Process**:
- Execute tasks in dependency order (Phase 0 → setup → containerization → Helm → deployment)
- Use AI DevOps tools for all operations (document every prompt)
- Test-Driven Deployment: Define failure scenarios → Implement configs → Validate
- Use kubectl-ai for: deployments, scaling, debugging, resource inspection
- Use kagent for: cluster health, optimization, issue diagnosis
- Use Gordon for: Dockerfile generation, image optimization
- Commit after each logical deployment artifact (helm chart, dockerfile, config)
- Create PHR (Prompt History Record) after implementation

### 5. Quality Gates

**Before considering deployment feature complete**:
- ✅ All AI DevOps tools validated in MCP context (Phase 0)
- ✅ Container images build successfully and run locally
- ✅ Helm charts validate (helm lint, helm template)
- ✅ Deployment to Minikube succeeds (helm install)
- ✅ Pods start and pass health checks
- ✅ Services expose applications (NodePort access works)
- ✅ Scaling tests pass (kubectl-ai scale operations work)
- ✅ Pod recovery test succeeds (delete pod, verify restart)
- ✅ AI tool coverage requirement met (kubectl-ai + kagent used)
- ✅ Application behavior unchanged from non-containerized version
- ✅ PHR created in `history/prompts/<feature>/`
- ✅ AI tool interactions documented (prompts, commands, outcomes)

## Governance

### Constitution Authority

This Phase IV constitution supersedes all previous development practices for deployment/orchestration work. When conflicts arise:

1. Constitution principles override manual deployment convenience
2. Phase IV deployment scope overrides application feature requests
3. AI-assisted DevOps tooling overrides direct kubectl/docker operations
4. Container-first design overrides traditional deployment methods
5. Declarative Helm charts override imperative kubectl commands
6. Local Minikube focus overrides cloud deployment considerations
7. AI DevOps context validation overrides prior tool usage assumptions

### Amendment Process

1. Propose change with rationale for deployment/orchestration practices
2. Document impact on existing Helm charts and container configurations
3. Update constitution version:
   - **MAJOR**: Backward-incompatible deployment principle changes (e.g., new orchestration platform, new AI DevOps stack)
   - **MINOR**: New AI-assisted DevOps principles or expanded guidance
   - **PATCH**: Clarifications, typo fixes, non-semantic refinements for deployment workflows
4. Update dependent templates (plan, spec, tasks) with AI DevOps tooling
5. Test amendments against Minikube cluster before finalizing
6. Obtain approval verifying AI tool integration still works

### Compliance Verification

**Every deployment PR/feature MUST**:
- Reference Phase IV constitution principles in plan.md Constitution Check
- Document AI DevOps tool MCP context validation status (Phase 0)
- Justify any deployment complexity or deviations in Complexity Tracking table
- Pass all deployment validation tests (TDD for Ops compliance)
- Maintain separation between application code and deployment configs
- Validate AI-assisted DevOps tooling used (Gordon, kubectl-ai, kagent)
- Validate container-first design (multi-stage builds, non-root users, resource limits)
- Validate declarative Helm charts used for all Kubernetes resources
- Verify NO application code modifications (deployment boundary rule)
- Document all AI tool prompts, generated commands, and outcomes

**Deployment violations require**:
- Documented justification with alternative approach exploration
- AI tool interaction logs showing attempted automation
- Explicit approval before bypassing AI-assisted workflows
- Validation that manual approaches don't mask AI tool inadequacies

### Runtime Guidance

See `CLAUDE.md` for Claude Code-specific development instructions, including:
- PHR creation workflow for deployment tasks
- ADR suggestion criteria for AI DevOps tooling decisions
- MCP tool usage for AI DevOps context validation
- Human-as-Tool invocation triggers for infrastructure decisions
- AI DevOps tool integration patterns

**Version**: 4.0.0 | **Ratified**: 2026-01-21 | **Last Amended**: 2026-01-21

---

**Note**: Phase IV Constitution is strictly for local Kubernetes deployment using AI-assisted DevOps tools. Application code (Phase III Todo Chatbot) is treated as immutable.

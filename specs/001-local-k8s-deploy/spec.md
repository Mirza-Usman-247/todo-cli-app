# Feature Specification: Phase IV — Local Kubernetes Deployment

**Feature Branch**: `001-local-k8s-deploy`
**Created**: 2026-01-21
**Status**: Draft
**Input**: User description: "Phase Objective:
Deploy the existing Phase III Todo Chatbot (frontend + backend) to a local Kubernetes cluster using Minikube with AI-assisted DevOps tooling."

## User Scenarios & Testing

### User Story 1 - Docker Containerization (Priority: P1)

As an Operations Engineer, I want to containerize both the frontend and backend applications using Docker, so that they can be deployed consistently across different environments.

**Why this priority**: Containerization is the foundational step for Kubernetes deployment. Without properly built container images, no deployment can proceed.

**Independent Test**: Container images can be built and verified independently using `docker images` command. The frontend image should expose port 3000 and the backend should expose port 8000.

**Acceptance Scenarios**:

1. **Given** the Phase III frontend application code is available, **When** Claude Code generates and builds the Dockerfile, **Then** a valid Docker image for the frontend is created and listed in the local registry as `todo-chatbot-frontend:latest`.

2. **Given** the Phase III backend application code is available, **When** Claude Code generates and builds the Dockerfile, **Then** a valid Docker image for the backend is created and listed in the local registry as `todo-chatbot-backend:latest`.

3. **Given** both container images are built, **When** I run `docker images | grep todo-chatbot`, **Then** I should see both todo-chatbot-frontend and todo-chatbot-backend images listed.

---

### User Story 2 - Helm Chart Creation (Priority: P1)

As an Operations Engineer, I want to create Helm charts for the Todo Chatbot, so that I can deploy the application to Kubernetes with configurable parameters and easy upgrades.

**Why this priority**: Helm charts provide the deployment manifests needed for Kubernetes. This is a critical prerequisite for any Kubernetes deployment operation.

**Independent Test**: Helm charts can be validated using `helm lint` and `helm template` commands to verify syntax and generated manifests without deploying to a cluster.

**Acceptance Scenarios**:

1. **Given** the Helm specification is defined, **When** kubectl-ai or Claude generates the Helm chart structure with Chart.yaml, values.yaml, and template files, **Then** the charts pass `helm lint` validation with no errors.

2. **Given** the Helm charts are created with LoadBalancer service type configured, **When** I run `helm template todo-chatbot ./helm/todo-chatbot`, **Then** valid Kubernetes manifests are generated for LoadBalancer Services, Deployments, ConfigMaps, and Secrets.

3. **Given** the Helm charts are templated, **When** I inspect the generated manifests, **Then** they include appropriate resource requests (frontend: 100m/128Mi, backend: 200m/256Mi) and limits (frontend: 200m/256Mi, backend: 500m/512Mi) for both frontend and backend components.

---

### User Story 3 - Minikube Deployment (Priority: P1)

As an Operations Engineer, I want to deploy the Todo Chatbot Helm charts to a Minikube cluster, so that I can run and test the application in a local Kubernetes environment.

**Why this priority**: This is the core deployment scenario where all previous work (containerization and Helm charts) comes together in a functional Kubernetes environment.

**Independent Test**: The deployment can be verified using standard kubectl commands without requiring application-level testing. Pod status, service endpoints, and logs can validate deployment success.

**Acceptance Scenarios**:

1. **Given** Minikube is running with adequate resources (4 CPU, 8GB RAM), **When** I execute `helm install todo-chatbot ./helm/todo-chatbot -n todo-app --create-namespace`, **Then** the Helm release is created successfully and all pods (1 frontend replica, 1 backend replica) enter Running state.

2. **Given** the application is deployed, **When** I run `kubectl get pods -n todo-app`, **Then** I see frontend and backend pods in Running status with no restarts.

3. **Given** the pods are running, **When** I inspect pod logs with `kubectl logs <pod-name> -n todo-app`, **Then** the logs show application startup without critical errors and health endpoints responding successfully.

---

### User Story 4 - Local Application Access (Priority: P1)

As an Operations Engineer, I want to access the Todo Chatbot frontend from my local machine, so that I can verify the application works correctly in the Minikube environment.

**Why this priority**: This validates that the entire deployment stack (containerization, Helm charts, Kubernetes services) works end-to-end and the application is accessible.

**Independent Test**: The frontend can be tested independently using a web browser or curl to verify accessibility. Backend accessibility can be verified separately using service endpoints.

**Acceptance Scenarios**:

1. **Given** the Minikube tunnel is running (`minikube tunnel`), **When** I access `http://localhost:3000` in my browser, **Then** the Todo Chatbot frontend UI loads successfully and displays without errors.

2. **Given** the Minikube tunnel is running, **When** I access `http://localhost:8000/health`, **Then** the backend health endpoint responds with HTTP 200 status and indicates the service is healthy.

3. **Given** both services are accessible, **When** I interact with the frontend UI to create a todo item, **Then** it successfully communicates with the backend service at `http://localhost:8000/api` and the todo item is persisted.

---

### User Story 5 - Application Scaling (Priority: P2)

As an Operations Engineer, I want to scale the Todo Chatbot application horizontally by increasing replicas, so that I can handle higher load and improve availability.

**Why this priority**: Scaling demonstrates Kubernetes' core value proposition. This validates that the deployment configurations support dynamic scaling operations.

**Independent Test**: Scaling operations can be performed and verified using kubectl commands independent of application functionality. Pod counts and distribution across nodes can validate scaling success.

**Acceptance Scenarios**:

1. **Given** the Todo Chatbot is deployed with 1 replica per component, **When** I execute `kubectl-ai "scale todo-chatbot-frontend deployment to 3 replicas"`, **Then** the deployment scales to 3 frontend pods and all enter Running state within 1 minute.

2. **Given** scaled replicas are running, **When** I run `kubectl get pods -n todo-app -l app.kubernetes.io/name=todo-chatbot,app.kubernetes.io/component=frontend`, **Then** I see 3 pods listed with status Running and Ready.

3. **Given** the scaled deployment is running, **When** I make multiple requests to the frontend service, **Then** traffic is distributed across all 3 replicas by the LoadBalancer service.

---

### User Story 6 - Cluster Health and Optimization Analysis (Priority: P2)

As an Operations Engineer, I want to analyze cluster health and optimize resource allocation, so that I can ensure efficient resource utilization and identify potential issues.

**Why this priority**: Resource optimization ensures cost-effective operations and helps prevent performance issues before they impact users.

**Independent Test**: Cluster health can be assessed using kagent commands and kubectl resource metrics without requiring application-specific functionality tests.

**Acceptance Scenarios**:

1. **Given** the Minikube cluster is running, **When** I execute `kagent "analyze cluster health for todo-app namespace"`, **Then** I receive a report on pod status, resource usage, and any detected issues within 30 seconds.

2. **Given** the Todo Chatbot is deployed with the recommended resource limits (frontend: 200m/256Mi, backend: 500m/512Mi), **When** I execute `kagent "suggest resource limits for todo-chatbot-frontend based on usage"`, **Then** I receive recommendations for CPU and memory limits within 30 seconds.

3. **Given** the cluster has been running for some time, **When** I execute `kagent "optimize resource allocation for todo-app namespace"`, **Then** I receive specific optimization suggestions for Deployments and resource configurations that can improve efficiency.

---

### User Story 7 - Pod Failure Diagnosis (Priority: P3)

As an Operations Engineer, I want to diagnose and troubleshoot pod failures using AI-assisted tools, so that I can quickly identify root causes and implement fixes.

**Why this priority**: While not a primary flow, debugging capability is essential for operations. This validates that AI tools help accelerate troubleshooting.

**Independent Test**: Pod failures can be simulated and diagnosed using kubectl-ai and kagent commands. The diagnosis process can be validated independently of normal application operations.

**Acceptance Scenarios**:

1. **Given** a pod is in CrashLoopBackOff state due to missing environment variable, **When** I execute `kubectl-ai "explain why pod todo-chatbot-backend-xyz is CrashLoopBackOff"`, **Then** the tool provides specific reasons (missing PORT environment variable) and suggests remediation steps (add PORT to deployment config).

2. **Given** a pod fails to start due to insufficient memory, **When** I execute `kagent "diagnose todo-chatbot-frontend pod startup failure"`, **Then** I receive analysis of logs showing OOMKilled events and actionable recommendations to increase memory limits from 256Mi to 512Mi.

3. **Given** application logs show database connection errors, **When** I execute `kubectl-ai "debug connection error in todo-chatbot-backend pod"`, **Then** I receive specific guidance on checking DATABASE_URL environment variable and verifying database service accessibility.

---

### Edge Cases

- What happens when Docker Desktop is not running when attempting to build images? (Capture error and suggest starting Docker Desktop)
- How does the system handle when Gordon AI agent is not available? (AI-generated Docker workflows via Claude Code will be used as a fallback; Claude generates multi-stage Dockerfiles, build optimization recommendations, and security best practices)
- What happens when Minikube doesn't have sufficient resources (CPU/memory) allocated? (Capture error and suggest increasing Minikube resources via `minikube config set memory 8192` and `minikube config set cpus 4`)
- How does the system handle when a container image doesn't exist in the local registry? (Capture error and suggest building the image first with AI-generated Docker workflows via Claude Code)
- What happens when kubectl-ai is not installed or API key is missing? (Provide fallback manual kubectl commands and document setup requirements)
- How does the system handle when kagent is not available? (Fall back to manual kubectl debugging and standard Kubernetes troubleshooting commands)
- What happens when Helm charts have syntax errors? (helm lint should catch errors and provide detailed feedback on line numbers and issues)
- How does the system handle when port 3000 or 8000 is already in use on localhost? (Minikube tunnel will detect conflict and use alternative ports; document troubleshooting in deployment guide)
- What happens when network policies prevent pod-to-pod communication? (Default Minikube networking is permissive; no NetworkPolicy resources will be created for Phase IV scope)
- How does the system handle when application needs environment variables that aren't configured? (ConfigMap and Secret templates include all required variables: PORT, DATABASE_URL, JWT_SECRET, VITE_API_URL, NODE_ENV)

## Requirements

### Functional Requirements

- **FR-001**: System MUST containerize the existing Phase III frontend application into a Docker image using Claude Code-generated Dockerfiles (Gordon unavailable per research.md), creating multi-stage builds optimized for production with exposed port 3000.

- **FR-002**: System MUST containerize the existing Phase III backend application into a Docker image using Claude Code-generated Dockerfiles (Gordon unavailable per research.md), creating multi-stage builds optimized for production with exposed port 8000.

- **FR-003**: System MUST create Helm chart structure with Chart.yaml, values.yaml, and templates directory containing Kubernetes manifests for frontend and backend deployments with LoadBalancer service type.

- **FR-004**: System MUST generate Kubernetes Deployment manifests for both frontend and backend components with proper container configurations, health checks at `/health` endpoint, and resource requests/limits.

- **FR-005**: System MUST generate Kubernetes Service manifests for both frontend and backend components with LoadBalancer service type, ClusterIP configuration, and port mappings (frontend: 3000 internally → 3000 on Service, backend: 8000 internally → 8000 on Service). Note: minikube tunnel exposes Service ports on localhost at their respective application ports (localhost:3000 for frontend, localhost:8000 for backend).

- **FR-006**: System MUST define ConfigMap manifests for non-sensitive configuration data including: PORT (8000, backend-only), NODE_ENV (development), VITE_API_URL (http://localhost:8000/api). Note: Frontend uses port 3000 via its own environment configuration.

- **FR-007**: System MUST define Secret manifests for sensitive configuration data including: DATABASE_URL, JWT_SECRET, BETTER_AUTH_SECRET with values auto-generated during Helm installation.

- **FR-008**: System MUST configure resource requests and limits in Helm values.yaml: frontend requests 100m CPU/128Mi memory with limits 200m CPU/256Mi memory; backend requests 200m CPU/256Mi memory with limits 500m CPU/512Mi memory.

- **FR-009**: System MUST deploy the Todo Chatbot Helm chart to a running Minikube cluster using `helm install todo-chatbot ./helm/todo-chatbot -n todo-app --create-namespace` command.

- **FR-010**: System MUST verify that all pods reach Running state after deployment using `kubectl get pods -n todo-app` command with zero restarts observed.

- **FR-011**: System MUST enable local access to the frontend application using `minikube tunnel` command which provides LoadBalancer IP accessible at localhost:3000.

- **FR-012**: System MUST enable local access to the backend API using `minikube tunnel` command which provides LoadBalancer IP accessible at localhost:8000.

- **FR-013**: System MUST support scaling operations using kubectl-ai natural language commands OR manual kubectl scale commands if kubectl-ai unavailable to increase or decrease replica counts for frontend and backend deployments.

- **FR-014**: System MUST support cluster health analysis using kagent to provide insights on pod status, resource usage, and detected issues in the todo-app namespace.

- **FR-015**: System MUST support pod failure diagnosis using kubectl-ai and kagent tools to identify root causes and recommend remediation steps for debugging CrashLoopBackOff, OOMKilled, and other pod failure states.

- **FR-016**: System MUST document fallback CLI commands for all AI tool operations (Claude Code for Docker, kubectl-ai, kagent) in case AI tools are unavailable, including manual docker build commands and standard kubectl troubleshooting procedures.

- **FR-017**: System MUST provide verification commands at each major deployment step for validating successful completion: `docker images | grep todo-chatbot` for containerization, `helm lint` and `helm template` for chart validation, `kubectl get pods -n todo-app` for deployment verification.

- **FR-018**: System MUST document the process for setting up Minikube with appropriate resource allocations: minimum 4 CPUs, 8GB RAM, 30GB disk via `minikube config` commands.

- **FR-019**: System MUST validate that the deployed frontend and backend applications behave identically to the non-containerized Phase III version, maintaining full CRUD functionality for todo items.

- **FR-020**: System MUST create troubleshooting documentation for common issues: OOMKilled (increase memory limits), ImagePullBackOff (check image existence and pull policy), CrashLoopBackOff (check environment variables and logs), port conflicts (use minikube tunnel alternative ports).

### Key Entities

- **DockerImage**: Container image containing the application code and dependencies. Attributes: repository name (todo-chatbot-frontend/backend), tag (latest), image ID, size, exposed ports (3000/8000), environment variables (PORT, DATABASE_URL, JWT_SECRET, VITE_API_URL, NODE_ENV).

- **HelmChart**: Package containing Kubernetes manifests and configuration values. Attributes: chart name (todo-chatbot), version (0.1.0), templates (deployment, service, configmap, secret), values files (values.yaml with resource allocations).

- **KubernetesDeployment**: Controller managing replica pods. Attributes: deployment name (todo-chatbot-frontend/backend), replicas (1), container specifications (image: todo-chatbot-frontend/backend:latest), resource limits (frontend: 200m/256Mi, backend: 500m/512Mi), health checks (liveness/readiness probes at /health), update strategy (RollingUpdate).

- **KubernetesService**: Network endpoint exposing pods. Attributes: service name (todo-chatbot-frontend/backend), type (LoadBalancer), selector (app: todo-chatbot-frontend/backend), ports (frontend: 80→3000, backend: 80→8000), cluster IP.

- **KubernetesPod**: Running container instance. Attributes: pod name (todo-chatbot-frontend/backend-*), status (Running/Completed/CrashLoopBackOff), containers (1 per pod), resource usage (tracked via metrics-server), restart count, events.

- **MinikubeCluster**: Local Kubernetes cluster environment. Attributes: cluster status (Running), resource allocation (4 CPU, 8GB RAM, 30GB disk), node count (1), enabled addons (ingress, metrics-server, dashboard).

## Success Criteria

### Measurable Outcomes

- **SC-001**: Frontend and backend container images are successfully built and available in the local Docker registry within 5 minutes of build initiation, with images named `todo-chatbot-frontend:latest` and `todo-chatbot-backend:latest`.

- **SC-002**: Helm charts generate valid Kubernetes manifests that pass `helm lint` validation with zero errors and `helm template` renders all resources including LoadBalancer Services, Deployments, ConfigMaps, and Secrets.

- **SC-003**: Deployment to Minikube completes within 10 minutes and all pods reach Running state with 0 restarts within 2 minutes of deployment, verified by `kubectl get pods -n todo-app`.

- **SC-004**: Frontend application is accessible from localhost at http://localhost:3000 within 30 seconds of Minikube tunnel initialization, displaying the Todo Chatbot UI.

- **SC-005**: Backend API responds to health check requests at http://localhost:8000/health within 30 seconds of service exposure, returning HTTP 200 status and indicating service is healthy.

- **SC-006**: Scaling operation using kubectl-ai completes within 1 minute, increasing frontend replica count from 1 to 3 with all pods successfully entering Ready state within 30 seconds.

- **SC-007**: kagent cluster health analysis completes within 30 seconds and provides actionable insights on resource utilization (frontend: under 50% CPU, backend: under 70% CPU) and potential issues in todo-app namespace.

- **SC-008**: Pod failure diagnosis using kubectl-ai provides specific root cause identification and remediation steps within 2 minutes of failure detection (e.g., identifies missing PORT environment variable and suggests adding it to deployment config).

- **SC-009**: All deployment configurations are properly applied and can be verified: resource requests/limits visible in `kubectl describe pod`, health checks showing successful probes in pod description, environment variables from ConfigMap/Secret mounted correctly.

- **SC-010**: The deployed application maintains functional parity with Phase III Todo Chatbot, allowing users to perform create, read, update, and delete operations on todo items through the frontend UI connected to the backend API at http://localhost:8000/api.

### Assumptions

- Phase III Todo Chatbot application code (frontend and backend) is available and functional without modifications in the repository at `./frontend` and `./backend` directories.
- Docker Desktop is installed and running with WSL 2 integration enabled on Windows systems, or native Docker on macOS/Linux.
- Minikube is installed and configured with appropriate resource allocations (minimum 4 CPUs, 8GB RAM, 30GB disk) via `minikube config`.
- kubectl-ai tool is installed and configured with API access keys via OPENAI_API_KEY environment variable or configuration file.
- kagent tool is installed and accessible from the command line with proper authentication.
- Docker AI Agent (Gordon) was unavailable in our region during Phase IV implementation; AI-generated Docker workflows via Claude Code are used as a fallback approach. Claude generates multi-stage Dockerfiles, build optimization recommendations, and security best practices.
- Helm 3+ is installed and configured with proper repository access.
- kubectl is installed and configured to work with Minikube context.
- Network connectivity is available to pull base images (node:20-alpine, python:3.13-slim) from Docker Hub or other container registries.
- Application uses standard ports (frontend: 3000, backend: 8000) that are exposed via LoadBalancer services.
- Local machine has sufficient disk space (minimum 30GB) for Minikube VM and container images.
- All AI DevOps tools (Claude Code for Docker, kubectl-ai, kagent) have appropriate authentication and API credentials configured.
- Values.yaml will use auto-generated secrets and should not be committed to version control with sensitive data; secrets are generated fresh on each Helm install.

<!--
Sync Impact Report (2026-01-13)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Version Change: 1.0.0 → 2.0.0
Rationale: Phase II transformation from CLI to multi-user web application

Modified Principles:
  - II. Phase-Scoped Development: CLI scope → Web application scope
  - V. File-Backed In-Memory Architecture → V. Persistent Database Architecture
  - VI. Separation of Concerns: Updated for full-stack (frontend/backend/ORM)

Added Principles:
  - VII. MCP Context-First Development
  - VIII. RESTful API Design
  - IX. Auth-Aware Architecture

Removed Sections:
  - Phase I Technical Constraints (CLI-specific)
  - User Interface (CLI-specific)

Added Sections:
  - Phase II Technical Constraints (Next.js, FastAPI, Neon, SQLModel, Better Auth)
  - MCP Context Validation Requirement

Templates Status:
  ✅ .specify/templates/plan-template.md - Structure supports web apps
  ✅ .specify/templates/spec-template.md - No changes needed
  ✅ .specify/templates/tasks-template.md - No changes needed
  ⚠ .specify/commands/sp.constitution.md - Review for Phase 2 references

Follow-up TODOs:
  - Review CLAUDE.md for Phase 2 references
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-->

# The Evolution of Todo - Phase II Constitution

## Core Principles

### I. Spec-Driven Development (SDD) Mandate

All development MUST follow the Agentic Dev Stack workflow:

1. Write specification using `/sp.specify`
2. Generate implementation plan using `/sp.plan`
3. Break into actionable tasks using `/sp.tasks`
4. Implement via Claude Code following generated artifacts

**Rationale**: Ensures every code change is traceable to documented requirements, preventing scope creep and maintaining alignment with project goals.

**Non-negotiable rules**:
- NEVER write code without a corresponding spec
- NEVER skip planning or task generation steps
- STOP immediately if requirements are unclear and request clarification
- Every feature MUST have artifacts in `/specs/<feature>/` (spec.md, plan.md, tasks.md)

### II. Phase-Scoped Development

Phase II scope is strictly limited to a multi-user web application with persistent storage.

**In Scope**:
- Web-based user interface (Next.js 16+ App Router)
- RESTful API backend (FastAPI)
- User authentication and session management (Better Auth)
- Persistent database storage (Neon Serverless PostgreSQL + SQLModel)
- User isolation and secure access control
- All Phase I CLI features as web API endpoints

**Out of Scope** (Failure conditions):
- WebSocket or real-time features
- Third-party OAuth providers beyond Better Auth defaults
- AI-powered or machine learning features
- Mobile native applications
- Complex enterprise features (SSO, RBAC beyond user isolation)
- Any Phase III+ functionality

**Rationale**: Constraining scope to Phase II prevents premature optimization and ensures a working, testable foundation before expanding.

**Non-negotiable rules**:
- REJECT any implementation request that introduces out-of-scope features
- DOCUMENT scope violations if discovered during implementation
- REQUEST clarification if a requirement could expand beyond Phase II

### III. Test-First Development (TDD)

Test-Driven Development is MANDATORY for all feature implementation.

**Red-Green-Refactor cycle**:
1. **Red**: Write tests that fail (verify failure)
2. **Green**: Implement minimum code to pass tests
3. **Refactor**: Clean up while keeping tests green

**Rationale**: TDD ensures code correctness, prevents regressions, and serves as living documentation.

**Non-negotiable rules**:
- Tests MUST be written BEFORE implementation code
- Tests MUST fail initially (verify red state)
- Implementation proceeds ONLY after test approval
- ALL acceptance criteria MUST have corresponding tests

### IV. Minimal Viable Simplicity

Start with the simplest solution. Complexity requires explicit justification.

**YAGNI (You Aren't Gonna Need It) principles**:
- No abstractions for single use cases
- No architectural patterns without proven need
- No "future-proofing" beyond Phase II requirements
- No external dependencies unless absolutely necessary

**Rationale**: Premature abstraction creates maintenance burden and obscures intent. Simple code is easier to test, understand, and modify.

**Non-negotiable rules**:
- JUSTIFY any abstraction (repository pattern, dependency injection, etc.)
- REJECT unnecessary design patterns
- PREFER inline code over premature extraction
- DOCUMENT complexity violations in plan.md Complexity Tracking table

### V. Persistent Database Architecture

Data is stored in Neon Serverless PostgreSQL using SQLModel for ORM.

**Data flow**:
- Application startup → SQLModel connects to Neon PostgreSQL
- User operation → Modify data via SQLModel models
- Changes → Auto-committed by session or explicit flush
- Error handling → Rollback on failure, graceful reconnection

**Rationale**: Provides production-grade persistence with type safety and migrations suitable for Phase II scope.

**Non-negotiable rules**:
- ALL todos MUST persist to Neon PostgreSQL via SQLModel
- Domain models MUST be separate from persistence models
- SQLModel relationships MUST be properly defined for user isolation
- Database migrations MUST be environment-safe (dev/staging/prod)

### VI. Separation of Concerns

Clean architecture with distinct layers for full-stack application:

**Required structure**:
```
backend/
├── models/          # SQLAlchemy/SQLModel persistence models
├── schemas/         # Pydantic request/response schemas
├── api/             # FastAPI route handlers
├── services/        # Business logic (orchestrates models/schemas)
└── db/              # Database connection and session management

frontend/
├── app/             # Next.js App Router pages
├── components/      # React components
├── services/        # API client wrappers
└── types/           # TypeScript shared types

tests/
├── backend/         # FastAPI tests (pytest)
└── frontend/        # Next.js tests (Jest/Playwright)
```

**Rationale**: Separation enables testing, maintainability, and future refactoring across full-stack.

**Non-negotiable rules**:
- Models MUST NOT contain business logic or API concerns
- API routes MUST NOT contain business logic (delegate to services)
- Services MUST NOT import frontend components
- Each layer has clear, testable responsibilities

### VII. MCP Context-First Development

Before any planning or implementation, the agent MUST connect to MCP Context Server and fetch latest official documentation for all technologies used.

**Required MCP Context Validations**:
1. Next.js (App Router) - Verify routing patterns, server components, API routes
2. FastAPI - Verify dependency injection, request validation, response models
3. SQLModel - Verify model definitions, relationships, session management
4. Neon Serverless PostgreSQL - Verify connection patterns, serverless compatibility
5. Better Auth - Verify installation, configuration, middleware integration

**Rationale**: Ensures implementation follows current best practices and avoids deprecated patterns.

**Non-negotiable rules**:
- NEVER rely on training data assumptions for framework APIs
- ALWAYS fetch and validate documentation via MCP before implementation
- VERIFY APIs, configurations, auth flows against official docs
- UPDATE MCP context if new versions are released during development

### VIII. RESTful API Design

All API endpoints MUST follow RESTful conventions with proper schemas.

**Design principles**:
- Resource-based URLs (/todos, /users, /auth/)
- HTTP methods as intended (GET=read, POST=create, PUT=replace, PATCH=update, DELETE=remove)
- Proper status codes (200, 201, 400, 401, 403, 404, 422, 500)
- Versioned API path (/api/v1/...)

**Request/Response contracts**:
- ALL endpoints MUST have Pydantic request models
- ALL endpoints MUST have typed response models
- Error responses MUST follow consistent format with error codes
- Authenticated endpoints MUST validate session on every request

**Rationale**: Consistent API design enables frontend integration, testing, and future extensibility.

**Non-negotiable rules**:
- NEVER expose internal models directly in API responses
- VALIDATE all inputs with Pydantic schemas
- DOCUMENT all endpoints with OpenAPI (FastAPI automatic)
- RETURN appropriate HTTP status codes for all outcomes

### IX. Auth-Aware Architecture

Authentication MUST be implemented using Better Auth with proper middleware enforcement.

**Auth requirements**:
- User signup and signin with email/password
- Secure session/token handling via Better Auth
- Auth middleware enforced on ALL protected routes
- User isolation: users can ONLY access their own todos

**Security rules**:
- NO custom authentication logic unless explicitly required by spec
- Session tokens MUST be validated on every protected request
- Passwords MUST be hashed by Better Auth (bcrypt/argon2)
- API endpoints MUST check ownership before data access

**Rationale**: Proper auth prevents unauthorized access and ensures multi-user isolation.

**Non-negotiable rules**:
- USE Better Auth for all authentication flows
- PROTECT all TODO API endpoints with auth middleware
- VALIDATE user ownership before any modify/delete operations
- NEVER expose other users' data through API responses

### X. Automated Deployment via CI/CD

Deployment MUST be automated using GitHub Actions for frontend and Railway for backend.

**Deployment requirements**:
- Frontend deploys automatically via GitHub Actions to Vercel (or static host)
- Backend deploys automatically via Railway from GitHub repository
- All deployments MUST pass tests before going live
- Environment variables managed via GitHub Secrets and Railway dashboard
- Health checks configured for backend monitoring

**CI/CD principles**:
- NEVER deploy without passing tests
- AUTOMATE deployment on merge to main branch
- MAINTAIN separate staging and production environments (if applicable)
- EXPOSE health check endpoint for monitoring

**Rationale**: Automated deployment reduces manual errors, ensures consistent environments, and enables rapid iteration.

**Non-negotiable rules**:
- DEPLOY frontend via GitHub Actions workflow
- DEPLOY backend via Railway with GitHub integration
- RUN all tests in CI pipeline before deployment
- STORE secrets in GitHub Secrets or Railway dashboard (never in code)
- IMPLEMENT health check endpoint for backend monitoring

## Phase II Technical Constraints

### Frontend

- **Framework**: Next.js 16+ (App Router only)
- **UI Library**: React 18+
- **Styling**: Tailwind CSS (or CSS Modules)
- **API Communication**: REST only (no GraphQL in Phase II)
- **Auth Integration**: Better Auth client
- **Build Target**: Node.js 18+ server or Vercel deployment

### Backend

- **Language**: Python 3.13+
- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Auth**: Better Auth (Python client)
- **Package Manager**: UV (REQUIRED)

### Database

- **Provider**: Neon Serverless PostgreSQL
- **ORM**: SQLModel (typed models)
- **Migrations**: Alembic with SQLModel support
- **Connection**: Asyncpg for async FastAPI
- **Isolation**: User-scoped queries with proper foreign keys

### Authentication

- **Provider**: Better Auth
- **Methods**: Email/password (primary), session-based
- **Middleware**: FastAPI dependency for route protection
- **Session Security**: HTTP-only cookies, CSRF protection

### Testing Requirements

- **Backend**: pytest with httpx for API testing
- **Frontend**: Jest + React Testing Library or Playwright
- **Coverage**: All core functionality (API endpoints, auth flows)
- **Test Types**: Unit tests (models, services), integration tests (API + auth)
- **Validation**: Tests MUST pass before considering task complete

### Deployment Requirements

- **Frontend Deployment**: GitHub Actions CI/CD → Vercel (or static host)
- **Backend Deployment**: Railway with GitHub integration
- **Database**: Neon Serverless PostgreSQL (external, already configured)
- **CI/CD Pipeline**: Automated testing and deployment on merge to main
- **Environment Management**: Secrets via GitHub Secrets (frontend) and Railway dashboard (backend)
- **Health Checks**: Backend MUST expose health endpoint for Railway monitoring
- **Rollback Strategy**: Git-based rollback via Railway dashboard or re-deploy previous commit

## Development Workflow

### 1. Feature Initiation

```bash
/sp.specify <feature-description>
```

**Output**: `/specs/<feature>/spec.md` with:
- User stories (prioritized P1, P2, P3)
- Acceptance scenarios (Given/When/Then)
- Functional requirements (FR-001, FR-002, etc.)
- Success criteria

### 2. Planning

```bash
/sp.plan
```

**Output**: `/specs/<feature>/plan.md` with:
- Technical context (Next.js, FastAPI, SQLModel, Neon, Better Auth)
- Constitution check (validates Phase II compliance)
- Project structure (frontend/, backend/, tests/)
- Complexity justifications (if any violations)
- MCP Context validation status

### 3. Task Breakdown

```bash
/sp.tasks
```

**Output**: `/specs/<feature>/tasks.md` with:
- Setup tasks (project initialization)
- Foundational tasks (database, auth, API structure)
- User story tasks (grouped by priority)
- Test tasks (TDD: written first, fail, then implement)

### 4. Implementation

```bash
/sp.implement
```

**Process**:
- Execute tasks in dependency order
- Fetch MCP context for each technology before implementation
- Write tests → Verify failure → Implement → Verify pass
- Commit after each logical task or group
- Create PHR (Prompt History Record) after implementation

### 5. Quality Gates

**Before considering feature complete**:
- ✅ All tests pass
- ✅ Spec acceptance criteria satisfied
- ✅ No constitution violations (or documented in Complexity Tracking)
- ✅ Code follows separation of concerns (frontend/backend/models)
- ✅ PHR created in `history/prompts/<feature>/`
- ✅ MCP context validated for all technologies used

## Governance

### Constitution Authority

This constitution supersedes all other development practices. When conflicts arise:

1. Constitution principles override convenience
2. Phase II scope overrides feature requests
3. Simplicity overrides architectural patterns
4. MCP context validation overrides training data assumptions

### Amendment Process

1. Propose change with rationale
2. Document impact on existing code
3. Update constitution version:
   - **MAJOR**: Backward-incompatible principle changes (e.g., new tech stack)
   - **MINOR**: New principles or expanded guidance
   - **PATCH**: Clarifications, typo fixes, non-semantic refinements
4. Update dependent templates (plan, spec, tasks)
5. Create migration plan for existing code (if needed)
6. Obtain approval before finalizing

### Compliance Verification

**Every PR/feature MUST**:
- Reference constitution principles in plan.md Constitution Check
- Document MCP context validation status
- Justify any complexity or deviations in Complexity Tracking table
- Pass all tests (TDD compliance)
- Maintain separation of concerns (frontend/backend/services)

**Violations require**:
- Documented justification
- Exploration of simpler alternatives
- Explicit approval before proceeding

### Runtime Guidance

See `CLAUDE.md` for Claude Code-specific development instructions, including:
- PHR creation workflow
- ADR suggestion criteria
- MCP tool usage
- Human-as-Tool invocation triggers

**Version**: 2.0.0 | **Ratified**: 2026-01-01 | **Last Amended**: 2026-01-13

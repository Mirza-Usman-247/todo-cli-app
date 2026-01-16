<!--
Sync Impact Report (2026-01-15)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Version Change: 2.0.0 → 3.0.0
Rationale: Major backward-incompatible evolution from Phase II (web application)
to Phase III (AI-Powered Chatbot with MCP integration and OpenAI Agents SDK)

Modified Principles:
  - I. Spec-Driven Development: Expanded with mandatory MCP Context Server validation
  - II. Phase-Scoped Development: Web scope → AI Chatbot with MCP + Agents SDK scope
  - V. Persistent Database Architecture: Expanded to include conversation state storage
  - VI. Separation of Concerns: Expanded for AI layer (Agent/MCP/Backend)
  - VII. MCP Context-First Development: CRITICAL - now mandatory for every planning/implementation phase

Added Principles:
  - XI. MCP-First Tool Execution (Hard Rule)
  - XII. Agentic AI Behavioral Constitution
  - XIII. Stateless Conversation Architecture

Updated Sections:
  - Phase III Technical Constraints (OpenAI Agents SDK, Official MCP SDK, ChatKit UI)
  - MCP Context Validation Requirement (elevated to Phase 0 gate)
  - Agent behavioral rules and error handling

Removed Sections:
  - None (Phase II constraints retained for reference)

Templates Status:
  ✅ .specify/templates/plan-template.md - MCP context check already present
  ✅ .specify/templates/spec-template.md - Supports AI features
  ✅ .specify/templates/tasks-template.md - Supports agent workflow tasks
  ⚠ CLAUDE.md - Update to emphasize MCP-first and agent integration

Follow-up TODOs:
  - Validate that MCP Context Server is accessible before /sp.plan
  - Create skill for OpenAI Agents SDK integration patterns
  - Document conversation state schema in data-model.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-->

# The Evolution of Todo - Phase III Constitution

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

Phase III scope is strictly limited to AI-powered chatbot integration with MCP tools and OpenAI Agents SDK.

**In Scope**:
- AI-powered chatbot interface using OpenAI ChatKit UI
- OpenAI Agents SDK integration (single task-oriented agent)
- MCP Server built with Official MCP SDK
- MCP tools for all todo CRUD operations (add_task, list_tasks, complete_task, delete_task, update_task)
- Task explanation capability (fetch task data via MCP, analyze, explain intent)
- Conversation state persistence in Neon PostgreSQL
- Stateless backend server (no in-memory session storage)
- User-scoped conversation history and task isolation
- All Phase I and Phase II features preserved

**Out of Scope** (Failure conditions):
- Direct database access from AI agent (MUST use MCP tools only)
- In-memory conversation state or session storage
- Multiple AI agents or agent orchestration
- Custom authentication beyond Better Auth
- Real-time streaming features beyond basic chat
- Mobile native applications
- Any Phase IV+ functionality

**Rationale**: Constraining scope to Phase III ensures proper MCP architecture, stateless design, and production-ready AI integration without premature complexity.

**Non-negotiable rules**:
- REJECT any implementation that bypasses MCP tools for data operations
- REJECT any implementation that stores conversation state in memory
- DOCUMENT scope violations if discovered during implementation
- REQUEST clarification if a requirement could expand beyond Phase III

### III. Test-First Development (TDD)

Test-Driven Development is MANDATORY for all feature implementation, including MCP tools and agent workflows.

**Red-Green-Refactor cycle**:
1. **Red**: Write tests that fail (verify failure)
2. **Green**: Implement minimum code to pass tests
3. **Refactor**: Clean up while keeping tests green

**AI-specific testing requirements**:
- MCP tool contract tests (verify tool signatures and responses)
- Agent workflow tests (verify correct tool selection and execution)
- Conversation state persistence tests
- User isolation tests for conversations and tasks

**Rationale**: TDD ensures code correctness, prevents regressions, and serves as living documentation, especially critical for AI systems with complex state management.

**Non-negotiable rules**:
- Tests MUST be written BEFORE implementation code
- Tests MUST fail initially (verify red state)
- Implementation proceeds ONLY after test approval
- ALL acceptance criteria MUST have corresponding tests
- MCP tools MUST have contract tests before integration

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

### V. Persistent Database Architecture

Data is stored in Neon Serverless PostgreSQL using SQLModel for ORM, including conversation state.

**Data flow**:
- Application startup → SQLModel connects to Neon PostgreSQL
- User operation → Modify data via SQLModel models
- AI conversation → Load conversation history, execute MCP tools, save updated history
- Changes → Auto-committed by session or explicit flush
- Error handling → Rollback on failure, graceful reconnection

**Conversation state storage**:
- Conversation history stored per user in database
- Each request loads conversation context from database
- Agent response appended to conversation history
- Updated history persisted before returning response
- No in-memory conversation state between requests

**Rationale**: Provides production-grade persistence with type safety and migrations suitable for Phase III scope, ensuring stateless server architecture.

**Non-negotiable rules**:
- ALL todos MUST persist to Neon PostgreSQL via SQLModel
- ALL conversation history MUST persist to Neon PostgreSQL
- NO in-memory conversation state between requests
- Domain models MUST be separate from persistence models
- SQLModel relationships MUST be properly defined for user isolation
- Database migrations MUST be environment-safe (dev/staging/prod)

### VI. Separation of Concerns

Clean architecture with distinct layers for full-stack application with AI integration:

**Required structure**:
```
backend/
├── models/          # SQLAlchemy/SQLModel persistence models (todos, conversations)
├── schemas/         # Pydantic request/response schemas
├── api/             # FastAPI route handlers (including /api/{user_id}/chat)
├── services/        # Business logic (orchestrates models/schemas)
├── agent/           # AI agent configuration and initialization
├── mcp/             # MCP server and tool definitions
└── db/              # Database connection and session management

frontend/
├── app/             # Next.js App Router pages
├── components/      # React components (including ChatKit UI)
├── services/        # API client wrappers
└── types/           # TypeScript shared types

mcp_server/          # Standalone MCP server (if separate process)
├── tools/           # MCP tool implementations (add_task, list_tasks, etc.)
├── schemas/         # MCP tool schemas
└── server.py        # MCP server entry point

tests/
├── backend/         # FastAPI tests (pytest)
├── frontend/        # Next.js tests (Jest/Playwright)
├── mcp/             # MCP tool contract tests
└── agent/           # Agent workflow tests
```

**Rationale**: Separation enables testing, maintainability, and future refactoring across full-stack with AI integration. Clear boundaries between AI layer, MCP layer, and backend prevent tight coupling.

**Non-negotiable rules**:
- Models MUST NOT contain business logic or API concerns
- API routes MUST NOT contain business logic (delegate to services)
- Agent logic MUST NOT directly access database (use MCP tools only)
- MCP tools MUST be stateless and delegate to backend services
- Services MUST NOT import frontend components
- Each layer has clear, testable responsibilities

### VII. MCP Context-First Development

Before any implementation, the agent MUST connect to MCP Context Server and fetch latest official documentation for all technologies used.

**Required MCP Context Validations (Phase III)**:
1. OpenAI Agents SDK - Verify agent initialization, tool execution, conversation patterns
2. Official MCP SDK - Verify tool definitions, server setup, protocol compliance
3. FastAPI - Verify dependency injection, request validation, response models
4. SQLModel - Verify model definitions, relationships, session management
5. Neon Serverless PostgreSQL - Verify connection patterns, serverless compatibility
6. Better Auth - Verify installation, configuration, middleware integration
7. OpenAI ChatKit UI - Verify integration patterns, event handling, styling

**Rationale**: Ensures implementation follows current best practices and avoids deprecated patterns, CRITICAL for rapidly evolving AI frameworks.

**Non-negotiable rules**:
- NEVER rely on training data assumptions for framework APIs
- ALWAYS fetch and validate documentation via MCP before implementation
- VERIFY APIs, configurations, auth flows against official docs
- UPDATE MCP context if new versions are released during development
- FAIL planning phase if MCP context cannot be validated
- DOCUMENT all MCP context validation in plan.md Phase 0

### VIII. RESTful API Design

All API endpoints MUST follow RESTful conventions with proper schemas, including chatbot endpoint.

**Design principles**:
- Resource-based URLs (/todos, /users, /auth/, /chat)
- HTTP methods as intended (GET=read, POST=create, PUT=replace, PATCH=update, DELETE=remove)
- Proper status codes (200, 201, 400, 401, 403, 404, 422, 500)
- Versioned API path (/api/v1/...)

**Chatbot endpoint**:
- POST /api/{user_id}/chat - Accept user message, return agent response
- Request: User message + conversation context (loaded from DB)
- Response: Agent response + updated conversation state (saved to DB)
- Stateless: No session storage between requests

**Request/Response contracts**:
- ALL endpoints MUST have Pydantic request models
- ALL endpoints MUST have typed response models
- Error responses MUST follow consistent format with error codes
- Authenticated endpoints MUST validate session on every request

**Rationale**: Consistent API design enables frontend integration, testing, and future extensibility, especially critical for stateless AI chatbot architecture.

**Non-negotiable rules**:
- NEVER expose internal models directly in API responses
- VALIDATE all inputs with Pydantic schemas
- DOCUMENT all endpoints with OpenAPI (FastAPI automatic)
- RETURN appropriate HTTP status codes for all outcomes
- LOAD conversation state from database on every chat request
- SAVE updated conversation state to database after every response

### IX. Auth-Aware Architecture

Authentication MUST be implemented using Better Auth with proper middleware enforcement and user isolation for conversations.

**Auth requirements**:
- User signup and signin with email/password
- Secure session/token handling via Better Auth
- Auth middleware enforced on ALL protected routes (including /chat)
- User isolation: users can ONLY access their own todos and conversations

**Security rules**:
- NO custom authentication logic unless explicitly required by spec
- Session tokens MUST be validated on every protected request
- Passwords MUST be hashed by Better Auth (bcrypt/argon2)
- API endpoints MUST check ownership before data access
- Chat endpoint MUST validate user_id matches authenticated user

**Rationale**: Proper auth prevents unauthorized access and ensures multi-user isolation for both todos and conversations.

**Non-negotiable rules**:
- USE Better Auth for all authentication flows
- PROTECT all TODO and CHAT API endpoints with auth middleware
- VALIDATE user ownership before any modify/delete operations
- NEVER expose other users' data or conversations through API responses
- NEVER allow cross-user conversation access

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

### XI. MCP-First Tool Execution (Hard Rule)

The AI agent MUST use MCP tools exclusively for all todo CRUD operations. Direct database access from the agent is STRICTLY PROHIBITED.

**MCP tool architecture**:
- MCP server exposes tools: add_task, list_tasks, complete_task, delete_task, update_task
- Agent selects appropriate tool based on user intent
- MCP tool delegates to backend services for database operations
- Backend services enforce user isolation and data validation
- Agent receives structured response from MCP tool

**Tool execution flow**:
1. User sends message to /api/{user_id}/chat
2. Backend loads conversation history from database
3. Agent analyzes user intent and selects MCP tool
4. MCP tool executes via backend service (with user_id context)
5. Backend service performs database operation with validation
6. MCP tool returns structured result to agent
7. Agent formats response for user
8. Backend saves updated conversation to database

**Rationale**: MCP architecture ensures separation of concerns, enables testing, and prevents agent from direct database manipulation, maintaining data integrity and security.

**Non-negotiable rules**:
- Agent MUST NEVER access database directly
- Agent MUST NEVER fabricate task data
- Agent MUST use MCP tools for ALL task operations
- MCP tools MUST be stateless (no internal state)
- MCP tools MUST delegate to backend services for persistence
- Backend services MUST enforce user isolation for all MCP tool requests
- FETCH task data via MCP before explaining task purpose

### XII. Agentic AI Behavioral Constitution

The AI agent MUST follow strict behavioral rules for user interaction and error handling.

**Task operation mapping**:
- User intent: "add task" → add_task tool
- User intent: "list tasks" → list_tasks tool
- User intent: "complete task" → complete_task tool
- User intent: "delete task" → delete_task tool
- User intent: "update task" → update_task tool

**Task explanation workflow**:
When user asks: "What is this task for?", "Why did I create this?", "Explain task X"
1. Agent MUST fetch task via list_tasks or specific lookup
2. Agent MUST analyze task title + description
3. Agent MUST explain intent in natural language
4. Agent MUST NOT assume information beyond stored data

**Ambiguity handling**:
- If user intent is unclear → Ask clarification question
- If multiple interpretations exist → Present options to user
- NEVER guess or assume user intent
- NEVER proceed without clear understanding

**Error handling**:
- Task not found → Polite, clear message ("I couldn't find that task")
- Invalid command → Ask user to rephrase ("Could you clarify what you'd like to do?")
- Tool failure → Explain failure, do not hide it ("There was an error updating the task")

**Rationale**: Clear behavioral rules ensure consistent, user-friendly interactions and prevent agent from making incorrect assumptions or hiding errors.

**Non-negotiable rules**:
- ALWAYS fetch task data before explaining
- ALWAYS ask for clarification when ambiguous
- NEVER fabricate or assume task information
- NEVER hide errors or tool failures from user
- ALWAYS provide clear confirmations for actions ("Task added successfully")
- ALWAYS use human-friendly language (avoid technical jargon)

### XIII. Stateless Conversation Architecture

The backend server MUST be stateless with all conversation state stored in the database.

**Stateless server requirements**:
- NO in-memory conversation storage
- NO session variables for conversation context
- NO global state for agent conversations
- Each request is independent and self-contained

**Conversation state management**:
- Conversation history stored in database per user
- Each chat request loads full conversation history
- Agent processes message with conversation context
- Response appended to conversation history
- Updated history saved to database before response
- Next request loads fresh from database

**Database schema requirements**:
- conversations table with user_id foreign key
- messages table with conversation_id foreign key
- Proper indexes for efficient retrieval
- Conversation isolation by user_id

**Rationale**: Stateless architecture enables horizontal scaling, crash recovery, and prevents memory leaks from long-running conversations.

**Non-negotiable rules**:
- NEVER store conversation state in memory between requests
- ALWAYS load conversation history from database
- ALWAYS save updated conversation history before returning response
- ALWAYS enforce user isolation for conversation access
- VALIDATE conversation ownership before loading
- HANDLE concurrent requests gracefully (optimistic locking if needed)

## Phase III Technical Constraints

### Frontend

- **Framework**: Next.js 16+ (App Router only)
- **UI Library**: React 18+
- **Chat UI**: OpenAI ChatKit UI (clean, neutral, modern style)
- **Styling**: Tailwind CSS (or CSS Modules) - minimal, product-like
- **API Communication**: REST only (POST /api/{user_id}/chat)
- **Auth Integration**: Better Auth client
- **Build Target**: Node.js 18+ server or Vercel deployment

### Backend

- **Language**: Python 3.13+
- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Auth**: Better Auth (Python client)
- **AI SDK**: OpenAI Agents SDK (REQUIRED)
- **MCP SDK**: Official MCP SDK (REQUIRED)
- **Package Manager**: UV (REQUIRED)

### AI Layer

- **Agent Framework**: OpenAI Agents SDK
- **Agent Type**: Single task-oriented agent
- **Tool Protocol**: MCP (Model Context Protocol)
- **Conversation Management**: Database-backed stateless architecture
- **Agent Capabilities**: Intent recognition, tool selection, response generation, task explanation

### MCP Server

- **SDK**: Official MCP SDK
- **Tools**: add_task, list_tasks, complete_task, delete_task, update_task
- **Tool Architecture**: Stateless, delegate to backend services
- **Tool Schemas**: Strongly typed with Pydantic
- **User Context**: user_id passed with every tool invocation
- **Deployment**: Integrated with backend (or standalone process if required)

### Database

- **Provider**: Neon Serverless PostgreSQL
- **ORM**: SQLModel (typed models)
- **Migrations**: Alembic with SQLModel support
- **Connection**: Asyncpg for async FastAPI
- **Isolation**: User-scoped queries with proper foreign keys
- **New Schema**: conversations, messages tables for chat history

### Authentication

- **Provider**: Better Auth
- **Methods**: Email/password (primary), session-based
- **Middleware**: FastAPI dependency for route protection
- **Session Security**: HTTP-only cookies, CSRF protection
- **Chat Protection**: /api/{user_id}/chat MUST validate user_id matches authenticated user

### Testing Requirements

- **Backend**: pytest with httpx for API testing
- **Frontend**: Jest + React Testing Library or Playwright
- **MCP Tools**: Contract tests for tool signatures and responses
- **Agent Workflows**: Tests for tool selection and execution
- **Conversation State**: Tests for persistence and isolation
- **Coverage**: All core functionality (API endpoints, auth flows, MCP tools, agent workflows)
- **Test Types**: Unit tests (models, services), integration tests (API + auth + agent), contract tests (MCP tools)
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

### 0. MCP Context Validation (Phase 0 - BLOCKING)

```bash
# Validate MCP Context Server access
# Fetch documentation for:
# - OpenAI Agents SDK
# - Official MCP SDK
# - FastAPI
# - SQLModel
# - Neon Serverless PostgreSQL
# - Better Auth
# - OpenAI ChatKit UI

# GATE: Cannot proceed to planning without successful MCP context validation
```

**Output**: MCP context validation report in plan.md Phase 0

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
- MCP context validation status (Phase 0)
- Technical context (OpenAI Agents SDK, MCP SDK, Next.js, FastAPI, SQLModel, Neon, Better Auth, ChatKit UI)
- Constitution check (validates Phase III compliance)
- Project structure (frontend/, backend/, mcp_server/, tests/)
- Complexity justifications (if any violations)

### 3. Task Breakdown

```bash
/sp.tasks
```

**Output**: `/specs/<feature>/tasks.md` with:
- Setup tasks (project initialization)
- Foundational tasks (database, auth, API structure, MCP server, agent initialization)
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
- ✅ All tests pass (including MCP tool contract tests and agent workflow tests)
- ✅ Spec acceptance criteria satisfied
- ✅ No constitution violations (or documented in Complexity Tracking)
- ✅ Code follows separation of concerns (frontend/backend/agent/mcp/models)
- ✅ Agent uses MCP tools exclusively (no direct database access)
- ✅ Conversation state persisted correctly (stateless server validated)
- ✅ User isolation enforced for todos and conversations
- ✅ PHR created in `history/prompts/<feature>/`
- ✅ MCP context validated for all technologies used

## Governance

### Constitution Authority

This constitution supersedes all other development practices. When conflicts arise:

1. Constitution principles override convenience
2. Phase III scope overrides feature requests
3. MCP-first architecture overrides direct database access
4. Stateless design overrides in-memory state convenience
5. Simplicity overrides architectural patterns
6. MCP context validation overrides training data assumptions

### Amendment Process

1. Propose change with rationale
2. Document impact on existing code
3. Update constitution version:
   - **MAJOR**: Backward-incompatible principle changes (e.g., new tech stack, architectural shift)
   - **MINOR**: New principles or expanded guidance
   - **PATCH**: Clarifications, typo fixes, non-semantic refinements
4. Update dependent templates (plan, spec, tasks)
5. Create migration plan for existing code (if needed)
6. Obtain approval before finalizing

### Compliance Verification

**Every PR/feature MUST**:
- Reference constitution principles in plan.md Constitution Check
- Document MCP context validation status (Phase 0)
- Justify any complexity or deviations in Complexity Tracking table
- Pass all tests (TDD compliance, MCP contract tests, agent workflow tests)
- Maintain separation of concerns (frontend/backend/agent/mcp/services)
- Validate MCP-first architecture (no direct database access from agent)
- Validate stateless server (no in-memory conversation state)

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
- Agent integration patterns

**Version**: 3.0.0 | **Ratified**: 2026-01-01 | **Last Amended**: 2026-01-15

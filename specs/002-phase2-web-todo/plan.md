# Implementation Plan: Phase 2 - Todo Web Application

**Branch**: `002-phase2-web-todo` | **Date**: 2026-01-13 | **Spec**: [Link](spec.md)
**Input**: Feature specification from `specs/002-phase2-web-todo/spec.md`

## Summary

Transform the existing console todo application into a multi-user web application with persistent storage. The system consists of a Next.js 16+ frontend communicating via REST APIs to a FastAPI backend backed by Neon Serverless PostgreSQL, with user authentication handled by Better Auth. All five basic features (create, read, update, delete, complete todos) are delivered through a responsive web interface with per-user data isolation.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5+ (frontend)
**Primary Dependencies**: FastAPI 0.109+, Next.js 16+, SQLModel, Better Auth, Pydantic 2.x
**Storage**: Neon Serverless PostgreSQL (async connection via SQLModel + asyncpg)
**Testing**: pytest + httpx (backend), Jest/Playwright (frontend)
**Target Platform**: Linux server (FastAPI), Vercel/Node.js 18+ (Next.js)
**Project Type**: Full-stack web application (frontend + backend)
**Performance Goals**: API response < 2s, page load < 3s, 99% uptime
**Constraints**: REST APIs only (no GraphQL), Better Auth only (no custom auth), No hard-coded secrets
**Scale/Scope**: Individual users, ~20 todos per page, Phase 2 scope only

## Constitution Check

**Phase II Compliance - PASS**

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ | Following SDD workflow (spec → plan → tasks → implement) |
| II. Phase-Scoped Development | ✅ | Web app scope only, no WebSocket/OAuth/AI features |
| III. Test-First Development | ✅ | TDD required for all implementation |
| IV. Minimal Viable Simplicity | ✅ | No premature abstractions planned |
| V. Persistent Database Architecture | ✅ | Neon PostgreSQL + SQLModel |
| VI. Separation of Concerns | ✅ | Frontend/backend/services structure defined |
| VII. MCP Context-First | ✅ | Phase 1.3 tasks (M001-M005) enforce validation |
| VIII. RESTful API Design | ✅ | Resource-based endpoints, proper schemas |
| IX. Auth-Aware Architecture | ✅ | Better Auth with middleware enforcement |
| X. Automated Deployment via CI/CD | ✅ | GitHub Actions (frontend) + Railway (backend) |

**GATE Status**: ✅ PASS - All constitution requirements satisfied

## System Architecture

### Frontend Architecture (Next.js 16+ App Router)

```
frontend/
├── app/                          # Next.js App Router pages
│   ├── (auth)/                   # Authenticated route group
│   │   ├── page.tsx              # Dashboard (todo list)
│   │   ├── layout.tsx            # Authenticated layout with nav
│   │   └── new/page.tsx          # Create todo page
│   ├── (public)/                 # Public route group
│   │   ├── signin/page.tsx       # Sign in page
│   │   ├── signup/page.tsx       # Sign up page
│   │   └── layout.tsx            # Public layout
│   ├── api/                      # API routes (if needed)
│   └── globals.css               # Global styles (Tailwind)
├── components/                   # React components
│   ├── ui/                       # Base UI components (buttons, inputs)
│   ├── todo/                     # Todo-specific components
│   │   ├── TodoList.tsx
│   │   ├── TodoItem.tsx
│   │   ├── CreateTodoForm.tsx
│   │   └── UpdateTodoForm.tsx
│   └── auth/                     # Auth components
│       ├── SignInForm.tsx
│       └── SignUpForm.tsx
├── services/                     # API client wrappers
│   ├── api.ts                    # Base API client (fetch wrapper)
│   ├── auth.service.ts           # Auth API calls
│   └── todo.service.ts           # Todo CRUD API calls
├── types/                        # TypeScript shared types
│   ├── todo.ts
│   ├── user.ts
│   └── api.ts
├── hooks/                        # Custom React hooks
│   ├── useTodos.ts
│   ├── useAuth.ts
│   └── usePagination.ts
└── lib/                          # Utilities
    └── utils.ts
```

**Frontend Architecture Decisions**:
- App Router with route groups for auth/unauth separation
- Server Components for initial data fetch (optional)
- Client Components for interactive forms
- Tailwind CSS for responsive styling
- REST API calls from client components (no GraphQL)

### Backend Architecture (FastAPI)

```
backend/
├── src/
│   ├── models/                   # SQLModel persistence models
│   │   ├── user.py               # User SQLModel
│   │   ├── todo.py               # Todo SQLModel
│   │   └── database.py           # Database connection
│   ├── schemas/                  # Pydantic request/response
│   │   ├── user.py               # User schemas
│   │   ├── todo.py               # Todo schemas
│   │   └── auth.py               # Auth response schemas
│   ├── api/                      # FastAPI route handlers
│   │   ├── __init__.py
│   │   ├── auth.py               # Auth endpoints
│   │   ├── todos.py              # Todo CRUD endpoints
│   │   └── users.py              # User endpoints
│   ├── services/                 # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py       # Auth business logic
│   │   ├── todo_service.py       # Todo business logic
│   │   └── user_service.py       # User business logic
│   ├── db/                       # Database layer
│   │   ├── connection.py         # Neon connection
│   │   └── session.py            # Session management
│   └── main.py                   # FastAPI application entry
├── tests/
│   ├── conftest.py               # Pytest fixtures
│   ├── unit/
│   │   ├── test_models.py
│   │   └── test_schemas.py
│   └── integration/
│       ├── test_auth.py
│       └── test_todos.py
└── alembic/                      # Database migrations
    └── versions/
```

**Backend Architecture Decisions**:
- SQLModel for type-safe ORM with SQLAlchemy under the hood
- Pydantic for request validation and response serialization
- Dependency injection for auth and database sessions
- Services encapsulate business logic (Constitution VI compliance)
- API routes delegate to services (no business logic in routes)

### Authentication Flow (Better Auth)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Better Auth Integration                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Frontend (Next.js)                                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Better Auth Client                                      │    │
│  │  - signIn.signUp(email, password)                        │    │
│  │  - signIn.signIn(email, password)                        │    │
│  │  - signOut()                                             │    │
│  │  - useSession() hook                                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  HTTP Requests (REST API)                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Headers:                                                │    │
│  │  - Content-Type: application/json                       │    │
│  │  - Cookie: bettersession=... (HTTP-only)                │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  Backend (FastAPI)                                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Better Auth Python Client                               │    │
│  │  - auth.api.signUp() endpoint                            │    │
│  │  - auth.api.signIn() endpoint                            │    │
│  │  - auth.api.session() endpoint                           │    │
│  │  - auth.middleware() for protected routes                │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  Database (Neon PostgreSQL)                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Tables:                                                 │    │
│  │  - user (id, email, password_hash, created_at, ...)     │    │
│  │  - session (id, user_id, token, expires_at, ...)        │    │
│  │  - verification (email verification tokens)              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Auth Integration Points**:
- Better Auth Python client on FastAPI backend
- Better Auth React client on Next.js frontend
- HTTP-only cookies for session tokens (CSRF protected)
- Sliding session expiration (24h inactivity) managed by Better Auth
- Multiple concurrent sessions allowed per user

### Database Schema Strategy (SQLModel + Neon)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Database Schema (Neon PostgreSQL)             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  user                                                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ id: UUID (PK)                                           │    │
│  │ email: VARCHAR(255) (UNIQUE, NOT NULL)                  │    │
│  │ password_hash: VARCHAR(255) (NOT NULL)                  │    │
│  │ created_at: TIMESTAMP (NOT NULL, default now())         │    │
│  │ updated_at: TIMESTAMP (NOT NULL)                        │    │
│  │ deleted_at: TIMESTAMP (NULL, for soft delete)           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              │ 1:N                              │
│                              ▼                                   │
│  todo                                                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ id: UUID (PK)                                           │    │
│  │ user_id: UUID (FK to user.id, NOT NULL)                 │    │
│  │ title: VARCHAR(255) (NOT NULL)                          │    │
│  │ description: TEXT (NULL)                                │    │
│  │ is_completed: BOOLEAN (NOT NULL, default false)         │    │
│  │ created_at: TIMESTAMP (NOT NULL, default now())         │    │
│  │ updated_at: TIMESTAMP (NOT NULL)                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  session (Managed by Better Auth)                                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ id: VARCHAR(255) (PK)                                   │    │
│  │ user_id: UUID (FK to user.id, NOT NULL)                 │    │
│  │ expires_at: TIMESTAMP (NOT NULL)                        │    │
│  │ token: VARCHAR(255) (NOT NULL)                          │    │
│  │ ip_address: VARCHAR(45) (NULL)                          │    │
│  │ user_agent: TEXT (NULL)                                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Schema Design Principles**:
- UUID primary keys for scalability
- Soft delete on users (30-day retention per policy)
- Foreign key constraints enforce user isolation
- Index on user_id for todo queries (pagination performance)
- Timestamps on all entities for audit trail
- SQLModel relationships for type-safe queries

## Data Flow

### Authenticated Request Lifecycle

```
┌──────────────────────────────────────────────────────────────────────┐
│              Authenticated User Request Flow                          │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  1. User Action                                                       │
│     ┌──────────┐     ┌──────────────┐     ┌──────────────────┐      │
│     │  User    │────▶│  Frontend    │────▶│  REST API Call   │      │
│     │  clicks  │     │  Component   │     │  (fetch/axios)   │      │
│     └──────────┘     └──────────────┘     └────────┬─────────┘      │
│                                                      │               │
│                                                      ▼               │
│  2. API Request (with Session Cookie)                                 │
│     ┌─────────────────────────────────────────────────────────────┐  │
│     │  Request Headers:                                            │  │
│     │  - Content-Type: application/json                            │  │
│     │  - Cookie: bettersession=abc123... (HTTP-only)               │  │
│     │  - Authorization: (if using Bearer token)                    │  │
│     └─────────────────────────────────────────────────────────────┘  │
│                              │                                        │
│                              ▼                                        │
│  3. FastAPI Middleware Chain                                          │
│     ┌─────────────────────────────────────────────────────────────┐  │
│     │  1. CORSMiddleware (allow frontend origin)                   │  │
│     │  2. SessionMiddleware (validate cookie, extract session)     │  │
│     │  3. AuthMiddleware (protect routes, inject session)          │  │
│     │  4. RequestLogger (optional, trace requests)                 │  │
│     └─────────────────────────────────────────────────────────────┘  │
│                              │                                        │
│                              ▼                                        │
│  4. Route Handler + Dependency Injection                              │
│     ┌─────────────────────────────────────────────────────────────┐  │
│     │  def get_todos(session: Session = Depends(get_session)):    │  │
│     │      # session.user is available from auth middleware       │  │
│     │      todos = service.list_todos(user_id=session.user.id)    │  │
│     └─────────────────────────────────────────────────────────────┘  │
│                              │                                        │
│                              ▼                                        │
│  5. Service Layer (Business Logic)                                    │
│     ┌─────────────────────────────────────────────────────────────┐  │
│     │  def list_todos(user_id: UUID) -> List[TodoResponse]:       │  │
│     │      # Query with user_id filter (enforce isolation)        │  │
│     │      return db.query(Todo).filter(Todo.user_id == user_id)  │  │
│     │          .order_by(Todo.created_at.desc()).offset(0).limit(20)│ │
│     └─────────────────────────────────────────────────────────────┘  │
│                              │                                        │
│                              ▼                                        │
│  6. Database Query (SQLModel)                                         │
│     ┌─────────────────────────────────────────────────────────────┐  │
│     │  SELECT * FROM todo                                         │  │
│     │  WHERE user_id = ? AND deleted_at IS NULL                   │  │
│     │  ORDER BY created_at DESC                                   │  │
│     │  LIMIT 20 OFFSET 0                                          │  │
│     └─────────────────────────────────────────────────────────────┘  │
│                              │                                        │
│                              ▼                                        │
│  7. Response (Pydantic Schema)                                        │
│     ┌─────────────────────────────────────────────────────────────┐  │
│     │  HTTP 200 OK                                                │  │
│     │  {                                                         │  │
│     │    "todos": [                                              │  │
│     │      {"id": "...", "title": "...", "is_completed": false}  │  │
│     │    ],                                                      │  │
│     │    "total": 5,                                             │  │
│     │    "page": 1                                               │  │
│     │  }                                                         │  │
│     └─────────────────────────────────────────────────────────────┘  │
│                              │                                        │
│                              ▼                                        │
│  8. Frontend Update                                                   │
│     ┌──────────┐     ┌──────────────┐     ┌──────────────────┐      │
│     │  API     │────▶│  React       │────▶│  UI Re-render    │      │
│     │  Response│     │  State       │     │  (todo list)     │      │
│     └──────────┘     └──────────────┘     └──────────────────┘      │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

### API Request/Response Contracts

#### Authentication Endpoints

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| POST | /api/v1/auth/signup | Create account | {email, password} | {user, session} |
| POST | /api/v1/auth/signin | Sign in | {email, password} | {user, session} |
| POST | /api/v1/auth/signout | Sign out | {} | {success: true} |
| GET | /api/v1/auth/session | Get current session | Cookie | {user} or 401 |

#### Todo Endpoints

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | /api/v1/todos | List user's todos | ?page=1&limit=20 | {todos: [], total, page} |
| POST | /api/v1/todos | Create todo | {title, description?} | {todo} |
| GET | /api/v1/todos/{id} | Get single todo | Path param | {todo} |
| PUT | /api/v1/todos/{id} | Update todo | {title?, description?, is_completed?} | {todo} |
| DELETE | /api/v1/todos/{id} | Delete todo | Path param | {success: true} |

#### Error Responses

| Status | Error Code | Message |
|--------|------------|---------|
| 400 | VALIDATION_ERROR | Invalid input data |
| 401 | UNAUTHORIZED | Not authenticated |
| 403 | FORBIDDEN | Not authorized to access this resource |
| 404 | NOT_FOUND | Resource not found |
| 422 | UNPROCESSABLE_ENTITY | Validation error |
| 500 | INTERNAL_ERROR | Server error |

### Frontend ↔ Backend Interaction

```
┌─────────────────────────────────────────────────────────────────┐
│              Frontend/Backend Communication Pattern              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Service Layer Pattern (frontend/services/)                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  // api.ts (base client)                                │    │
│  │  const API_BASE = process.env.NEXT_PUBLIC_API_URL       │    │
│  │  async function fetchApi<T>(endpoint, options?) {       │    │
│  │    const res = await fetch(`${API_BASE}${endpoint}`, {  │    │
│  │      credentials: 'include',  // Send cookies            │    │
│  │      ...options                                        │    │
│  │    })                                                   │    │
│  │    if (!res.ok) throw await handleError(res)            │    │
│  │    return res.json() as T                               │    │
│  │  }                                                      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  // todo.service.ts                                      │    │
│  │  export async function getTodos(page = 1) {             │    │
│  │    return fetchApi<TodoListResponse>(`/api/v1/todos?page=${page}`)│    │
│  │  }                                                       │    │
│  │                                                          │    │
│  │  export async function createTodo(data) {               │    │
│  │    return fetchApi<Todo>('/api/v1/todos', {             │    │
│  │      method: 'POST',                                     │    │
│  │      body: JSON.stringify(data)                          │    │
│  │    })                                                    │    │
│  │  }                                                       │    │
│  │                                                          │    │
│  │  export async function updateTodo(id, data) {           │    │
│  │    return fetchApi<Todo>(`/api/v1/todos/${id}`, {       │    │
│  │      method: 'PUT',                                      │    │
│  │      body: JSON.stringify(data)                          │    │
│  │    })                                                    │    │
│  │  }                                                       │    │
│  │                                                          │    │
│  │  export async function deleteTodo(id) {                 │    │
│  │    return fetchApi<{success: boolean}>(`/api/v1/todos/${id}`,│    │
│  │      { method: 'DELETE' })                               │    │
│  │  }                                                       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  React Query / SWR Pattern (recommended for data fetching)       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  const { data: todos, isLoading, error, refetch } =     │    │
│  │    useQuery({ queryKey: ['todos', page],                │    │
│  │               queryFn: () => getTodos(page) })           │    │
│  │                                                          │    │
│  │  const mutation = useMutation({                          │    │
│  │    mutationFn: (data) => createTodo(data),              │    │
│  │    onSuccess: () => queryClient.invalidateQueries(...)  │    │
│  │  })                                                      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Communication Principles**:
- All API calls include `credentials: 'include'` for session cookies
- Environment variable for API base URL (no hard-coded URLs)
- Centralized error handling
- TypeScript types match Pydantic schemas
- Loading states managed by React Query/SWR

## Implementation Phases

### Phase 1: Project Scaffolding & Environment Setup

**Duration**: Setup only, no feature code

**Goals**:
- Create separate frontend and backend project structures
- Configure development environments (UV for backend, npm/pnpm for frontend)
- Set up Neon Serverless PostgreSQL connection
- Configure environment variables for both projects
- Establish linting, formatting, and type checking
- Create initial Git structure for mono-repo

**Deliverables**:
- `backend/` directory with FastAPI + SQLModel initialized
- `frontend/` directory with Next.js 16+ initialized
- `.env.example` files for both projects
- `docker-compose.yml` for local development (optional)
- Basic project README with setup instructions

**Dependencies**: None (foundational)

### Phase 2: Authentication Integration

**Goals**:
- Integrate Better Auth Python client with FastAPI
- Integrate Better Auth React client with Next.js
- Create auth pages (signup, signin)
- Implement session management with sliding expiration
- Protect API routes with auth middleware
- Handle auth errors gracefully

**Deliverables**:
- User signup endpoint and page
- User signin endpoint and page
- Signout functionality
- Protected todo API routes (return 401 for unauthenticated)
- Auth state management on frontend
- Redirect unauthenticated users to signin

**Dependencies**: Phase 1 complete

### Phase 3: Core Feature APIs

**Goals**:
- Define SQLModel entities (User, Todo)
- Create Pydantic schemas (request/response)
- Implement todo service layer (CRUD + user isolation)
- Build REST API endpoints for todos
- Implement pagination (20 items/page)
- Add input validation and error handling
- Write integration tests for all endpoints

**Deliverables**:
- `GET /api/v1/todos` - List todos with pagination
- `POST /api/v1/todos` - Create todo
- `GET /api/v1/todos/{id}` - Get single todo
- `PUT /api/v1/todos/{id}` - Update todo
- `DELETE /api/v1/todos/{id}` - Delete todo
- Unit tests for models and services
- Integration tests for all API endpoints

**Dependencies**: Phase 2 complete

### Phase 4: Frontend Feature Integration

**Goals**:
- Build todo list component with pagination UI
- Create todo form components (create, edit)
- Connect frontend to backend REST APIs
- Implement responsive design (mobile-friendly)
- Add loading states and error handling
- Display success/error feedback to users
- Write frontend tests

**Deliverables**:
- Dashboard page with todo list
- Create todo page and inline form
- Edit todo modal or page
- Delete confirmation dialog
- Responsive navigation
- Loading spinners and error messages
- Jest/Playwright tests for components

**Dependencies**: Phase 3 complete

### Phase 5: Validation, Error Handling, and Polish

**Goals**:
- Validate all user input on both frontend and backend
- Handle edge cases (network errors, session expiry)
- Add form validation with helpful error messages
- Polish UI (animations, transitions, empty states)
- Performance optimization (caching, lazy loading)
- Security review (ensure no data leaks)
- Final testing and bug fixes

**Deliverables**:
- Form validation on all inputs
- Network error handling with retry UI
- Session expiry handling (redirect to signin)
- Empty state for todos list
- Loading skeletons
- Accessibility improvements
- Performance audit and fixes

**Dependencies**: Phase 4 complete

### Phase 6: Deployment & CI/CD

**Goals**:
- Configure GitHub Actions workflow for frontend CI/CD
- Set up Railway deployment for backend
- Create health check endpoint for monitoring
- Configure environment variables in GitHub Secrets and Railway
- Test deployment pipeline end-to-end
- Document rollback procedures

**Deliverables**:
- GitHub Actions workflow file (`.github/workflows/deploy-frontend.yml`)
- Railway configuration file (`railway.json` or Procfile)
- Health check endpoint (`GET /health`) returning 200 OK
- Frontend deployed to Vercel (or static host) automatically on merge
- Backend deployed to Railway automatically on merge
- Deployment documentation in README
- Environment variable templates updated with deployment-specific vars

**Dependencies**: Phase 5 complete

## Deployment Architecture

### CI/CD Pipeline Flow

```
┌────────────────────────────────────────────────────────────────────┐
│                     Deployment Pipeline                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Developer Push/Merge to main                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  git push origin main                                        │  │
│  └─────────────────────────────┬───────────────────────────────┘  │
│                                │                                   │
│                                ▼                                   │
│  GitHub Actions Workflow                                           │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Frontend CI/CD (.github/workflows/deploy-frontend.yml)     │  │
│  │  1. Checkout code                                           │  │
│  │  2. Install dependencies (npm install)                      │  │
│  │  3. Run tests (npm test)                                    │  │
│  │  4. Build Next.js app (npm run build)                       │  │
│  │  5. Deploy to Vercel (vercel --prod)                        │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                │                                   │
│                                ▼                                   │
│  Frontend Deployed (Vercel)                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  URL: https://todo-app.vercel.app                           │  │
│  │  Environment: Production                                     │  │
│  │  Secrets: NEXT_PUBLIC_API_URL (from GitHub Secrets)         │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Railway Deployment (Backend)                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Railway watches GitHub repo (automatic)                     │  │
│  │  1. Detect push to main                                      │  │
│  │  2. Build Docker image or use Nixpacks                       │  │
│  │  3. Run migrations (alembic upgrade head)                    │  │
│  │  4. Run tests (pytest)                                       │  │
│  │  5. Deploy with zero-downtime rollout                        │  │
│  │  6. Health check: GET /health                                │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                │                                   │
│                                ▼                                   │
│  Backend Deployed (Railway)                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  URL: https://todo-api.railway.app                          │  │
│  │  Environment: Production                                     │  │
│  │  Secrets: DATABASE_URL, BETTER_AUTH_SECRET (Railway dash)   │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### GitHub Actions Workflow Configuration

**File**: `.github/workflows/deploy-frontend.yml`

```yaml
name: Deploy Frontend to Vercel

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci
      - name: Run tests
        working-directory: ./frontend
        run: npm test
      - name: Build
        working-directory: ./frontend
        run: npm run build
        env:
          NEXT_PUBLIC_API_URL: ${{ secrets.NEXT_PUBLIC_API_URL }}

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./frontend
```

### Railway Configuration

**File**: `backend/railway.json` (or use Railway dashboard)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Alternative**: `backend/Procfile` (if using Procfile)

```
web: alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

### Environment Variables Management

**GitHub Secrets** (for frontend deployment):
- `VERCEL_TOKEN`: Vercel API token
- `VERCEL_ORG_ID`: Vercel organization ID
- `VERCEL_PROJECT_ID`: Vercel project ID
- `NEXT_PUBLIC_API_URL`: Backend API URL (e.g., `https://todo-api.railway.app`)

**Railway Environment Variables** (for backend deployment):
- `DATABASE_URL`: Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET`: Auth secret key
- `BETTER_AUTH_URL`: Backend URL for CORS
- `FRONTEND_URL`: Frontend origin for CORS (e.g., `https://todo-app.vercel.app`)

### Health Check Endpoint

**Implementation**: `backend/src/api/health.py`

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "todo-api"}
```

This endpoint is used by Railway to monitor backend health and trigger restarts if unhealthy.

## Risks and Constraints

### Auth Integration Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Better Auth Python client has unexpected behavior | Medium | Validate with MCP docs before implementation; test thoroughly |
| Session cookie issues with cross-origin requests | High | Configure CORS properly; use credentials: 'include'; test with real browser |
| Session hijacking vulnerabilities | High | Use HTTP-only cookies; enable CSRF protection; consider IP binding |
| Password hashing not secure | High | Let Better Auth handle hashing; use bcrypt/argon2 |
| Multiple sessions not working correctly | Low | Test concurrent session scenario; use Better Auth's built-in support |

### Serverless Database Limitations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Cold start latency on Neon | Medium | Implement connection pooling; use keep-alive; accept initial latency |
| Connection limits on free tier | Medium | Monitor connection usage; implement proper cleanup; upgrade if needed |
| Serverless idle timeout disconnections | Low | Implement retry logic for failed queries; use asyncpg reconnection |
| Lack of local development database | Medium | Use Docker PostgreSQL for local dev; sync schema with Neon |
| Migration complexity | Low | Use Alembic for migrations; test migrations before production |

### Spec-Driven Enforcement Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Implementation drifts from spec | High | Use tasks.md for traceability; require spec reference in PRs |
| Claude Code skips TDD cycle | High | Enforce test-first in quality gates; review tests in PRs |
| Scope creep (Phase III features) | Medium | Reference Phase II scope in constitution; reject out-of-scope PRs |
| Missing MCP context validation | Medium | Add checklist item; validate before implementation tasks |
| Architecture violations (business logic in routes) | Medium | Review code structure in PRs; enforce separation of concerns |

### Deployment Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| GitHub Actions workflow fails | Medium | Test workflow locally with act; validate secrets configuration |
| Vercel deployment quota exceeded | Low | Monitor usage; upgrade plan if needed; consider alternative hosts |
| Railway deployment fails | Medium | Validate railway.json/Procfile; test with Railway CLI locally |
| Health check endpoint unreachable | High | Implement robust health check; test before deployment |
| Environment variable misconfiguration | High | Use .env.example templates; validate all vars before deploy |
| Database migration fails during deployment | Critical | Test migrations locally; implement rollback strategy |
| CORS issues in production | High | Configure CORS correctly; test with production URLs before go-live |
| Secrets exposed in logs or code | Critical | Audit code for hardcoded secrets; use GitHub Secret scanning |

### Technical Constraints Summary

| Constraint | Enforcement |
|------------|-------------|
| REST APIs only | No GraphQL dependencies; verify in code review |
| Better Auth only | No custom auth; use Better Auth Python/React clients |
| No hard-coded secrets | Use .env files; validate no secrets in code |
| User isolation enforced | Database queries must filter by user_id; test cross-user access |
| Pagination 20 items | API returns paginated results; frontend implements pagination UI |
| Automated deployment | GitHub Actions for frontend, Railway for backend |
| Health check required | Backend MUST expose /health endpoint for Railway monitoring |

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

## MCP Context Validation Status

| Technology | Status | Notes |
|------------|--------|-------|
| Next.js (App Router) | Task Created | M001 - Must validate before Phase 2+ |
| FastAPI | Task Created | M002 - Must validate before Phase 2+ |
| SQLModel | Task Created | M003 - Must validate before Phase 2+ |
| Neon PostgreSQL | Task Created | M004 - Must validate before Phase 2+ |
| Better Auth | Task Created | M005 - Must validate before Phase 2+ |

**Implementation**: Phase 1.3 (tasks.md) includes 5 parallel MCP validation tasks (M001-M005) that MUST complete before implementation begins.

## Project Structure

### Documentation (this feature)

```text
specs/002-phase2-web-todo/
├── plan.md              # This file (/sp.plan command output)
├── spec.md              # Feature specification (/sp.specify output)
├── research.md          # Phase 0 output (NOT NEEDED - spec is complete)
├── data-model.md        # Phase 1 output (inline in plan.md)
├── quickstart.md        # Phase 1 output (create after implementation)
├── contracts/           # Phase 1 output (API contracts inline)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/          # SQLModel persistence models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── api/             # FastAPI route handlers
│   ├── services/        # Business logic
│   ├── db/              # Database connection and session management
│   └── main.py          # FastAPI application entry
├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── alembic/
│   └── versions/
├── .env.example
├── pyproject.toml
└── uv.lock

frontend/
├── app/
│   ├── (auth)/          # Authenticated pages
│   ├── (public)/        # Public pages
│   └── api/             # API routes (if needed)
├── components/
│   ├── ui/
│   ├── todo/
│   └── auth/
├── services/            # API client wrappers
├── types/               # TypeScript types
├── hooks/               # Custom React hooks
├── .env.example
├── package.json
└── tsconfig.json

tests/
├── backend/             # Python tests (pytest)
└── frontend/            # TypeScript tests (Jest/Playwright)

.env                      # Environment variables (gitignored)
```

**Structure Decision**: Full-stack mono-repo with separate `backend/` and `frontend/` directories following Constitution VI separation of concerns. Each project has independent dependency management (UV for Python, npm/pnpm for Node.js).

## Next Steps

1. **Run `/sp.tasks`** to generate detailed task breakdown
2. **Validate MCP context** for all technologies before implementation
3. **Begin Phase 1**: Project scaffolding and environment setup
4. **Commit** after each phase completion
5. **Create PHR** after each phase

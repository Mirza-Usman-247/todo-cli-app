# Tasks: Phase 2 - Todo Web Application

**Input**: Design documents from `/specs/002-phase2-web-todo/`
**Prerequisites**: plan.md (required), spec.md (required)

**Organization**: Tasks are grouped by implementation phase and category. Each task has a single responsibility and clear acceptance criteria.

## Format: `[ID] [P?] [Story/Category] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Category]**: Backend, Database, Auth, API, Frontend, Integration
- Include exact file paths in descriptions

---

## Phase 1: Project Scaffolding & Environment Setup

**Purpose**: Initialize project structures and configurations

---

### Phase 1.1: Backend Setup

- [ ] B001 [P] [Backend] Create backend directory structure per plan.md

  **Reference**: plan.md - Project Structure section

  **Location**: `backend/`

  **Description**:
  Create the backend directory structure:
  ```
  backend/
  ├── src/
  │   ├── models/
  │   ├── schemas/
  │   ├── api/
  │   ├── services/
  │   ├── db/
  │   └── main.py
  ├── tests/
  │   ├── conftest.py
  │   ├── unit/
  │   └── integration/
  ├── alembic/
  │   └── versions/
  ├── .env.example
  ├── pyproject.toml
  └── uv.lock
  ```

  **Acceptance Criteria**:
  - [ ] All directories created
  - [ ] `__init__.py` files created in all Python packages
  - [ ] Directory structure matches plan.md exactly

---

- [ ] B002 [P] [Backend] Initialize Python project with UV and dependencies

  **Reference**: plan.md - Technical Context section

  **Location**: `backend/pyproject.toml`

  **Description**:
  Create `pyproject.toml` with:
  - Python 3.13+ requirement
  - FastAPI 0.109+
  - SQLModel
  - Better Auth Python client
  - Pydantic 2.x
  - pytest + httpx for testing
  - Alembic for migrations

  **Acceptance Criteria**:
  - [ ] `pyproject.toml` created with all dependencies
  - [ ] `uv.lock` generated
  - [ ] `uv sync` runs successfully

---

- [ ] B003 [P] [Backend] Configure environment variables template

  **Reference**: plan.md - Technical Context section, spec.md - Non-Functional Requirements

  **Location**: `backend/.env.example`

  **Description**:
  Create `.env.example` with placeholders for:
  - `DATABASE_URL` (Neon PostgreSQL connection string)
  - `BETTER_AUTH_SECRET` (auth secret key)
  - `BETTER_AUTH_URL` (backend URL for CORS)
  - `FRONTEND_URL` (frontend origin for CORS)
  - `DATABASE_HOST` (Neon host)
  - `DATABASE_USER` (Neon user)
  - `DATABASE_PASSWORD` (Neon password)
  - `DATABASE_NAME` (Neon database)

  **Acceptance Criteria**:
  - [ ] All environment variables documented
  - [ ] No actual secrets in file (all placeholders)
  - [ ] Comments explain each variable

---

- [ ] B004 [P] [Backend] Create FastAPI application entry point

  **Reference**: plan.md - Backend Architecture section

  **Location**: `backend/src/main.py`

  **Description**:
  Create `main.py` with:
  - FastAPI app initialization
  - CORS middleware configuration
  - Root route `/` returning health check
  - OpenAPI documentation setup

  **Acceptance Criteria**:
  - [ ] App starts with `uvicorn main:app --reload`
  - [ ] Health check at `GET /` returns 200 OK
  - [ ] CORS allows frontend origin from environment
  - [ ] OpenAPI docs accessible at `/docs`

---

- [ ] B005 [P] [Backend] Configure pytest and test fixtures

  **Reference**: Constitution III - Test-First Development

  **Location**: `backend/tests/conftest.py`

  **Description**:
  Create test configuration:
  - pytest configuration in `pyproject.toml`
  - `conftest.py` with fixtures for:
    - Test database session
    - Test client
    - App fixture

  **Acceptance Criteria**:
  - [ ] `pytest` runs without errors
  - [ ] Test discovery works (`pytest --collect-only`)
  - [ ] Fixtures can be imported in tests

---

### Phase 1.2: Frontend Setup

- [ ] F001 [P] [Frontend] Create frontend directory structure

  **Reference**: plan.md - Frontend Architecture section

  **Location**: `frontend/`

  **Description**:
  Create the frontend directory structure:
  ```
  frontend/
  ├── app/
  │   ├── (auth)/
  │   │   └── page.tsx
  │   ├── (public)/
  │   │   └── page.tsx
  │   ├── layout.tsx
  │   └── page.tsx
  ├── components/
  │   ├── ui/
  │   ├── todo/
  │   └── auth/
  ├── services/
  ├── types/
  ├── hooks/
  ├── lib/
  ├── .env.example
  ├── package.json
  ├── tsconfig.json
  └── tailwind.config.ts
  ```

  **Acceptance Criteria**:
  - [ ] All directories created
  - [ ] TypeScript files have basic exports
  - [ ] Directory structure matches plan.md

---

- [ ] F002 [P] [Frontend] Initialize Next.js 16+ project

  **Reference**: plan.md - Technical Context section

  **Location**: `frontend/package.json`, `frontend/tsconfig.json`

  **Description**:
  Create Next.js 16+ project configuration:
  - `package.json` with Next.js 16+, React 18+, TypeScript 5+
  - `tsconfig.json` configured for strict mode
  - App Router enabled

  **Acceptance Criteria**:
  - [ ] `npm install` runs successfully
  - [ ] `npm run dev` starts dev server
  - [ ] TypeScript compilation passes

---

- [ ] F003 [P] [Frontend] Configure Tailwind CSS and styling

  **Reference**: plan.md - Frontend Architecture Decisions

  **Location**: `frontend/tailwind.config.ts`, `frontend/app/globals.css`

  **Description**:
  Set up Tailwind CSS:
  - `tailwind.config.ts` with content paths
  - `globals.css` with Tailwind directives
  - Basic responsive breakpoints

  **Acceptance Criteria**:
  - [ ] Tailwind CSS builds without errors
  - [ ] CSS classes work in components
  - [ ] Responsive configuration present

---

- [ ] F004 [P] [Frontend] Create environment variables template

  **Reference**: spec.md - Non-Functional Requirements (no hard-coded secrets)

  **Location**: `frontend/.env.example`

  **Description**:
  Create `.env.example` with:
  - `NEXT_PUBLIC_API_URL` (backend API base URL)

  **Acceptance Criteria**:
  - [ ] API URL variable documented
  - [ ] No actual URLs in file

---

### Phase 1.3: MCP Context Validation

- [ ] M001 [P] [MCP] Validate Next.js 16+ App Router documentation

  **Reference**: Constitution VII - MCP Context-First Development, plan.md:586

  **Location**: MCP Context Server

  **Description**:
  Fetch and validate Next.js 16+ documentation via MCP:
  - App Router routing patterns
  - Server Components vs Client Components
  - Route groups and layouts
  - Middleware for auth protection

  **Acceptance Criteria**:
  - [ ] MCP docs fetched successfully
  - [ ] App Router patterns verified
  - [ ] Server/Client component patterns documented
  - [ ] Auth middleware approach confirmed

---

- [ ] M002 [P] [MCP] Validate FastAPI dependency injection and middleware

  **Reference**: Constitution VII - MCP Context-First Development, plan.md:587

  **Location**: MCP Context Server

  **Description**:
  Fetch and validate FastAPI documentation via MCP:
  - Dependency injection patterns
  - Middleware configuration
  - Request validation with Pydantic
  - Response models and status codes

  **Acceptance Criteria**:
  - [ ] MCP docs fetched successfully
  - [ ] Dependency injection patterns verified
  - [ ] Middleware approach confirmed
  - [ ] Pydantic validation patterns documented

---

- [ ] M003 [P] [MCP] Validate SQLModel relationships and async sessions

  **Reference**: Constitution VII - MCP Context-First Development, plan.md:588

  **Location**: MCP Context Server

  **Description**:
  Fetch and validate SQLModel documentation via MCP:
  - Model definition patterns
  - Relationships and foreign keys
  - Async session management
  - Query patterns with filters

  **Acceptance Criteria**:
  - [ ] MCP docs fetched successfully
  - [ ] Model relationships verified
  - [ ] Async session patterns documented
  - [ ] User isolation query patterns confirmed

---

- [ ] M004 [P] [MCP] Validate Neon Serverless PostgreSQL connection patterns

  **Reference**: Constitution VII - MCP Context-First Development, plan.md:589

  **Location**: MCP Context Server

  **Description**:
  Fetch and validate Neon PostgreSQL documentation via MCP:
  - Serverless connection strings
  - Connection pooling for serverless
  - Asyncpg driver configuration
  - Cold start mitigation strategies

  **Acceptance Criteria**:
  - [ ] MCP docs fetched successfully
  - [ ] Connection string format verified
  - [ ] Connection pooling approach documented
  - [ ] Serverless best practices confirmed

---

- [ ] M005 [P] [MCP] Validate Better Auth integration (Python + React)

  **Reference**: Constitution VII - MCP Context-First Development, plan.md:590

  **Location**: MCP Context Server

  **Description**:
  Fetch and validate Better Auth documentation via MCP:
  - Python client installation and configuration
  - React client installation and configuration
  - Email/password authentication setup
  - Session management and middleware patterns

  **Acceptance Criteria**:
  - [ ] MCP docs fetched successfully
  - [ ] Python client integration verified
  - [ ] React client integration verified
  - [ ] Session middleware patterns documented

---

## Phase 2: Database & ORM

**Purpose**: Define SQLModel entities and database connection

---

- [ ] D001 [Database] Create database connection module

  **Reference**: plan.md - Database Schema Strategy section

  **Location**: `backend/src/db/connection.py`

  **Description**:
  Create async database connection to Neon PostgreSQL:
  - `get_engine()` function returning async engine
  - Environment-based connection string
  - Connection pool settings for serverless

  **Acceptance Criteria**:
  - [ ] Engine connects to Neon PostgreSQL
  - [ ] Connection can be established from environment
  - [ ] Async support works

---

- [ ] D002 [Database] Create SQLModel User entity

  **Reference**: plan.md - Database Schema Strategy, spec.md - Key Entities (User)

  **Location**: `backend/src/models/user.py`

  **Description**:
  Define User SQLModel with:
  - `id`: UUID, primary key
  - `email`: VARCHAR(255), unique, NOT NULL
  - `password_hash`: VARCHAR(255), NOT NULL
  - `created_at`: TIMESTAMP, NOT NULL
  - `updated_at`: TIMESTAMP, NOT NULL
  - `deleted_at`: TIMESTAMP, NULL (for soft delete)

  **Acceptance Criteria**:
  - [ ] User model defined with SQLModel
  - [ ] All fields match schema
  - [ ] Unique constraint on email
  - [ ] Soft delete field present

---

- [ ] D003 [Database] Create SQLModel Todo entity

  **Reference**: plan.md - Database Schema Strategy, spec.md - Key Entities (Todo)

  **Location**: `backend/src/models/todo.py`

  **Description**:
  Define Todo SQLModel with:
  - `id`: UUID, primary key
  - `user_id`: UUID, foreign key to user.id, NOT NULL
  - `title`: VARCHAR(255), NOT NULL
  - `description`: TEXT, NULL
  - `is_completed`: BOOLEAN, NOT NULL, default false
  - `created_at`: TIMESTAMP, NOT NULL
  - `updated_at`: TIMESTAMP, NOT NULL

  **Acceptance Criteria**:
  - [ ] Todo model defined with SQLModel
  - [ ] All fields match schema
  - [ ] Foreign key to User
  - [ ] Default value for is_completed

---

- [ ] D004 [Database] Create database session management

  **Reference**: plan.md - Backend Architecture Decisions

  **Location**: `backend/src/db/session.py`

  **Description**:
  Create session dependency for FastAPI:
  - `get_db()` async generator
  - SessionLocal for SQLModel
  - Proper cleanup on request end

  **Acceptance Criteria**:
  - [ ] Session can be injected in routes
  - [ ] Sessions are properly closed
  - [ ] Works with async/await

---

- [ ] D005 [Database] Create Alembic migration configuration

  **Reference**: plan.md - Technical Context (Alembic migrations)

  **Location**: `backend/alembic/`, `backend/alembic.ini`

  **Description**:
  Set up Alembic for migrations:
  - `alembic.ini` configuration
  - `env.py` for SQLModel auto-generation
  - `script.py.mako` template
  - Initial migration

  **Acceptance Criteria**:
  - [ ] `alembic revision --autogenerate` works
  - [ ] `alembic upgrade head` applies migrations
  - [ ] Initial migration creates user and todo tables

---

## Phase 3: Authentication

**Purpose**: Integrate Better Auth on backend and frontend

---

- [ ] A001 [Auth] Configure Better Auth Python client on backend

  **Reference**: plan.md - Authentication Flow, spec.md - FR-001 to FR-008

  **Location**: `backend/src/auth.py` (or Better Auth config location)

  **Description**:
  Configure Better Auth for FastAPI:
  - Initialize Better Auth with email/password plugin
  - Configure session settings (24h sliding expiration)
  - Set up cookie-based sessions
  - Configure CSRF protection

  **Acceptance Criteria**:
  - [ ] Better Auth initializes without errors
  - [ ] Email/password authentication configured
  - [ ] Session expiration set to 24h sliding
  - [ ] HTTP-only cookies configured

---

- [ ] A002 [Auth] Create auth middleware for protected routes

  **Reference**: plan.md - Authenticated Request Lifecycle, spec.md - FR-009

  **Location**: `backend/src/api/auth.py` or middleware file

  **Description**:
  Create auth protection middleware/dependency:
  - Extract session from cookies
  - Return 401 for unauthenticated requests
  - Inject session into request context

  **Acceptance Criteria**:
  - [ ] Unauthenticated requests to protected routes return 401
  - [ ] Authenticated requests have session available
  - [ ] Invalid sessions are rejected

---

- [ ] A003 [Auth] Integrate Better Auth React client on frontend

  **Reference**: plan.md - Authentication Flow

  **Location**: `frontend/lib/auth.ts` or `frontend/providers/auth-provider.tsx`

  **Description**:
  Set up Better Auth client on Next.js:
  - Configure auth client with API URL
  - Create auth provider wrapper
  - Set up session hook (useSession equivalent)

  **Acceptance Criteria**:
  - [ ] Auth client initializes
  - [ ] Session can be fetched
  - [ ] Provider wraps app correctly

---

- [ ] A004 [Auth] Create frontend authentication hooks

  **Reference**: plan.md - Frontend Architecture (useAuth hook)

  **Location**: `frontend/hooks/useAuth.ts`

  **Description**:
  Create custom React hooks for auth:
  - `useAuth()` - returns session state
  - `useSignUp()` - signup function
  - `useSignIn()` - signin function
  - `useSignOut()` - signout function

  **Acceptance Criteria**:
  - [ ] Hooks return expected types
  - [ ] Hooks integrate with Better Auth client
  - [ ] Loading and error states work

---

- [ ] A005 [Auth] Test authentication flow

  **Reference**: spec.md - User Story 1 (Authentication)

  **Location**: `backend/tests/integration/test_auth.py`

  **Description**:
  Write integration tests for auth:
  - Test user signup creates account
  - Test sign in with valid credentials
  - Test sign in with invalid credentials
  - Test protected route without auth returns 401
  - Test sign out clears session

  **Acceptance Criteria**:
  - [ ] All auth tests pass
  - [ ] Tests verify user isolation
  - [ ] Tests verify error handling

---

## Phase 4: API Endpoints

**Purpose**: Build REST API endpoints for todo CRUD operations

---

- [ ] E001 [API] Create Pydantic schemas for todo requests/responses

  **Reference**: plan.md - API Request/Response Contracts, spec.md - FR-010 to FR-017

  **Location**: `backend/src/schemas/todo.py`

  **Description**:
  Define Pydantic schemas:
  - `TodoCreate` - title (required), description (optional)
  - `TodoUpdate` - title (optional), description (optional), is_completed (optional)
  - `TodoResponse` - id, title, description, is_completed, created_at, updated_at
  - `TodoListResponse` - todos array, total, page

  **Acceptance Criteria**:
  - [ ] All schemas defined
  - [ ] Validation works for requests
  - [ ] Response schemas match API contract

---

- [ ] E002 [API] Create todo service layer with user isolation

  **Reference**: plan.md - Service Layer Pattern, spec.md - FR-011, FR-018

  **Location**: `backend/src/services/todo_service.py`

  **Description**:
  Implement todo business logic:
  - `create_todo(user_id, data)` - creates todo for user
  - `get_todos(user_id, page, limit)` - lists todos with pagination
  - `get_todo(user_id, todo_id)` - gets single todo (must belong to user)
  - `update_todo(user_id, todo_id, data)` - updates todo (must belong to user)
  - `delete_todo(user_id, todo_id)` - deletes todo (must belong to user)

  **Acceptance Criteria**:
  - [ ] All CRUD operations implemented
  - [ ] User isolation enforced (query filters by user_id)
  - [ ] Pagination works (limit 20, offset calculated)
  - [ ] Returns 404 for not found or wrong owner

---

- [ ] E003 [API] Implement GET /api/v1/todos endpoint

  **Reference**: plan.md - Todo Endpoints, spec.md - FR-009

  **Location**: `backend/src/api/todos.py`

  **Description**:
  Create list todos endpoint:
  - `GET /api/v1/todos?page=1&limit=20`
  - Requires authentication
  - Returns paginated list of user's todos
  - Sorts by created_at DESC (newest first)

  **Acceptance Criteria**:
  - [ ] Endpoint returns 401 without auth
  - [ ] Returns user's todos only (user isolation)
  - [ ] Pagination works (page 1 returns first 20)
  - [ ] Response matches TodoListResponse schema

---

- [ ] E004 [API] Implement POST /api/v1/todos endpoint

  **Reference**: plan.md - Todo Endpoints, spec.md - FR-010

  **Location**: `backend/src/api/todos.py`

  **Description**:
  Create todo endpoint:
  - `POST /api/v1/todos`
  - Requires authentication
  - Body: {title, description?}
  - Returns created todo

  **Acceptance Criteria**:
  - [ ] Endpoint returns 401 without auth
  - [ ] Validates title required (max 255 chars)
  - [ ] Validates description max 1000 chars
  - [ ] Creates todo associated with authenticated user
  - [ ] Returns 201 Created

---

- [ ] E005 [API] Implement GET /api/v1/todos/{id} endpoint

  **Reference**: plan.md - Todo Endpoints, spec.md - FR-011

  **Location**: `backend/src/api/todos.py`

  **Description**:
  Get single todo endpoint:
  - `GET /api/v1/todos/{id}`
  - Requires authentication
  - Returns todo if owned by user

  **Acceptance Criteria**:
  - [ ] Endpoint returns 401 without auth
  - [ ] Returns 404 for non-existent todo
  - [ ] Returns 404 for todo owned by another user
  - [ ] Returns todo if owned by authenticated user

---

- [ ] E006 [API] Implement PUT /api/v1/todos/{id} endpoint

  **Reference**: plan.md - Todo Endpoints, spec.md - FR-014

  **Location**: `backend/src/api/todos.py`

  **Description**:
  Update todo endpoint:
  - `PUT /api/v1/todos/{id}`
  - Requires authentication
  - Body: {title?, description?, is_completed?}
  - Updates todo if owned by user

  **Acceptance Criteria**:
  - [ ] Endpoint returns 401 without auth
  - [ ] Returns 404 for non-existent todo
  - [ ] Returns 403/404 for todo owned by another user
  - [ ] Updates only provided fields (partial update)
  - [ ] Returns updated todo

---

- [ ] E007 [API] Implement DELETE /api/v1/todos/{id} endpoint

  **Reference**: plan.md - Todo Endpoints, spec.md - FR-016, FR-017

  **Location**: `backend/src/api/todos.py`

  **Description**:
  Delete todo endpoint:
  - `DELETE /api/v1/todos/{id}`
  - Requires authentication
  - Deletes todo if owned by user
  - Returns confirmation

  **Acceptance Criteria**:
  - [ ] Endpoint returns 401 without auth
  - [ ] Returns 404 for non-existent todo
  - [ ] Returns 403/404 for todo owned by another user
  - [ ] Todo is deleted from database
  - [ ] Returns success response

---

- [ ] E008 [API] Implement user soft delete endpoint

  **Reference**: spec.md - FR-020 (soft delete users, 30-day retention)

  **Location**: `backend/src/api/users.py`

  **Description**:
  Create user soft delete endpoint:
  - `DELETE /api/v1/users/me`
  - Requires authentication
  - Sets deleted_at timestamp on user (soft delete)
  - Does not immediately delete data
  - Returns confirmation

  **Acceptance Criteria**:
  - [ ] Endpoint returns 401 without auth
  - [ ] Sets deleted_at timestamp (does not hard delete)
  - [ ] User can no longer sign in after soft delete
  - [ ] Todos remain in database (for 30-day retention)
  - [ ] Returns success response

---

- [ ] E009 [API] Implement user data retention purge job

  **Reference**: spec.md - FR-020 (30-day retention before purging)

  **Location**: `backend/src/services/user_service.py`, `backend/scripts/purge_deleted_users.py`

  **Description**:
  Create scheduled job for purging soft-deleted users:
  - Query users where deleted_at < (now - 30 days)
  - Hard delete user and all associated todos
  - Log purge operations
  - Can be run as cron job or scheduled task

  **Acceptance Criteria**:
  - [ ] Script queries users with deleted_at older than 30 days
  - [ ] Deletes user and cascades to todos
  - [ ] Logs purge operations
  - [ ] Can be executed manually or via scheduler
  - [ ] Includes dry-run mode for testing

---

- [ ] E010 [API] Test all todo API endpoints

  **Reference**: spec.md - User Stories 2-4 (Create/List, Update, Delete)

  **Location**: `backend/tests/integration/test_todos.py`

  **Description**:
  Write integration tests for todo endpoints:
  - Test CRUD operations as authenticated user
  - Test user isolation (can't access other user's todos)
  - Test pagination
  - Test validation errors
  - Test not found errors

  **Acceptance Criteria**:
  - [ ] All CRUD tests pass
  - [ ] User isolation tests pass
  - [ ] Pagination tests pass
  - [ ] Error handling tests pass

---

## Phase 5: Frontend Pages & Components

**Purpose**: Build UI for authentication and todo management

---

- [ ] W001 [Frontend] Create TypeScript types for API responses

  **Reference**: plan.md - Frontend ↔ Backend Interaction

  **Location**: `frontend/types/todo.ts`, `frontend/types/user.ts`

  **Description**:
  Define TypeScript interfaces matching Pydantic schemas:
  - `Todo` type (id, title, description, is_completed, created_at, updated_at)
  - `User` type (id, email)
  - `TodoListResponse` type (todos, total, page)
  - `AuthResponse` type

  **Acceptance Criteria**:
  - [ ] Types match API response schemas
  - [ ] No `any` types used
  - [ ] Types can be imported in components

---

- [ ] W002 [Frontend] Create API client service

  **Reference**: plan.md - Service Layer Pattern (frontend/services/)

  **Location**: `frontend/services/api.ts`

  **Description**:
  Create base API client:
  - `fetchApi<T>()` function with credentials: 'include'
  - Error handling that throws readable errors
  - Base URL from environment variable

  **Acceptance Criteria**:
  - [ ] Sends cookies with requests
  - [ ] Environment variable for API URL
  - [ ] Error handling works
  - [ ] Returns typed responses

---

- [ ] W003 [Frontend] Create todo service

  **Reference**: plan.md - Service Layer Pattern

  **Location**: `frontend/services/todo.service.ts`

  **Description**:
  Create todo API functions:
  - `getTodos(page)` - calls GET /api/v1/todos
  - `createTodo(data)` - calls POST /api/v1/todos
  - `updateTodo(id, data)` - calls PUT /api/v1/todos/{id}
  - `deleteTodo(id)` - calls DELETE /api/v1/todos/{id}

  **Acceptance Criteria**:
  - [ ] All functions call correct endpoints
  - [ ] Functions return typed responses
  - [ ] Functions use API client

---

- [ ] W004 [Frontend] Create auth pages (signin/signup)

  **Reference**: spec.md - User Story 1 (Authentication)

  **Location**: `frontend/app/(public)/signin/page.tsx`, `frontend/app/(public)/signup/page.tsx`

  **Description**:
  Create authentication pages:
  - Sign up page with form (email, password)
  - Sign in page with form (email, password)
  - Forms submit to auth service
  - Handle errors and loading states
  - Redirect to dashboard on success

  **Acceptance Criteria**:
  - [ ] Pages render correctly
  - [ ] Forms submit and handle auth
  - [ ] Errors display to user
  - [ ] Redirect on success

---

- [ ] W005 [Frontend] Create auth components (forms)

  **Reference**: plan.md - Frontend Architecture (SignInForm, SignUpForm)

  **Location**: `frontend/components/auth/SignInForm.tsx`, `frontend/components/auth/SignUpForm.tsx`

  **Description**:
  Create reusable auth form components:
  - Email input with validation
  - Password input with masking
  - Submit button with loading state
  - Error message display

  **Acceptance Criteria**:
  - [ ] Components are reusable
  - [ ] Inputs have proper types
  - [ ] Loading states work
  - [ ] Error messages display

---

- [ ] W006 [Frontend] Create todo list component

  **Reference**: spec.md - User Story 2 (Create and List Todos)

  **Location**: `frontend/components/todo/TodoList.tsx`

  **Description**:
  Create todo list display:
  - Fetches todos from API
  - Displays each todo with title, description, status
  - Shows loading state
  - Shows empty state
  - Includes pagination controls

  **Acceptance Criteria**:
  - [ ] Fetches and displays todos
  - [ ] Shows loading skeleton
  - [ ] Shows empty state when no todos
  - [ ] Pagination works

---

- [ ] W007 [Frontend] Create todo item component

  **Reference**: spec.md - User Story 3 (Update and Complete Todos)

  **Location**: `frontend/components/todo/TodoItem.tsx`

  **Description**:
  Create individual todo item:
  - Displays todo title and description
  - Checkbox for complete/incomplete toggle
  - Edit button
  - Delete button
  - Visual distinction for completed todos

  **Acceptance Criteria**:
  - [ ] Displays all todo fields
  - [ ] Toggle updates status
  - [ ] Edit/delete buttons present
  - [ ] Visual feedback for completed

---

- [ ] W008 [Frontend] Create create todo form

  **Reference**: spec.md - User Story 2 (Create and List Todos)

  **Location**: `frontend/components/todo/CreateTodoForm.tsx`

  **Description**:
  Create todo creation form:
  - Title input (required)
  - Description textarea (optional)
  - Submit button
  - Clear form after success
  - Show success/error feedback

  **Acceptance Criteria**:
  - [ ] Form creates todo
  - [ ] Validation works
  - [ ] Clears on success
  - [ ] Shows feedback

---

- [ ] W009 [Frontend] Create update todo form/modal

  **Reference**: spec.md - User Story 3 (Update and Complete Todos)

  **Location**: `frontend/components/todo/UpdateTodoForm.tsx`

  **Description**:
  Create todo edit form/modal:
  - Pre-fills with existing todo data
  - Allows editing title, description, status
  - Submit updates to API
  - Shows confirmation dialog

  **Acceptance Criteria**:
  - [ ] Pre-fills existing data
  - [ ] Updates todo on submit
  - [ ] Handles validation
  - [ ] Shows confirmation

---

- [ ] W010 [Frontend] Create delete confirmation dialog

  **Reference**: spec.md - User Story 4 (Delete Todos), FR-017

  **Location**: `frontend/components/todo/DeleteTodoDialog.tsx`

  **Description**:
  Create delete confirmation:
  - Modal with confirmation message
  - Cancel and delete buttons
  - Deletes on confirmation
  - Shows loading state

  **Acceptance Criteria**:
  - [ ] Confirmation required before delete
  - [ ] Loading state during delete
  - [ ] Closes after delete
  - [ ] Shows feedback

---

- [ ] W011 [Frontend] Create authenticated layout and navigation

  **Reference**: plan.md - Frontend Architecture (layout.tsx)

  **Location**: `frontend/app/(auth)/layout.tsx`, `frontend/components/NavBar.tsx`

  **Description**:
  Create authenticated layout:
  - Navigation bar with app name
  - Sign out button
  - User info display
  - Responsive design

  **Acceptance Criteria**:
  - [ ] Nav bar displays on authenticated pages
  - [ ] Sign out works
  - [ ] Responsive on mobile

---

- [ ] W012 [Frontend] Create dashboard page

  **Reference**: spec.md - User Story 2 (Create and List Todos)

  **Location**: `frontend/app/(auth)/page.tsx`

  **Description**:
  Create main dashboard:
  - Displays todo list
  - Shows create todo form
  - Shows pagination
  - Protected route (redirect if not authenticated)

  **Acceptance Criteria**:
  - [ ] Redirects if not authenticated
  - [ ] Displays todo list
  - [ ] Create form present
  - [ ] Pagination works

---

- [ ] W013 [Frontend] Handle auth state and redirects

  **Reference**: spec.md - User Story 1 (Authentication), FR-009

  **Location**: `frontend/middleware.ts` or auth context

  **Description**:
  Implement auth state handling:
  - Redirect unauthenticated users to signin
  - Redirect authenticated users away from auth pages
  - Handle session expiry
  - Persist auth state

  **Acceptance Criteria**:
  - [ ] Unauth users redirected to signin
  - [ ] Auth users can access dashboard
  - [ ] Session expiry handled
  - [ ] No flash of protected content

---

## Phase 6: Integration & Validation

**Purpose**: Final testing, error handling, and polish

---

- [ ] I001 [Integration] Add form validation on frontend

  **Reference**: spec.md - FR-025 (input validation), FR-002 (email validation)

  **Location**: `frontend/components/` form files

  **Description**:
  Add client-side validation:
  - Email format validation
  - Password minimum 8 chars with mixed case + number
  - Title maximum 255 characters
  - Description maximum 1000 characters
  - Required field validation

  **Acceptance Criteria**:
  - [ ] Validation prevents invalid submissions
  - [ ] Helpful error messages display
  - [ ] Matches backend validation

---

- [ ] I002 [Integration] Handle network errors gracefully

  **Reference**: spec.md - Edge Cases (network disconnection)

  **Location**: `frontend/services/api.ts`, components

  **Description**:
  Implement error handling:
  - Network error detection
  - Retry UI for failed requests
  - User-friendly error messages
  - Session expiry handling (redirect to signin)

  **Acceptance Criteria**:
  - [ ] Network errors show retry option
  - [ ] Session expiry redirects to signin
  - [ ] Errors are readable
  - [ ] No sensitive data in errors

---

- [ ] I003 [Integration] Implement loading states and skeletons

  **Reference**: spec.md - SC-003 (2 second response)

  **Location**: `frontend/components/todo/TodoList.tsx`, other components

  **Description**:
  Add loading UI:
  - Loading skeletons for todo list
  - Loading spinners on buttons
  - Disable form during submission
  - Optimistic updates where appropriate

  **Acceptance Criteria**:
  - [ ] Loading state while fetching
  - [ ] Skeleton matches content
  - [ ] Buttons disabled during submit
  - [ ] Feedback during optimistic updates

---

- [ ] I004 [Integration] Add empty states and polish

  **Reference**: spec.md - SC-001 (2 minute signup)

  **Location**: `frontend/components/todo/TodoList.tsx`, dashboard

  **Description**:
  Create empty states:
  - "Add your first todo" prompt when list empty
  - Helpful empty state copy
  - Call to action to create todo

  **Acceptance Criteria**:
  - [ ] Empty state displays when no todos
  - [ ] Helpful text and CTA
  - [ ] Visually appealing

---

- [ ] I005 [Integration] Implement responsive design

  **Reference**: spec.md - SC-004 (mobile devices), User Story 5

  **Location**: `frontend/app/`, components, `globals.css`

  **Description**:
  Ensure mobile-friendly:
  - Responsive grid/flex layouts
  - Touch-friendly button sizes
  - Mobile navigation
  - No horizontal scroll

  **Acceptance Criteria**:
  - [ ] Works on mobile viewport
  - [ ] Touch targets >= 44px
  - [ ] No horizontal scroll
  - [ ] Layout adapts to screen size

---

- [ ] I006 [Integration] Write frontend component tests

  **Reference**: Constitution III - TDD

  **Location**: `frontend/tests/` ( Jest or Playwright)

  **Description**:
  Create frontend tests:
  - Component tests with React Testing Library
  - Auth form tests
  - Todo list tests
  - Integration tests for user flows

  **Acceptance Criteria**:
  - [ ] Component tests pass
  - [ ] Auth flow tests pass
  - [ ] Todo CRUD tests pass
  - [ ] No test failures

---

- [ ] I007 [Integration] Final integration testing

  **Reference**: spec.md - Success Criteria (all 8 criteria)

  **Location**: Manual testing + automated integration tests

  **Description**:
  Run full integration tests:
  - End-to-end user flows
  - Cross-user data isolation verification
  - Performance testing (response times)
  - Security testing (auth bypass attempts)

  **Acceptance Criteria**:
  - [ ] All user stories work end-to-end
  - [ ] User isolation verified (can't see other's todos)
  - [ ] Response times < 2 seconds
  - [ ] No security vulnerabilities found

---

## Phase 7: Deployment & CI/CD

**Purpose**: Configure automated deployment pipelines for frontend and backend

---

- [ ] D001 [Deployment] Create health check endpoint for backend

  **Reference**: spec.md - FR-029 (health check endpoint), Constitution X

  **Location**: `backend/src/api/health.py`, `backend/src/main.py`

  **Description**:
  Create health check endpoint:
  - Define `GET /health` endpoint
  - Return `{"status": "healthy", "service": "todo-api"}`
  - Include in FastAPI app routes
  - Optionally check database connection

  **Acceptance Criteria**:
  - [ ] Endpoint returns 200 OK
  - [ ] Response includes status and service name
  - [ ] Endpoint registered in main.py
  - [ ] Can be accessed at /health

---

- [ ] D002 [Deployment] Create GitHub Actions workflow for frontend

  **Reference**: spec.md - FR-027, FR-030, plan.md - Deployment Architecture

  **Location**: `.github/workflows/deploy-frontend.yml`

  **Description**:
  Create GitHub Actions CI/CD workflow:
  - Trigger on push to main and pull requests
  - Checkout code
  - Setup Node.js 18
  - Install dependencies (npm ci)
  - Run tests (npm test)
  - Build Next.js app (npm run build)
  - Deploy to Vercel on merge to main

  **Acceptance Criteria**:
  - [ ] Workflow file created
  - [ ] Tests run before deployment
  - [ ] Build succeeds
  - [ ] Deployment only on main branch
  - [ ] Uses GitHub Secrets for credentials

---

- [ ] D003 [Deployment] Configure Railway deployment for backend

  **Reference**: spec.md - FR-028, plan.md - Railway Configuration

  **Location**: `backend/railway.json` or `backend/Procfile`

  **Description**:
  Create Railway deployment configuration:
  - Define build command (pip install requirements)
  - Define start command (alembic upgrade + uvicorn)
  - Configure health check path (/health)
  - Set restart policy (ON_FAILURE)
  - Connect to GitHub repository

  **Acceptance Criteria**:
  - [ ] railway.json or Procfile created
  - [ ] Build command specified
  - [ ] Start command includes migrations
  - [ ] Health check path configured
  - [ ] Railway project linked to GitHub repo

---

- [ ] D004 [Deployment] Configure environment variables for production

  **Reference**: spec.md - FR-031, plan.md - Environment Variables Management

  **Location**: GitHub Secrets, Railway dashboard, documentation

  **Description**:
  Set up production environment variables:
  - Add GitHub Secrets for frontend (VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID, NEXT_PUBLIC_API_URL)
  - Add Railway environment variables (DATABASE_URL, BETTER_AUTH_SECRET, BETTER_AUTH_URL, FRONTEND_URL)
  - Update .env.example files with production variables
  - Document all required environment variables

  **Acceptance Criteria**:
  - [ ] All GitHub Secrets configured
  - [ ] All Railway variables configured
  - [ ] No secrets in code or version control
  - [ ] .env.example updated with deployment vars
  - [ ] Documentation includes all required variables

---

- [ ] D005 [Deployment] Test deployment pipeline end-to-end

  **Reference**: spec.md - SC-007, SC-008, SC-009

  **Location**: Deployed applications

  **Description**:
  Test full deployment process:
  - Push to main branch
  - Verify GitHub Actions runs and passes tests
  - Verify frontend deploys to Vercel
  - Verify backend deploys to Railway
  - Test health check endpoint
  - Verify frontend can communicate with backend
  - Test user flows on production

  **Acceptance Criteria**:
  - [ ] GitHub Actions workflow completes successfully
  - [ ] Frontend deployed and accessible
  - [ ] Backend deployed and accessible
  - [ ] Health check returns 200 OK
  - [ ] Production CORS configured correctly
  - [ ] All user stories work in production

---

- [ ] D006 [Deployment] Document deployment and rollback procedures

  **Reference**: spec.md - FR-032, plan.md - Phase 6 Deliverables

  **Location**: `README.md`, `docs/deployment.md`

  **Description**:
  Create deployment documentation:
  - Deployment process overview
  - Required GitHub Secrets and Railway variables
  - How to trigger manual deployment
  - Rollback procedure (redeploy previous commit)
  - Troubleshooting common deployment issues
  - Monitoring and health checks

  **Acceptance Criteria**:
  - [ ] Deployment process documented
  - [ ] Environment variables documented
  - [ ] Rollback procedure documented
  - [ ] Troubleshooting guide included
  - [ ] Links to Railway and Vercel dashboards

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Scaffolding)**: No dependencies - can start immediately
  - Phase 1.1 (Backend setup): B001-B005
  - Phase 1.2 (Frontend setup): F001-F004
  - Phase 1.3 (MCP validation): M001-M005 (MUST complete before Phase 2+)
- **Phase 2 (Database)**: Depends on Phase 1 (backend setup + MCP validation)
- **Phase 3 (Authentication)**: Depends on Phase 2 (database) and Phase 1 (backend + MCP)
- **Phase 4 (API)**: Depends on Phase 3 (authentication) and Phase 2 (database)
- **Phase 5 (Frontend)**: Depends on Phase 4 (API endpoints)
- **Phase 6 (Integration)**: Depends on Phase 5 (frontend components)
- **Phase 7 (Deployment)**: Depends on Phase 6 (all integration tests passing)

### Within Each Phase

- Tasks marked [P] can run in parallel
- Non-[P] tasks depend on previous tasks in that phase
- Backend tasks should complete before frontend tasks that depend on them
- MCP validation tasks (M001-M005) MUST complete before implementation phases

### Parallel Opportunities

- B001-B005 (Backend setup) can run in parallel
- F001-F004 (Frontend setup) can run in parallel
- M001-M005 (MCP validation) can run in parallel
- All frontend component tasks (W001-W013) can run in parallel once types/services are done
- All integration tasks (I001-I007) can run in parallel
- D001, D002, D003, D004 (Deployment config) can run in parallel
- D005, D006 (Deployment testing and docs) must run sequentially after D001-D004

---

## Implementation Strategy

### MVP First (Core Auth + CRUD)

1. Complete Phase 1.1 + 1.2: Project scaffolding (backend + frontend)
2. Complete Phase 1.3: **MCP validation (MANDATORY before proceeding)**
3. Complete Phase 2: Database setup
4. Complete Phase 3: Authentication
5. Complete Phase 4: API endpoints (including user soft delete)
6. **STOP and VALIDATE**: Test core CRUD with API client
7. Complete Phase 5: Frontend UI
8. Complete Phase 6: Integration and validation
9. Complete Phase 7: **Deployment and CI/CD (production-ready)**

### Incremental Delivery

1. Complete Phase 1 (scaffolding + MCP validation) → Project structure ready
2. Complete Phase 2 + 3 + 4 → Core API ready
3. Add Phase 5 → Full frontend UI
4. Add Phase 6 → Polish and validation
5. Add Phase 7 → Automated deployment to production
6. Each phase adds value without breaking previous work

### Parallel Team Strategy

With multiple developers:
- Developer A: Backend tasks (B001-B005, D001-D005, A001-A005, E001-E010)
- Developer B: Frontend tasks (F001-F004, W001-W013)
- Developer C: MCP validation and testing (M001-M005, I001-I007)
- DevOps/Developer D: Deployment tasks (D001-D006)

---

## Notes

- **[P]** tasks = parallelizable (different files, no dependencies)
- All tasks must pass acceptance criteria before moving on
- Commit after each task or logical group
- Create PHR after each phase completion
- Stop at any checkpoint to validate independently
- Avoid vague tasks, same file conflicts, cross-task dependencies that break independence

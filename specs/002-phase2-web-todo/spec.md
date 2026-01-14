# Feature Specification: Phase 2 - Todo Web Application

**Feature Branch**: `002-phase2-web-todo`
**Created**: 2026-01-13
**Status**: Draft
**Input**: Transform the existing console application into a modern, production-ready, multi-user web application with persistent storage. Implement all 5 Basic Level features of the original console app as a web-based, multi-user system.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Authentication (Priority: P1)

As a new user, I want to create an account with email and password so that I can access my personal todo list securely.

**Why this priority**: Authentication is the foundation of a multi-user system. Without it, users cannot access any features, and data isolation cannot be enforced. This is the absolute first requirement before any other functionality.

**Independent Test**: Can be fully tested by creating a new account, verifying email format, and successfully signing in to access an authenticated dashboard. Delivers secure access to a personal workspace.

**Acceptance Scenarios**:

1. **Given** a new user visits the signup page, **When** they enter a valid email and password, **Then** the system creates their account and redirects them to the authenticated dashboard.

2. **Given** a registered user visits the signin page, **When** they enter correct credentials, **Then** the system authenticates them and provides access to their todos.

3. **Given** an unauthenticated user, **When** they try to access any protected page, **Then** the system redirects them to the signin page.

4. **Given** a user with invalid credentials, **When** they attempt to sign in, **Then** the system displays an appropriate error message without revealing whether the email exists.

---

### User Story 2 - Create and List Todos (Priority: P1)

As an authenticated user, I want to create new todos and view my existing todos so that I can track my tasks in one place.

**Why this priority**: Creating and viewing todos are the core operations of the application. Without these, there is no todo management functionality. This delivers immediate value to users.

**Independent Test**: Can be fully tested by signing in, creating a new todo with title and description, and immediately seeing it appear in the todo list. Delivers task tracking capability.

**Acceptance Scenarios**:

1. **Given** an authenticated user on the dashboard, **When** they create a new todo with a title, **Then** the todo is saved and associated with their account.

2. **Given** an authenticated user with existing todos, **When** they view the dashboard, **Then** they see all their todos displayed with title, description, and completion status.

3. **Given** an authenticated user with no todos, **When** they view the dashboard, **Then** they see a prompt to add their first todo.

4. **Given** an authenticated user, **When** they view another user's todos, **Then** the system returns an empty list or shows only their own todos (user isolation enforced).

---

### User Story 3 - Update and Complete Todos (Priority: P1)

As an authenticated user, I want to update my todo details and mark todos as complete so that I can keep my task list accurate and track progress.

**Why this priority**: Updating and completing todos are essential for task management workflow. Users need to modify details and mark progress to effectively manage their work.

**Independent Test**: Can be fully tested by editing a todo's title/description and marking it as complete, then verifying the changes persist and the status updates correctly.

**Acceptance Scenarios**:

1. **Given** an authenticated user viewing their todos, **When** they edit a todo's title or description, **Then** the changes are saved and reflected in the todo list.

2. **Given** an authenticated user viewing their todos, **When** they mark a todo as complete, **Then** the todo's status changes to complete and is visually distinguished.

3. **Given** an authenticated user viewing their todos, **When** they mark a complete todo as incomplete, **Then** the todo's status changes back to pending.

4. **Given** an authenticated user, **When** they try to update another user's todo, **Then** the system denies the operation and returns an error.

---

### User Story 4 - Delete Todos (Priority: P2)

As an authenticated user, I want to delete todos that are no longer needed so that I can keep my task list clean and focused.

**Why this priority**: Deletion is a standard CRUD operation that users expect. While not as critical as create/read/update, it completes the todo management experience.

**Independent Test**: Can be fully tested by deleting a todo and verifying it no longer appears in the todo list.

**Acceptance Scenarios**:

1. **Given** an authenticated user viewing their todos, **When** they confirm deletion of a todo, **Then** the todo is permanently removed from their list.

2. **Given** an authenticated user, **When** they try to delete another user's todo, **Then** the system denies the operation and returns an error.

3. **Given** an authenticated user, **When** they attempt to delete without confirmation, **Then** the todo is preserved (no accidental deletions).

---

### User Story 5 - Responsive Web Interface (Priority: P2)

As a user accessing the application from any device, I want a responsive interface that works on desktop and mobile so that I can manage my todos conveniently.

**Why this priority**: Mobile access extends the application's utility beyond desktop. Users increasingly expect to access web applications from phones and tablets.

**Independent Test**: Can be tested by accessing the application from different screen sizes and verifying layout adapts appropriately for each device type.

**Acceptance Scenarios**:

1. **Given** a user on a desktop browser, **When** they access the application, **Then** the interface uses the full screen width with a comfortable layout.

2. **Given** a user on a mobile browser, **When** they access the application, **Then** the interface adapts to fit the smaller screen with touch-friendly controls.

3. **Given** a user on any device, **When** they rotate the screen, **Then** the layout adjusts appropriately without breaking.

---

### Edge Cases (Addressed)

- **Duplicate email signup**: System rejects with "email already registered" message
- **Invalid email format**: System validates and shows helpful error message
- **Network disconnection**: System shows error and allows retry when reconnected
- **Many todos**: Pagination at 20 items per page handles large lists
- **Session expiration**: System redirects to sign-in page when session expires

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to create accounts with email and password
- **FR-002**: System MUST validate email format during signup
- **FR-003**: System MUST enforce minimum password strength (8+ chars, mixed case + number)
- **FR-004**: System MUST normalize emails to lowercase (case-insensitive uniqueness)
- **FR-005**: System MUST allow registered users to sign in with their credentials
- **FR-006**: System MUST handle authentication errors without revealing whether email exists
- **FR-007**: System MUST implement sliding session expiration (24 hours of inactivity)
- **FR-008**: System MUST allow multiple concurrent sessions per user
- **FR-009**: System MUST require authentication for all todo operations
- **FR-010**: System MUST create new todos with title and optional description
- **FR-011**: System MUST associate all todos with the authenticated user
- **FR-012**: System MUST paginate todo lists at 20 items per page
- **FR-013**: System MUST sort todos by created date (newest first)
- **FR-014**: System MUST allow users to update todo title and description
- **FR-015**: System MUST allow users to mark todos as complete or incomplete
- **FR-016**: System MUST allow users to delete their own todos
- **FR-017**: System MUST require confirmation before todo deletion
- **FR-018**: System MUST enforce user isolation - users can only access their own todos
- **FR-019**: System MUST NOT allow todo sharing or collaboration (Phase 2)
- **FR-020**: System MUST soft-delete users and retain data for 30 days before purging
- **FR-021**: System MUST not require email confirmation before sign-in (Phase 2)
- **FR-022**: System MUST persist all data to the database
- **FR-023**: System MUST provide a responsive web interface for all screen sizes
- **FR-024**: System MUST communicate between frontend and backend via REST APIs only
- **FR-025**: System MUST validate all API inputs with appropriate error responses
- **FR-026**: System MUST store no hard-coded secrets and use environment-based configuration
- **FR-027**: System MUST deploy frontend automatically via GitHub Actions to Vercel (or static host)
- **FR-028**: System MUST deploy backend automatically via Railway with GitHub integration
- **FR-029**: System MUST expose a health check endpoint at `/health` for backend monitoring
- **FR-030**: System MUST run all tests in CI pipeline before deployment
- **FR-031**: System MUST manage secrets via GitHub Secrets (frontend) and Railway dashboard (backend)
- **FR-032**: System MUST support rollback to previous deployment via Git history

### Key Entities

- **User**: Represents an authenticated user account with unique email (case-insensitive), hashed password, deleted_at timestamp (for soft delete), and timestamps
- **Todo**: Represents a task owned by a user with title (max 255 chars), description (max 1000 chars), completion status, and timestamps
- **Session**: Represents an authenticated session for maintaining user login state with last_activity tracking for sliding expiration

### Clarified Policies

- **Email Policy**: Case-insensitive (normalized to lowercase), unique per user
- **Password Policy**: Minimum 8 characters, requires uppercase, lowercase, and number
- **Session Policy**: Sliding 24-hour expiration, multiple concurrent sessions allowed
- **Pagination**: 20 items per page, sorted by created date (newest first)
- **Account Deletion**: Soft delete with 30-day retention period before data purging
- **Email Confirmation**: Not required in Phase 2 (immediate sign-in after signup)
- **Todo Sharing**: Not supported in Phase 2 (private todos only)
- **Deployment Policy**: Automated CI/CD via GitHub Actions (frontend) and Railway (backend), tests must pass before deployment, rollback via Git history

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: New users can create an account and sign in within 2 minutes of landing on the application
- **SC-002**: Authenticated users can create, view, update, and delete their todos with no more than 3 clicks
- **SC-003**: Todo operations (create, read, update, delete) complete within 2 seconds each
- **SC-004**: Users can access the application on mobile devices with a functional, responsive layout
- **SC-005**: User data is isolated - users only see and modify their own todos
- **SC-006**: All data persists across browser sessions and device changes
- **SC-007**: Frontend deploys automatically to Vercel (or static host) via GitHub Actions on merge to main
- **SC-008**: Backend deploys automatically to Railway on merge to main with zero-downtime
- **SC-009**: Health check endpoint responds with 200 OK when backend is healthy
- **SC-010**: Failed tests prevent deployment (CI pipeline blocks merge)

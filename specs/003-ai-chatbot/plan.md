# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `003-ai-chatbot` | **Date**: 2026-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-ai-chatbot/spec.md`

## Summary

Build an AI-powered chatbot interface that enables authenticated users to manage their todo tasks through natural language conversation. The chatbot uses OpenAI Agents SDK with MCP (Model Context Protocol) tools for all task operations, maintaining a stateless backend architecture with conversation history persisted in Neon PostgreSQL. Users interact via OpenAI ChatKit UI, which communicates with a FastAPI backend that orchestrates agent execution and MCP tool calls.

**Core Architecture**: ChatKit UI → FastAPI `/api/{user_id}/chat` → OpenAI Agent + Runner → MCP Server (5 tools) → Neon PostgreSQL via SQLModel

## Technical Context

**Language/Version**: Python 3.13+
**Model**: Google Gemini 2.5 Flash (via OpenAI Agents SDK / OpenAI-compatible endpoint)
**Primary Dependencies**:
- OpenAI Agents SDK (Python) v0.2.9+ - Agent orchestration and tool execution
- MCP Python SDK (modelcontextprotocol/python-sdk) - MCP server and tool definitions
- FastAPI 0.115+ - Async REST API backend
- SQLModel - Database ORM for conversation and message models
- Neon Serverless PostgreSQL - Database (existing from Phase II)
- Better Auth - Authentication (existing from Phase II)
- OpenAI ChatKit UI - Frontend chat interface
- Next.js 16+ - Frontend framework (existing from Phase II)

**Storage**: Neon Serverless PostgreSQL (existing + new tables: conversations, messages)
**Testing**: pytest (backend), Jest/Playwright (frontend), MCP tool contract tests
**Target Platform**: Railway (Backend), Vercel (Frontend)
**Project Type**: Web application (frontend + backend + MCP server)
**Performance Goals**:
- Chat response < 3 seconds (SC-002)
- Task operations < 10 seconds (SC-001)
- Agent context window: last 100 messages per conversation

**Constraints**:
- Stateless backend (no in-memory conversation state)
- MCP-first architecture (agent MUST use tools, never direct DB access)
- Single task-oriented agent (no multi-agent orchestration)
- Case-insensitive substring matching for task references
- Manual retry only (no auto-retry on failures)

**Scale/Scope**: Multi-user web application, one persistent conversation per user, Phase III scope only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase III Constitutional Compliance

**✅ I. Spec-Driven Development (SDD) Mandate**
- Specification complete and clarified (spec.md + clarifications.md)
- MCP Context validation completed via Context7 MCP server
- Planning follows constitution workflow
- **Status**: PASS

**✅ II. Phase-Scoped Development**
- In scope: AI chatbot, OpenAI Agents SDK, MCP server, ChatKit UI, stateless architecture
- Out of scope explicitly defined: No direct DB access from agent, no in-memory state, no multi-agent
- **Status**: PASS

**✅ III. Test-First Development (TDD)**
- Plan includes test requirements for MCP tools, agent workflows, conversation state
- Tests will be written before implementation (tasks.md will enforce Red-Green-Refactor)
- **Status**: PASS (deferred to tasks phase)

**✅ IV. Minimal Viable Simplicity**
- Single agent architecture (no orchestration)
- Simple task matching (case-insensitive substring, no fuzzy)
- Simple error handling (manual retry, no auto-retry)
- Full input as task title (no complex NLP parsing)
- **Status**: PASS

**✅ V. Persistent Database Architecture**
- Neon PostgreSQL for todos (existing) + conversations + messages (new)
- SQLModel ORM for type safety
- **Status**: PASS

**✅ VI. Separation of Concerns**
- Clear layers: Frontend (ChatKit UI) → Backend API → Agent → MCP Server → Database
- Agent in `backend/agent/`, MCP in `backend/mcp/`, API in `backend/api/`
- **Status**: PASS

**✅ VII. MCP Context-First Development (CRITICAL)**
- MCP context validated via Context7 for OpenAI Agents SDK, MCP SDK, FastAPI
- Official documentation patterns incorporated into plan
- **Status**: PASS

**✅ VIII. RESTful API Design**
- POST /api/{user_id}/chat endpoint for chatbot
- Pydantic request/response models
- Existing Phase II endpoints preserved
- **Status**: PASS

**✅ IX. Auth-Aware Architecture**
- Better Auth integration (existing from Phase II)
- User isolation enforced for conversations and tasks
- **Status**: PASS

**✅ X. Automated Deployment via CI/CD**
- Frontend: GitHub Actions → Vercel (existing)
- Backend: Railway (existing)
- **Status**: PASS

**✅ XI. MCP-First Tool Execution (Hard Rule - NEW in Phase III)**
- Agent uses MCP tools exclusively for task CRUD
- 5 tools defined: add_task, list_tasks, complete_task, delete_task, update_task
- MCP tools delegate to backend services
- No direct database access from agent
- **Status**: PASS

**✅ XII. Agentic AI Behavioral Constitution (NEW in Phase III)**
- Agent asks clarifying questions when ambiguous
- Agent fetches task data before explaining
- Agent provides human-friendly responses
- Error handling: polite messages, no technical jargon
- **Status**: PASS

**✅ XIII. Stateless Conversation Architecture (NEW in Phase III)**
- No in-memory conversation state between requests
- Conversation history loaded from database (last 100 messages)
- Updated history saved before returning response
- One persistent conversation per user
- **Status**: PASS

**Overall Gate Status**: ✅ **PASS** - All 13 constitutional principles satisfied

## System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  Next.js 16 + OpenAI ChatKit UI + Better Auth Client       │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS POST /api/{user_id}/chat
                           │ { message: str, conversation_id?: str }
┌──────────────────────────▼──────────────────────────────────┐
│                      FastAPI Backend Layer                    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  POST /api/{user_id}/chat Endpoint                  │   │
│  │  - Validate auth (Better Auth middleware)           │   │
│  │  - Load conversation history (last 100 messages)    │   │
│  │  - Persist user message                             │   │
│  │  - Execute agent workflow ──────────┐               │   │
│  │  - Persist assistant response       │               │   │
│  │  - Return response                  │               │   │
│  └────────────────────────────────────┼────────────────┘   │
│                                        │                     │
│  ┌─────────────────────────────────────▼───────────────┐   │
│  │          OpenAI Agents SDK Layer                    │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │  Agent (single task-oriented agent)          │   │   │
│  │  │  - Instructions: "You help manage todos..."  │   │   │
│  │  │  - Tools: [5 MCP tools]                      │   │   │
│  │  │  - Conversation history: last 100 messages   │   │   │
│  │  └──────────────────┬───────────────────────────┘   │   │
│  │                     │ Runner.run(agent, input,      │   │
│  │                     │              conversation)    │   │
│  │  ┌──────────────────▼───────────────────────────┐   │   │
│  │  │  Runner                                       │   │   │
│  │  │  - Execute agent with conversation context   │   │   │
│  │  │  - Invoke MCP tools as needed                │   │   │
│  │  │  - Return result with tool call logs         │   │   │
│  │  └──────────────────┬───────────────────────────┘   │   │
│  └────────────────────┼──────────────────────────────┘   │
│                       │ Tool invocations                  │
│  ┌────────────────────▼──────────────────────────────┐   │
│  │           MCP Server Layer                        │   │
│  │  (FastMCP with 5 registered tools)                │   │
│  │                                                    │   │
│  │  Tools (all stateless, user_id context):          │   │
│  │  - add_task(user_id, title) → TaskResult          │   │
│  │  - list_tasks(user_id, filter?) → List[Task]      │   │
│  │  - complete_task(user_id, task_ref) → TaskResult  │   │
│  │  - delete_task(user_id, task_ref) → TaskResult    │   │
│  │  - update_task(user_id, task_ref, new_title)      │   │
│  │                  → TaskResult                      │   │
│  │                                                    │   │
│  │  Each tool delegates to backend services ────┐    │   │
│  └──────────────────────────────────────────────┼────┘   │
│                                                  │         │
│  ┌──────────────────────────────────────────────▼────┐   │
│  │        Backend Services Layer                     │   │
│  │  - TaskService: CRUD operations via SQLModel     │   │
│  │  - ConversationService: Manage chat history      │   │
│  │  - Enforce user isolation                         │   │
│  │  - Case-insensitive substring matching           │   │
│  └──────────────────────┬────────────────────────────┘   │
└────────────────────────┼──────────────────────────────────┘
                         │ SQLModel queries
┌────────────────────────▼──────────────────────────────────┐
│              Neon Serverless PostgreSQL                    │
│                                                             │
│  Existing Tables:        New Tables:                       │
│  - users                 - conversations                   │
│  - todos                 - messages                        │
│                                                             │
│  User Isolation: Foreign keys + user_id filtering         │
└─────────────────────────────────────────────────────────────┘
```

### Request Lifecycle (Stateless Architecture)

```
1. User types message in ChatKit UI
   ↓
2. Frontend sends POST /api/{user_id}/chat
   {
     "message": "add a task to buy groceries",
     "conversation_id": "conv_123" (optional, created if absent)
   }
   ↓
3. FastAPI Backend:
   a. Validate auth (Better Auth middleware)
   b. Validate user_id matches authenticated user
   c. Load or create conversation for user (one persistent conversation)
   d. Query last 100 messages from database (ORDER BY timestamp DESC LIMIT 100)
   e. Persist user message to messages table
   ↓
4. Agent Execution:
   a. Create Agent with instructions and MCP tools
   b. Convert last 100 messages to Agent conversation format
   c. Call Runner.run(agent, input=user_message, conversation=messages)
   d. Agent analyzes intent → selects MCP tool (add_task)
   e. MCP tool executes → calls TaskService.create(user_id, "buy groceries")
   f. TaskService creates todo in database with user_id
   g. MCP tool returns result to agent
   h. Agent formats natural language response
   ↓
5. Backend Response Processing:
   a. Extract agent's final_output
   b. Create assistant message with response + tool call metadata
   c. Persist assistant message to messages table
   d. Commit transaction
   ↓
6. Return to Frontend:
   {
     "response": "Task added: Buy groceries",
     "conversation_id": "conv_123",
     "tool_calls": [{"tool": "add_task", "status": "success"}]
   }
   ↓
7. ChatKit UI renders assistant response
   - User sees: "Task added: Buy groceries"
   - Loading state cleared
   - Chat history updated
```

**Statelessness Enforced**:
- No in-memory state between requests
- Agent instance created fresh per request
- Conversation loaded from DB on every request
- Updated conversation saved to DB before response
- Server can restart without data loss

### Agent Decision Logic

**Intent Detection → Tool Selection**:

| User Intent Pattern | Agent Selects Tool | Parameters |
|---------------------|-------------------|------------|
| "add task...", "create..." | `add_task` | title=extracted_text |
| "show tasks", "list..." | `list_tasks` | filter=none |
| "complete X", "mark X done" | Case-insensitive match → `complete_task` | task_ref=X |
| "delete X", "remove X" | Case-insensitive match → `delete_task` | task_ref=X |
| "update X to Y", "change X" | Case-insensitive match → `update_task` | task_ref=X, new_title=Y |
| "what is X for?", "explain X" | `list_tasks` then analyze | filter=X |

**Multi-Step Flows**:

1. **Ambiguous Reference** (User Story 3 - P3):
   - User: "complete my task" (user has 3 tasks)
   - Agent: Calls `list_tasks` first
   - Agent: Sees multiple results
   - Agent: Responds "Which task did you mean? 1) Buy milk 2) Buy groceries 3) Call dentist"
   - User clarifies → Agent calls `complete_task`

2. **Task Explanation** (User Story 2 - P2):
   - User: "why did I create the groceries task?"
   - Agent: Calls `list_tasks(filter="groceries")`
   - MCP tool: Returns task with title="Buy groceries" description="Need ingredients for dinner party"
   - Agent: Analyzes title + description
   - Agent: Responds "This task is for purchasing ingredients needed for your dinner party on Saturday"

3. **Partial Match Clarification**:
   - User: "complete buy" (tasks: "Buy milk", "Buy groceries")
   - Agent: Calls `list_tasks(filter="buy")`
   - MCP tool: Returns 2 matches (case-insensitive substring)
   - Agent: Asks "Which task? 1) Buy milk 2) Buy groceries"

**Error Handling**:
- **Task not found**: Agent responds "I couldn't find that task in your list"
- **MCP tool fails**: Agent responds "There was an error completing that task. Please try again."
- **Database connection fails**: Agent responds "I'm having trouble connecting to your tasks right now. Please try again in a moment."
- **Ambiguous intent**: Agent asks clarifying question (per FR-036)
- **No auto-retry**: User must manually retry failed operations (per FR-035a)

### Frontend Integration Plan

**OpenAI ChatKit UI Integration**:

1. **Installation**: Add ChatKit UI to Next.js frontend
   ```
   npm install @openai/chatkit-ui
   ```

2. **Chat Component** (new page: `/app/chat/page.tsx`):
   - Render ChatKit component with clean, neutral, modern styling
   - Connect to `/api/{user_id}/chat` endpoint
   - Pass authenticated user_id from Better Auth session
   - Handle conversation continuity via conversation_id

3. **Message Rendering**:
   - User messages: Right-aligned, blue background
   - Assistant messages: Left-aligned, gray background
   - Tool call indicators: Subtle gray text below assistant messages
   - Timestamps: Show for each message
   - Format task lists with bullet points or numbered lists

4. **Loading States**:
   - Show "typing..." indicator when waiting for agent response
   - Disable input field during request
   - Show tool execution status: "Checking your tasks...", "Adding task..."
   - Timeout after 30 seconds with retry option

5. **Error States**:
   - Task not found: Show inline error with retry button
   - Network error: Show "Connection lost" with retry
   - Auth error: Redirect to login page
   - MCP tool failure: Show user-friendly message from agent

6. **Conversation Continuity**:
   - Conversation ID managed automatically (single persistent conversation per user)
   - Load conversation history on page mount (GET /api/{user_id}/conversation/history endpoint)
   - Display last 50 messages initially (pagination for older messages)
   - Auto-scroll to bottom on new messages

7. **Accessibility**:
   - ARIA labels for screen readers
   - Keyboard navigation (Enter to send, Escape to clear input)
   - Focus management for input field

## Risks & Constraints

### Risk 1: Tool Misuse (Agent bypasses MCP architecture)

**Risk**: Agent attempts direct database access or fabricates task data instead of using MCP tools

**Mitigation**:
- Agent instructions explicitly state "You MUST use the provided tools for all task operations"
- Agent has no database connection configuration
- MCP tools are the ONLY interface between agent and data
- Contract tests verify agent only calls defined MCP tools
- Code review enforces no direct DB imports in agent layer

**Detection**: Unit tests + integration tests verify all task operations go through MCP

### Risk 2: Stateless Consistency (Race conditions in conversation state)

**Risk**: Concurrent requests from same user could cause conversation history conflicts

**Mitigation**:
- Database transactions with optimistic locking on conversations table
- Last-write-wins strategy acceptable for chat (messages are append-only)
- Conversation history query uses `ORDER BY timestamp DESC LIMIT 100` (deterministic)
- Each request loads fresh from database (no cache invalidation issues)

**Detection**: Load testing with concurrent requests per user

### Risk 3: Incorrect Task Interpretation (Agent misunderstands intent)

**Risk**: Agent selects wrong tool or misidentifies task references (SC-003 target: 90% accuracy)

**Mitigation**:
- Clear agent instructions with examples for each tool
- Case-insensitive substring matching reduces false negatives
- Clarification questions for ambiguous requests (User Story 3)
- Conversation context (last 100 messages) helps resolve pronouns
- User can always retry with more explicit phrasing

**Detection**: Acceptance testing with diverse natural language inputs, track success rate

### Risk 4: MCP Latency or Failure Handling

**Risk**: MCP tool calls timeout or fail, leaving user without response

**Mitigation**:
- FastAPI timeout: 30 seconds per request (configurable)
- MCP tools designed for fast execution (database queries < 500ms)
- Error messages are user-friendly (no technical jargon per FR-035)
- Manual retry encouraged (no auto-retry to avoid duplicates per FR-035a)
- Health check endpoint monitors database connectivity

**Detection**: Load testing + chaos engineering (simulate DB failures)

### Risk 5: Conversation History Size (Performance degradation)

**Risk**: As conversations grow, loading 100 messages becomes slow

**Mitigation**:
- Index on (conversation_id, timestamp DESC) for fast query
- LIMIT 100 prevents unbounded growth
- Neon PostgreSQL optimized for serverless (fast cold starts)
- SQLModel uses async queries (non-blocking)
- Consider pagination if 100 messages proves too slow (deferred to monitoring)

**Detection**: Monitor P95 latency for /chat endpoint, alert if > 3 seconds

### Risk 6: OpenAI Agents SDK Version Compatibility

**Risk**: Agents SDK updates could break our implementation

**Mitigation**:
- Pin exact version in requirements.txt (v0.2.9)
- MCP context validation documented stable API patterns
- Comprehensive tests protect against regressions
- Monitor Agents SDK changelog for breaking changes

**Detection**: CI tests fail on dependency updates

## Project Structure

### Documentation (this feature)

```text
specs/003-ai-chatbot/
├── spec.md              # Feature specification (complete)
├── clarifications.md    # Clarification session (complete)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (next)
├── data-model.md        # Phase 1 output (next)
├── quickstart.md        # Phase 1 output (next)
├── contracts/           # Phase 1 output (next)
│   └── chat-api.yaml    # OpenAPI spec for /chat endpoint
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

**Web Application Structure** (frontend + backend detected):

```text
backend/
├── agent/
│   ├── __init__.py
│   ├── agent_config.py           # Agent initialization with instructions and tools
│   └── runner.py                 # Runner execution wrapper
├── mcp/
│   ├── __init__.py
│   ├── server.py                 # FastMCP server setup
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── add_task.py           # @mcp.tool() for add_task
│   │   ├── list_tasks.py         # @mcp.tool() for list_tasks
│   │   ├── complete_task.py      # @mcp.tool() for complete_task
│   │   ├── delete_task.py        # @mcp.tool() for delete_task
│   │   └── update_task.py        # @mcp.tool() for update_task
│   └── schemas.py                # Tool parameter/response schemas
├── models/
│   ├── __init__.py
│   ├── conversation.py           # SQLModel: Conversation
│   ├── message.py                # SQLModel: Message
│   └── todo.py                   # SQLModel: Todo (existing from Phase II)
├── schemas/
│   ├── __init__.py
│   ├── chat_request.py           # Pydantic: ChatRequest
│   ├── chat_response.py          # Pydantic: ChatResponse
│   └── todo.py                   # Pydantic: TodoCreate, TodoUpdate (existing)
├── api/
│   ├── __init__.py
│   ├── deps.py                   # Dependency injection (get_session, get_current_user)
│   ├── chat.py                   # POST /api/{user_id}/chat endpoint
│   └── todos.py                  # Existing Phase II todo endpoints
├── services/
│   ├── __init__.py
│   ├── task_service.py           # TaskService for CRUD via SQLModel
│   └── conversation_service.py   # ConversationService for chat history
├── db/
│   ├── __init__.py
│   └── session.py                # Database connection + session management
├── main.py                        # FastAPI app entry point
└── tests/
    ├── test_mcp_tools.py          # MCP tool contract tests
    ├── test_agent_workflows.py    # Agent integration tests
    ├── test_chat_endpoint.py      # API endpoint tests
    └── test_conversation_state.py # Stateless architecture tests

frontend/
├── app/
│   ├── chat/
│   │   └── page.tsx               # Chat page with ChatKit UI
│   ├── todos/
│   │   └── page.tsx               # Existing Phase II todo list page
│   └── layout.tsx                 # Root layout with Better Auth
├── components/
│   ├── ChatInterface.tsx          # ChatKit UI wrapper component
│   ├── MessageList.tsx            # Message rendering component
│   └── TodoList.tsx               # Existing Phase II component
├── services/
│   ├── chatApi.ts                 # API client for /chat endpoint
│   └── todoApi.ts                 # Existing Phase II API client
└── types/
    ├── chat.ts                    # TypeScript types for chat
    └── todo.ts                    # Existing Phase II types

tests/
├── backend/                       # Backend tests (pytest)
│   ├── integration/
│   │   ├── test_chat_flow.py      # End-to-end chat scenarios
│   │   └── test_mcp_integration.py # MCP server integration
│   ├── unit/
│   │   ├── test_agent_config.py   # Agent initialization tests
│   │   ├── test_mcp_tools.py      # Individual tool tests
│   │   └── test_services.py       # Service layer tests
│   └── contract/
│       └── test_mcp_contracts.py  # MCP tool schema validation
└── frontend/                      # Frontend tests (Jest/Playwright)
    ├── unit/
    │   └── ChatInterface.test.tsx # Component tests
    └── e2e/
        └── chat.spec.ts            # End-to-end chat flow
```

**Structure Decision**: Web application structure with backend/frontend separation. MCP server integrated as `backend/mcp/` module (not standalone process) for simpler deployment. Agent layer in `backend/agent/` clearly separated from MCP and API layers to enforce constitutional principle VI (Separation of Concerns).

## Deployment Strategy

**Backend (Railway)**
- Service: Python FastAPI Application
- Build Command: `uv pip install -r requirements.txt`
- Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- Environment Variables:
  - `DATABASE_URL`: Neon PostgreSQL connection string
  - `GEMINI_API_KEY`: Google Gemini API Key
  - `MODEL_ID`: `gemini-2.5-flash`
  - `OPENAI_BASE_URL`: OpenAI-compatible endpoint for Gemini (if using adapter)
  - `BETTER_AUTH_SECRET`: Auth secret
  - `BETTER_AUTH_URL`: Auth URL

**Frontend (Vercel)**
- Framework: Next.js
- Build Command: `npm run build`
- Environment Variables:
  - `NEXT_PUBLIC_API_URL`: Railway Backend URL
  - `BETTER_AUTH_URL`: Railway Backend URL (for auth)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations detected**. All Phase III requirements align with constitutional principles. No additional complexity beyond what is necessary for the feature.

## Phase 0: Research & Technology Validation

**Status**: ✅ COMPLETE

MCP context validation performed via Context7 MCP server. Key findings documented below.

### Technology Stack Validation

**OpenAI Agents SDK (Python) v0.2.9+**:
- **Purpose**: Agent orchestration and tool execution
- **Key APIs**:
  - `Agent(name, instructions, tools)` - Define agent with MCP tools
  - `@function_tool` decorator - Register Python functions as tools
  - `Runner.run(agent, input, session)` - Execute agent with conversation context
  - `SQLiteSession` or custom session for conversation memory
- **Pattern**: Create agent with tools, execute with Runner, handle tool calls automatically
- **Integration**: Works seamlessly with FastAPI async patterns

**MCP Python SDK (modelcontextprotocol/python-sdk)**:
- **Purpose**: Define MCP server with tool definitions
- **Key APIs**:
  - `FastMCP(name)` - Initialize MCP server
  - `@mcp.tool()` decorator - Register tool with typed parameters
  - Tool functions return structured data (validated against schemas)
- **Pattern**: FastMCP provides high-level interface, low-level Server class for advanced use
- **Integration**: Can run as embedded module (not separate process) in FastAPI app

**FastAPI 0.115+**:
- **Purpose**: Async REST API backend
- **Key APIs**:
  - `@app.post("/path")` with Pydantic models for request/response
  - `Depends()` for dependency injection (database sessions, auth)
  - Async endpoint functions with `async def`
- **Pattern**: Define Pydantic schemas, use dependency injection for services
- **Integration**: SQLModel integrates natively with FastAPI

**SQLModel**:
- **Purpose**: ORM for database models with Pydantic validation
- **Key APIs**:
  - `SQLModel` base class with `table=True` for database models
  - `Session` for database transactions
  - `select()` for queries with filtering and ordering
- **Pattern**: Define models with Field types, use Session for CRUD
- **Integration**: Works with Neon PostgreSQL (PostgreSQL-compatible)

**Neon Serverless PostgreSQL**:
- **Purpose**: Database with existing Phase II tables + new conversation tables
- **Key Features**: Serverless (auto-scaling), fast cold starts, PostgreSQL-compatible
- **Connection**: Standard PostgreSQL connection string with asyncpg driver
- **Integration**: SQLModel + asyncpg for async queries

**Better Auth**:
- **Purpose**: Authentication system (existing from Phase II)
- **Integration**: Middleware validates session tokens, provides user_id to endpoints
- **Pattern**: Protect chat endpoint with auth dependency

**OpenAI ChatKit UI**:
- **Purpose**: Frontend chat interface component
- **Installation**: npm package `@openai/chatkit-ui`
- **Integration**: React component for Next.js, styled with Tailwind CSS
- **Pattern**: Connect to API endpoint, handle loading/error states

### Decisions

**Decision 1: MCP Server as Embedded Module**
- **Rationale**: Simplifies deployment (no separate process), reduces latency, easier to manage
- **Alternative Considered**: Standalone MCP server process → Rejected due to deployment complexity and inter-process communication overhead
- **Implementation**: Import FastMCP in `backend/mcp/server.py`, register tools, expose via FastAPI startup

**Decision 2: Single Persistent Conversation Per User**
- **Rationale**: Simplifies UX (no conversation management UI), aligns with clarification Q1
- **Alternative Considered**: Multiple conversations with selector UI → Rejected for Phase III simplicity
- **Implementation**: One row per user in conversations table, auto-created on first message

**Decision 3: Last 100 Messages for Agent Context**
- **Rationale**: Balances context window (agent can resolve references) with performance/cost
- **Alternative Considered**: All messages, last 50 messages, summarization → 100 chosen per clarification Q3
- **Implementation**: SQL query `ORDER BY timestamp DESC LIMIT 100`, reverse for chronological order

**Decision 4: Case-Insensitive Substring Matching**
- **Rationale**: Good UX (users don't need exact titles), simple to implement, fast
- **Alternative Considered**: Fuzzy matching, semantic search → Rejected for Phase III simplicity per clarification Q2
- **Implementation**: SQL `LOWER(title) LIKE LOWER('%{task_ref}%')` in TaskService

**Decision 5: Manual Retry Only (No Auto-Retry)**
- **Rationale**: Prevents duplicate operations, simpler logic, clear to user what happened
- **Alternative Considered**: Auto-retry with idempotency → Rejected per clarification Q5
- **Implementation**: Agent returns error message, user must send new message to retry

## Next Steps

After completing this plan.md:

1. ✅ Phase 0 complete - MCP context validated
2. **Phase 1**: Generate design artifacts:
   - `data-model.md` - Database schema for conversations and messages
   - `contracts/chat-api.yaml` - OpenAPI spec for /chat endpoint
   - `quickstart.md` - Developer quickstart guide
3. **Phase 2**: Run `/sp.tasks` to generate tasks.md
4. **Phase 3**: Run `/sp.implement` to execute tasks

**Planning Status**: Phase 0 complete, ready for Phase 1 design artifacts.

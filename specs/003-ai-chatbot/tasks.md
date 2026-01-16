# Tasks: AI-Powered Todo Chatbot

**Input**: Design documents from `/specs/003-ai-chatbot/`
**Prerequisites**: plan.md, spec.md, clarfications.md

**Organization**: Tasks are grouped by phase and user story to enable independent implementation and testing.

## Phase 1: Foundational Infrastructure (Blocking)

**Purpose**: Core infrastructure for conversations and MCP server that MUST be complete before user story implementation.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T001 [Setup] Initialize backend directory structure (`backend/agent`, `backend/mcp`, `backend/api`) per plan (ref: plan.md-System Architecture) <!-- id: T-001 -->
- [ ] T002 [Data] Create SQLModel schemas for `Conversation` and `Message` in `backend/models/` (ref: spec.md-FR-022, FR-023) <!-- id: T-002 -->
- [ ] T003 [Data] Create DB migration for new tables and apply to Neon database (ref: plan.md-System Architecture) <!-- id: T-003 -->
- [ ] T004 [Service] Implement `ConversationService` for creating/loading conversations and messages (ref: spec.md-FR-022a, FR-106) <!-- id: T-004 -->
- [ ] T005 [MCP] Setup basic FastMCP server structure in `backend/mcp/server.py` (ref: spec.md-FR-012) <!-- id: T-005 -->
- [ ] T006 [MCP] Implement `TaskService` in `backend/services/task_service.py` with case-insensitive substring matching logic (ref: spec.md-FR-007) <!-- id: T-006 -->

**Checkpoint**: Database tables created, services ready, MCP server shell exists.

---

## Phase 2: MCP Tool Implementation (Priority: P0)

**Goal**: Implement the 5 strictly required MCP tools that the agent will use.
**Ref**: spec.md FR-010 to FR-015

- [ ] T007 [MCP] Implement `list_tasks` tool in `backend/mcp/tools/list_tasks.py` with filtering (ref: spec.md-FR-012, FR-006) <!-- id: T-007 -->
- [ ] T008 [MCP] Implement `add_task` tool in `backend/mcp/tools/add_task.py` (ref: spec.md-FR-012, FR-005) <!-- id: T-008 -->
- [ ] T009 [MCP] Implement `update_task` tool in `backend/mcp/tools/update_task.py` (ref: spec.md-FR-012, FR-008) <!-- id: T-009 -->
- [ ] T010 [MCP] Implement `complete_task` tool in `backend/mcp/tools/complete_task.py` (ref: spec.md-FR-012, FR-007) <!-- id: T-010 -->
- [ ] T011 [MCP] Implement `delete_task` tool in `backend/mcp/tools/delete_task.py` (ref: spec.md-FR-012, FR-009) <!-- id: T-011 -->
- [ ] T012 [Test] Create contract tests for all MCP tools in `tests/contract/test_mcp_contracts.py` ensuring they don't access DB directly (ref: spec.md-FR-011) <!-- id: T-012 -->

**Checkpoint**: All 5 MCP tools functional, tested, and ready for agent use.

---

## Phase 3: Agent & Backend Integration (Priority: P1) - User Story 1

**Goal**: delivering the core "Natural Language Task Management" story.
**Ref**: spec.md US1, FR-016 to FR-020

- [X] T013 [Agent] Configure OpenAI Agent with Gemini 2.5 Flash model and tool registration in `backend/agent/agent_config.py` using simple OpenAI-compatible client configuration (ref: spec.md-FR-016, FR-017) <!-- id: T-013 -->
- [X] T014 [API] Implement POST `/api/{user_id}/chat` endpoint shell with Auth validation (ref: spec.md-FR-004, FR-030) <!-- id: T-014 -->
- [X] T015 [Logic] Implement message persistence logic (save user msg -> running agent -> save response) (ref: spec.md-FR-109, FR-024) <!-- id: T-015 -->
- [X] T016 [Logic] Implement history loading strategy (last 100 messages) in `ConversationService` (ref: spec.md-FR-022b, FR-107) <!-- id: T-016 -->
- [X] T017 [Integration] Wire up `Runner.run` inside the API endpoint to execute agent with real tools (ref: plan.md-Request Lifecycle) <!-- id: T-017 -->
- [ ] T018 [Verify] Verify US1: "Add a task to buy milk" creates task and returns confirmation (ref: spec.md-SC-001) <!-- id: T-018 -->

**Checkpoint**: End-to-end backend flow works. Agent can CRUD tasks via API.

---

## Phase 4: Frontend Chat Interface (Priority: P1) - User Story 1

**Goal**: User interface for the chatbot.
**Ref**: spec.md FR-001 to FR-003

- [X] T019 [UI] Install and configure `@openai/chatkit-react` (or `@openai/chatkit`) in Next.js (ref: spec.md-FR-003) <!-- id: T-019 -->
- [X] T020 [UI] Create `app/chat/page.tsx` and integrate Chat component (ref: spec.md-FR-001) <!-- id: T-020 -->
- [X] T021 [UI] Wire Chat component to `/api/{user_id}/chat` endpoint (ref: plan.md-Frontend Integration) <!-- id: T-021 -->
- [X] T022 [UI] Implement initial history load on page mount (ref: spec.md-FR-002) <!-- id: T-022 -->
- [X] T023 [Verify] Verify US1: Full conversational flow from UI works (ref: spec.md-SC-004) <!-- id: T-023 -->

**Checkpoint**: MVP Complete. User can chat to manage tasks.

---

## Phase 5: Advanced Capabilities (Priority: P2/P3) - User Story 2 & 3

**Goal**: Explanation and Clarification capabilities.
**Ref**: spec.md US2, US3

- [ ] T024 [Agent] Enhance agent instructions to support Task Explanation (analyze before answering) (ref: spec.md-FR-026, FR-027) <!-- id: T-024 -->
- [ ] T025 [MCP] Verify `list_tasks` supports filtering by title for explanation context (ref: spec.md-FR-026) <!-- id: T-025 -->
- [ ] T026 [Agent] Enhance agent instructions to ask clarifying questions for ambiguous requests (ref: spec.md-FR-007a, FR-036) <!-- id: T-026 -->
- [ ] T027 [Verify] Verify US2: "What is the buy milk task for?" returns explanation (ref: spec.md-SC-005) <!-- id: T-027 -->
- [ ] T028 [Verify] Verify US3: "Complete task" (ambiguous) triggers clarification question (ref: spec.md-SC-008) <!-- id: T-028 -->

---

## Phase 6: Polish, Deployment & Robustness

**Goal**: Error handling, validation, and production deployment.

- [X] T029 [Error] Implement graceful error handling for MCP failures in Agent instructions (ref: spec.md-FR-035) <!-- id: T-029 -->
- [X] T030 [Error] Ensure correct HTTP status codes and error responses in Chat API (ref: spec.md-FR-037) <!-- id: T-030 -->
- [X] T031 [Polish] Verify formatted output for task lists (markdown/bullet points) (ref: spec.md-FR-042) <!-- id: T-031 -->
- [X] T032 [Config] Configure backend environment variables for Railway (`GEMINI_API_KEY`, `MODEL_ID`, `DATABASE_URL`) <!-- id: T-032 -->
- [X] T033 [Config] Configure frontend environment variables for Vercel (`NEXT_PUBLIC_API_URL`) <!-- id: T-033 -->
- [X] T034 [Deploy] Deploy backend to Railway and verify health check <!-- id: T-034 -->
- [X] T035 [Deploy] Deploy frontend to Vercel and verify chat functionality <!-- id: T-035 -->
- [X] T036 [Final] Run full acceptance suite against Success Criteria SC-001 to SC-009 <!-- id: T-036 -->

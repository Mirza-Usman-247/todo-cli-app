# Feature Specification: AI-Powered Todo Chatbot

**Feature Branch**: `003-ai-chatbot`
**Created**: 2026-01-15
**Status**: Draft
**Input**: User description: "AI-Powered Todo Chatbot with MCP and OpenAI Agents SDK integration"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Task Management (Priority: P1)

Users can add, list, complete, update, and delete tasks through natural language conversation without needing to know specific commands or UI navigation.

**Why this priority**: This is the core value proposition of the chatbot - enabling users to manage todos through conversational interface. Without this, the chatbot has no purpose.

**Independent Test**: Can be fully tested by having a user type conversational requests like "add a task to buy groceries" or "show me all my tasks" and verifying the chatbot correctly interprets intent and executes the appropriate operation.

**Acceptance Scenarios**:

1. **Given** user is authenticated and has an empty task list, **When** user types "add a task to buy groceries tomorrow", **Then** chatbot creates a new task with title "buy groceries tomorrow" (description empty) and confirms "Task added: Buy groceries tomorrow"
2. **Given** user has 5 tasks in their list, **When** user types "show me all my tasks", **Then** chatbot displays all 5 tasks with their current status
3. **Given** user has a task titled "Buy groceries", **When** user types "mark buy groceries as complete", **Then** chatbot marks the task complete and confirms the action
4. **Given** user has a task titled "Buy groceries", **When** user types "change buy groceries to buy milk instead", **Then** chatbot updates the task title and confirms the change
5. **Given** user has a task titled "Buy groceries", **When** user types "delete the buy groceries task", **Then** chatbot removes the task and confirms deletion

---

### User Story 2 - Task Context and Explanation (Priority: P2)

Users can ask the chatbot to explain what a task is for, why it was created, or get context about a task based on its title and description.

**Why this priority**: Adds intelligent assistant capabilities beyond basic CRUD. Helps users understand their task history and intent, especially useful for tasks created long ago.

**Independent Test**: Can be tested independently by creating tasks with descriptive titles and descriptions, then asking the chatbot "what is the buy groceries task for?" and verifying it provides a meaningful explanation based on stored data.

**Acceptance Scenarios**:

1. **Given** user has a task "Buy groceries" with description "Need ingredients for dinner party on Saturday", **When** user asks "what is the buy groceries task for?", **Then** chatbot fetches the task data and explains "This task is for purchasing ingredients needed for your dinner party on Saturday"
2. **Given** user has a task "Call dentist" with description "Schedule annual checkup", **When** user asks "why did I create the call dentist task?", **Then** chatbot explains "You created this task to schedule your annual dental checkup"
3. **Given** user has a task with no description, **When** user asks about the task, **Then** chatbot explains based only on the task title without making assumptions

---

### User Story 3 - Conversational Clarification (Priority: P3)

When user requests are ambiguous, the chatbot asks clarifying questions before taking action rather than guessing or failing.

**Why this priority**: Prevents errors from misinterpretation and provides better user experience. Not critical for MVP but significantly improves usability.

**Independent Test**: Can be tested by providing intentionally ambiguous requests like "update my task" when multiple tasks exist, and verifying the chatbot asks "Which task would you like to update?" rather than guessing or failing.

**Acceptance Scenarios**:

1. **Given** user has 3 tasks, **When** user types "complete my task", **Then** chatbot asks "Which task would you like to complete?" and lists the options
2. **Given** user types "add task" without specifying what task, **When** chatbot processes the request, **Then** chatbot asks "What task would you like to add?"
3. **Given** user types something unclear like "do that thing I mentioned", **When** chatbot processes the request, **Then** chatbot responds "Could you clarify what you'd like me to do?"

---

### Edge Cases

- What happens when user adds a task via chatbot? The entire natural language input becomes the task title, and the description field is left empty (users can add descriptions later via web UI)
- What happens when user tries to complete a task that doesn't exist? Chatbot responds with polite message: "I couldn't find that task in your list"
- What happens when user references a task with partial text that matches multiple tasks? Chatbot lists all matching tasks and asks "Which task did you mean?" (e.g., user says "complete buy" when tasks "Buy milk" and "Buy groceries" both exist)
- What happens when user tries to access another user's tasks? System enforces user isolation - user can only see their own tasks, chatbot never exposes other users' data
- What happens when the database connection fails? Chatbot explains the error politely: "I'm having trouble connecting to your tasks right now. Please try again in a moment" (no automatic retry; user must manually retry the operation)
- What happens when user's conversation history grows very large? System loads only the last 100 messages per request; older messages remain in database but don't affect performance or agent context window
- What happens when user asks the chatbot to do something outside its capabilities (like "what's the weather")? Chatbot politely responds: "I can help you manage your tasks, but I can't assist with that request"

## Requirements *(mandatory)*

### Functional Requirements

**Chatbot Interface**:
- **FR-001**: System MUST provide a chat interface where authenticated users can send natural language messages
- **FR-002**: System MUST display chatbot responses in the same conversation thread
- **FR-003**: Chat interface MUST use OpenAI ChatKit UI with clean, neutral, modern styling
- **FR-004**: Chat interface MUST communicate with backend via POST /api/{user_id}/chat endpoint

**Natural Language Task Operations**:
- **FR-005**: Chatbot MUST interpret natural language requests for adding tasks (e.g., "add a task to...", "create a reminder to...")
- **FR-005a**: When adding tasks via chatbot, the full user input MUST become the task title, and description field MUST remain empty (unless user explicitly structures input with title and description)
- **FR-006**: Chatbot MUST interpret natural language requests for listing tasks (e.g., "show my tasks", "what do I need to do")
- **FR-007**: Chatbot MUST interpret natural language requests for completing tasks (e.g., "mark X as done", "complete X") using case-insensitive substring matching
- **FR-007a**: When multiple tasks match the user's reference, chatbot MUST ask for clarification and list all matching tasks
- **FR-008**: Chatbot MUST interpret natural language requests for updating tasks (e.g., "change X to Y", "update X") using case-insensitive substring matching
- **FR-009**: Chatbot MUST interpret natural language requests for deleting tasks (e.g., "delete X", "remove X") using case-insensitive substring matching

**MCP Tool Architecture** (Critical - Hard Requirements):
- **FR-010**: Chatbot MUST use MCP tools exclusively for all task CRUD operations
- **FR-011**: Chatbot MUST NEVER access the database directly
- **FR-012**: MCP server MUST expose stateless tools: add_task, list_tasks, complete_task, delete_task, update_task
- **FR-013**: Each MCP tool invocation MUST include user_id context for user isolation
- **FR-014**: MCP tools MUST delegate to backend services for all database operations
- **FR-015**: MCP tools MUST return structured responses that the chatbot can format for users

**Agent Integration**:
- **FR-016**: System MUST use OpenAI Agents SDK to power the chatbot
- **FR-016a**: System MUST use a free tier-compatible model like Gemini 2.5 Flash as the underlying LLM
- **FR-017**: System MUST use a single task-oriented agent (no multi-agent orchestration)
- **FR-018**: Agent MUST analyze user intent and select the appropriate MCP tool
- **FR-019**: Agent MUST format MCP tool responses into natural, conversational language
- **FR-020**: Agent MUST ask clarifying questions when user intent is ambiguous

**Conversation State Management** (Critical - Stateless Architecture):
- **FR-021**: Backend server MUST be stateless - no in-memory conversation storage
- **FR-022**: Each chat request MUST load conversation history from database (from user's single persistent conversation)
- **FR-022a**: System MUST create user's persistent conversation on first chat message if it doesn't exist
- **FR-022b**: System MUST load only the last 100 messages from conversation history to provide to the agent (older messages remain in database but are not loaded into agent context)
- **FR-023**: System MUST append new messages to conversation history
- **FR-024**: System MUST save updated conversation history to database before returning response
- **FR-025**: Conversation history MUST be isolated per user (users cannot access other users' conversations)

**Task Explanation**:
- **FR-026**: When user asks about a task's purpose, chatbot MUST fetch task data via MCP
- **FR-027**: Chatbot MUST analyze task title and description to explain intent
- **FR-028**: Chatbot MUST provide explanations in natural, human-friendly language
- **FR-029**: Chatbot MUST NOT make assumptions beyond data stored in the database

**Authentication and Security**:
- **FR-030**: All chat requests MUST be authenticated using existing Better Auth system
- **FR-031**: System MUST validate that user_id in request path matches authenticated user
- **FR-032**: Users MUST only be able to manage and view their own tasks through the chatbot
- **FR-033**: System MUST enforce user isolation at all layers (API, MCP tools, database)

**Error Handling**:
- **FR-034**: When task not found, chatbot MUST respond with polite message (e.g., "I couldn't find that task")
- **FR-035**: When MCP tool fails, chatbot MUST explain the error without technical jargon and ask user to retry manually
- **FR-035a**: System MUST NOT automatically retry failed MCP tool operations to avoid potential duplicate actions
- **FR-036**: When user request is invalid or unclear, chatbot MUST ask for clarification
- **FR-037**: System MUST handle database connection failures gracefully with user-friendly messages

**Deployment Requirements**:
- **FR-043**: Frontend MUST be deployed to Vercel
- **FR-044**: Backend MUST be deployed to Railway

**Confirmations and Feedback**:
- **FR-038**: After adding a task, chatbot MUST confirm with task details
- **FR-039**: After completing a task, chatbot MUST confirm the action
- **FR-040**: After updating a task, chatbot MUST confirm what changed
- **FR-041**: After deleting a task, chatbot MUST confirm the deletion
- **FR-042**: When listing tasks, chatbot MUST format output in a readable way

### Key Entities

- **Conversation**: Represents a persistent chat session for a user. Contains user_id, creation timestamp, and metadata. Each user has exactly one persistent conversation that contains all their chat history.

- **Message**: Represents a single message in a conversation. Contains conversation_id (foreign key), role (user/assistant), content (message text), and timestamp. Messages form the conversation history.

- **ChatRequest**: Represents an incoming chat request from the user. Contains user_id, message text, and conversation context.

- **ChatResponse**: Represents the chatbot's response. Contains response text and updated conversation state to be persisted.

- **MCPToolInvocation**: Represents a call to an MCP tool. Contains tool name (add_task, list_tasks, etc.), parameters, user_id context, and result.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully add a task through natural language conversation in under 10 seconds
- **SC-002**: Users can list all their tasks and receive a formatted response in under 3 seconds (regardless of conversation history length)
- **SC-003**: 90% of user task management requests are correctly interpreted on the first attempt without requiring clarification
- **SC-004**: Users receive clear confirmation messages for all task operations (add, complete, update, delete) within 2 seconds
- **SC-005**: The chatbot successfully explains task purpose based on stored data with 100% accuracy (no fabricated information)
- **SC-006**: Zero cross-user data leaks - users can only access their own tasks and conversations
- **SC-007**: System maintains stateless architecture - server can restart without losing conversation history
- **SC-008**: 95% of ambiguous requests result in clarifying questions rather than errors or incorrect actions
- **SC-009**: Users can interact with the chatbot using natural, conversational language without learning specific commands or syntax

## Clarifications

### Session 2026-01-15

- Q: Conversation lifecycle - initialization (one persistent conversation vs multiple conversations per user)? → A: One persistent conversation per user; all messages append to the same conversation indefinitely
- Q: Task matching strategy (exact vs case-insensitive vs fuzzy matching)? → A: Case-insensitive substring matching; if multiple tasks match, chatbot asks for clarification
- Q: Conversation history limits (load all messages vs limit per request)? → A: Load last 100 messages per request; older messages archived but not loaded into agent context
- Q: Task description handling in natural language input (split title/description vs full input as title)? → A: Full user input becomes task title; description field remains empty unless user explicitly provides structure
- Q: MCP tool failure recovery behavior (auto-retry vs ask user to retry)? → A: Explain the error to user and ask them to retry manually; no automatic retry

## Assumptions

- Users are already authenticated via the existing Better Auth system from Phase II
- The existing Todo backend API and database schema from Phase II are operational
- OpenAI Agents SDK and Official MCP SDK are accessible and properly licensed
- OpenAI ChatKit UI library is available and compatible with the Next.js frontend
- Users have basic familiarity with chat interfaces (typing messages, reading responses)
- Database supports concurrent access for conversation history (via PostgreSQL transactions)
- Users will primarily use text-based chat (no voice, images, or rich media in Phase III)
- Network latency between frontend and backend is reasonable (<500ms) for chat responsiveness

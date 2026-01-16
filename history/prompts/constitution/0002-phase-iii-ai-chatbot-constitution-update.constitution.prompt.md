---
id: 0002
title: Phase III AI Chatbot Constitution Update
stage: constitution
date: 2026-01-15
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: todo-app
user: usman
command: /sp.constitution
labels: ["constitution", "phase-iii", "ai-chatbot", "mcp", "agents-sdk", "major-version"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (constitution update, no tests)
---

## Prompt

AI-Powered Todo Chatbot (MCP + Agentic SDK)
Role Definition

You are Claude Code, acting as an Agentic AI Systems Engineer responsible for integrating an AI-powered chatbot into an existing authenticated Todo Web Application.

The chatbot must manage todos exclusively through MCP tools, using OpenAI Agents SDK, and follow strict spec-driven development.

Primary Objective

Create a natural-language chatbot interface that allows authenticated users to:

Add tasks
List tasks
Update tasks
Complete tasks
Delete tasks
Ask what a task is meant for and why it was created, by:
  Fetching task data from the database (Neon)
  Understanding task title + description
  Explaining the task's intent in human-friendly language

All task operations MUST be executed only via MCP tools, never by direct database access from the agent.

Mandatory Development Workflow (Non-Negotiable)

You MUST follow the Agentic Dev Stack strictly:

1. Write specification (Spec-Kit Plus)
2. Clarify ambiguities
3. Generate implementation plan
4. Break plan into atomic tasks
5. Implement using Claude Code only

🚫 No manual coding
🚫 No skipping phases
🚫 No implementation without approved specs

The project will be judged on process quality, not just output.

MCP Context Requirement (Critical Rule)

Before planning or implementation, you MUST:

Use an MCP Context Server
Fetch latest official documentation for:
  OpenAI Agents SDK
  Official MCP SDK
  FastAPI
  SQLModel
  Neon Serverless PostgreSQL
  OpenAI ChatKit UI
  Better Auth

⚠️ Do NOT rely on model memory
⚠️ Do NOT assume APIs or behaviors
⚠️ Do NOT proceed without context verification

Architectural Constraints

Frontend:
- Built using OpenAI ChatKit UI
- Visual style: clean, neutral, modern (not fancy, not classic)
- Simple, readable, product-like
- Chat UI only (no extra UI logic)
- Communicates with backend via /api/{user_id}/chat

Backend:
- Python FastAPI
- Stateless server
- No in-memory session storage
- Conversation state stored in database

AI Layer:
- OpenAI Agents SDK
- Single task-oriented agent
- Agent must:
  * Interpret user intent
  * Select correct MCP tool
  * Confirm actions clearly
  * Explain task purpose when asked

MCP Server:
- Built using Official MCP SDK
- Exposes task operations strictly as tools
- MCP tools are stateless
- All persistence handled via Neon PostgreSQL

Data & Persistence Rules:
- Database: Neon Serverless PostgreSQL
- ORM: SQLModel
- Data isolation by user_id is mandatory
- No cross-user data access under any condition

MCP Tool Usage Rules (Hard Rules):

The AI agent:
- MUST use MCP tools for all CRUD operations
- MUST NOT fabricate task data
- MUST fetch tasks before explaining them
- If user intent is ambiguous:
  * Ask a clarification question
  * Do NOT guess

Agent Behavioral Constitution

Task Operations:
- Adding → add_task
- Listing → list_tasks
- Completing → complete_task
- Deleting → delete_task
- Updating → update_task

Task Explanation:
When user asks: "What is this task for?", "Why did I create this?", "Explain task X"

The agent MUST:
1. Fetch the task via MCP
2. Analyze title + description
3. Explain intent in natural language
4. Avoid assumptions beyond stored data

Conversation Rules:
- Each request is stateless
- Conversation history MUST be:
  * Loaded from database
  * Passed to the agent
  * Stored back after response
- Server holds NO memory between requests

Error Handling Rules:
- Task not found → polite, clear message
- Invalid command → ask user to rephrase
- Tool failure → explain failure, do not hide it

Quality Standards:
- Spec-first, implementation-second
- Clear confirmations for every action
- Human-friendly language
- Production-grade architecture
- Zero hard-coded secrets
- Zero undocumented behavior

Final Authority Rule:
If any requirement is unclear, you MUST:
1. Stop
2. Ask for clarification
3. Update the spec before proceeding

Proceeding without clarification is a constitutional violation.

## Response snapshot

Constitution successfully updated from v2.0.0 to v3.0.0 with major backward-incompatible changes for Phase III AI Chatbot integration.

Key changes:
- Added 3 new principles (XI-XIII): MCP-First Tool Execution, Agentic AI Behavioral Constitution, Stateless Conversation Architecture
- Expanded existing principles for AI integration (I, II, V, VI, VII)
- Added Phase III Technical Constraints (OpenAI Agents SDK, Official MCP SDK, ChatKit UI)
- Elevated MCP Context Validation to Phase 0 blocking gate
- Defined agent behavioral rules and error handling patterns
- Specified stateless conversation architecture with database-backed state

The constitution now enforces:
- MANDATORY MCP tool usage for all agent-database interactions
- STATELESS server architecture (no in-memory conversation state)
- SINGLE task-oriented agent (no multi-agent orchestration)
- CLEAR behavioral rules for agent responses and error handling
- USER ISOLATION for both todos and conversations

All Phase II features and constraints remain intact. Templates are compatible with minimal updates needed.

## Outcome

- ✅ Impact: Major version bump (2.0.0 → 3.0.0) - Constitution updated for Phase III AI Chatbot integration with MCP + OpenAI Agents SDK
- 🧪 Tests: N/A (constitution document, not tested)
- 📁 Files: .specify/memory/constitution.md (complete rewrite with 3 new principles and expanded sections)
- 🔁 Next prompts: /sp.specify for Phase III chatbot feature, update CLAUDE.md to emphasize MCP-first and agent integration
- 🧠 Reflection: Successfully captured all AI chatbot requirements from user input into constitutional principles. MCP-first architecture clearly defined. Stateless conversation pattern enforced. Agent behavioral rules comprehensive.

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution successfully updated with all requirements captured
- Graders run and results (PASS/FAIL): N/A (manual review recommended)
- Prompt variant (if applicable): N/A (user provided comprehensive constitution input)
- Next experiment (smallest change to try): Validate MCP Context Server accessibility before proceeding to /sp.specify

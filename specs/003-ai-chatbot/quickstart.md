# Quickstart Guide: AI Chatbot Development

**Feature**: 003-ai-chatbot
**Created**: 2026-01-15
**Audience**: Developers setting up local environment

## Overview

This guide walks you through setting up the AI-powered todo chatbot on your local machine in under 15 minutes. By the end, you'll have a fully functional chatbot that can manage tasks through natural language.

## Prerequisites

Before starting, ensure you have:

- **Python 3.13+** installed (`python --version`)
- **Node.js 18+** and npm installed (`node --version`)
- **PostgreSQL** running (local or Neon Serverless)
- **UV** package manager installed (`pip install uv`)
- **OpenAI API key** (for OpenAI Agents SDK)
- **Git** repository cloned (`git clone <repo-url>`)

## Architecture Quick Reference

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (Next.js 16 + ChatKit UI + Better Auth)      │
│  Port: 3001                                              │
└────────────────┬────────────────────────────────────────┘
                 │ POST /api/{user_id}/chat
┌────────────────▼────────────────────────────────────────┐
│  Backend (FastAPI + OpenAI Agent + MCP Server)          │
│  Port: 3000                                              │
│  - Agent: OpenAI Agents SDK                              │
│  - MCP: 5 tools (add/list/complete/delete/update)       │
└────────────────┬────────────────────────────────────────┘
                 │ SQLModel queries
┌────────────────▼────────────────────────────────────────┐
│  Database (Neon PostgreSQL)                              │
│  - users, todos (Phase II)                               │
│  - conversations, messages (Phase III - NEW)             │
└──────────────────────────────────────────────────────────┘
```

## Setup Instructions

### Step 1: Environment Variables

Create `.env` files for backend and frontend.

#### Backend `.env` (root directory)

```bash
# OpenAI API Key (required for Agents SDK)
OPENAI_API_KEY=sk-proj-...

# Database connection (Neon Serverless PostgreSQL)
DATABASE_URL=postgresql://user:password@your-neon-host/dbname

# Better Auth (existing from Phase II)
AUTH_SECRET=your-auth-secret-from-phase-2
AUTH_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

#### Frontend `.env.local` (frontend/ directory)

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:3000

# Better Auth (existing from Phase II)
BETTER_AUTH_URL=http://localhost:3000/api/auth
BETTER_AUTH_SECRET=your-auth-secret-from-phase-2
```

### Step 2: Install Backend Dependencies

```bash
# Navigate to backend directory
cd backend

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install packages
uv pip install \
  fastapi==0.115.0 \
  uvicorn[standard]==0.30.0 \
  sqlmodel==0.0.25 \
  openai-agents==0.2.9 \
  mcp==1.0.0 \
  python-dotenv==1.0.0 \
  alembic==1.13.0 \
  psycopg2-binary==2.9.9
```

### Step 3: Database Migration

Run Alembic migration to create `conversations` and `messages` tables.

```bash
# From backend/ directory
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
# Expected output: users, todos, conversations, messages
```

**Migration creates**:
- `conversations` table (id, user_id, created_at, updated_at)
- `messages` table (id, conversation_id, role, content, created_at)
- Indexes for performance (user_id, conversation_id + created_at)
- Foreign keys with cascade deletes

### Step 4: Start Backend Server

```bash
# From backend/ directory (with .venv activated)
uvicorn main:app --host 0.0.0.0 --port 3000 --reload

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:3000
# INFO:     Application startup complete
```

**Backend provides**:
- `POST /api/{user_id}/chat` - Chat endpoint
- `GET /api/health` - Health check
- `GET /api/docs` - OpenAPI documentation (Swagger UI)

**Verify backend**:
```bash
curl http://localhost:3000/api/health
# Expected: {"status": "healthy"}
```

### Step 5: Install Frontend Dependencies

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Install ChatKit UI
npm install @openai/chatkit --save
```

### Step 6: Start Frontend Development Server

```bash
# From frontend/ directory
npm run dev

# Expected output:
# ▲ Next.js 16.x.x
# - Local:   http://localhost:3001
# - Ready in X.Xs
```

**Frontend provides**:
- `/` - Home page with todo list (Phase II)
- `/chat` - AI chatbot interface (Phase III - NEW)
- `/login` - Better Auth login (Phase II)

### Step 7: Create Test User

If you don't have a test user from Phase II, create one:

```bash
# Option 1: Via frontend UI
# Navigate to http://localhost:3001/login
# Click "Sign Up" and create test user

# Option 2: Via database
psql $DATABASE_URL -c "
  INSERT INTO users (id, email, password_hash, created_at)
  VALUES (
    'test-user-123',
    'test@example.com',
    '<bcrypt-hash-of-password>',
    NOW()
  );
"
```

### Step 8: Test Chatbot

1. **Login**: Navigate to `http://localhost:3001/login` and authenticate
2. **Open Chat**: Navigate to `http://localhost:3001/chat`
3. **Send Messages**: Try these test commands:

```
User: "add a task to buy groceries tomorrow"
Expected: "Task added: Buy groceries tomorrow"

User: "show me all my tasks"
Expected: List of all tasks with status

User: "mark buy groceries as complete"
Expected: "Marked 'Buy groceries' as complete!"

User: "what is the buy groceries task for?"
Expected: Explanation based on task title/description
```

## Project Structure

After setup, your project structure should look like this:

```
todo-app/
├── backend/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── agent_config.py       # Agent initialization
│   │   └── runner.py             # Runner execution wrapper
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py             # FastMCP server setup
│   │   ├── tools/
│   │   │   ├── add_task.py       # MCP tool: add_task
│   │   │   ├── list_tasks.py     # MCP tool: list_tasks
│   │   │   ├── complete_task.py  # MCP tool: complete_task
│   │   │   ├── delete_task.py    # MCP tool: delete_task
│   │   │   └── update_task.py    # MCP tool: update_task
│   │   └── schemas.py            # Pydantic schemas
│   ├── models/
│   │   ├── conversation.py       # SQLModel: Conversation
│   │   ├── message.py            # SQLModel: Message
│   │   └── todo.py               # SQLModel: Todo (Phase II)
│   ├── api/
│   │   ├── chat.py               # POST /chat endpoint
│   │   └── todos.py              # Phase II endpoints
│   ├── services/
│   │   ├── task_service.py       # Task CRUD operations
│   │   └── conversation_service.py  # Conversation operations
│   ├── main.py                   # FastAPI app entry point
│   ├── .env                      # Environment variables
│   └── alembic/
│       └── versions/
│           └── 003_ai_chatbot.py  # Migration script
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx          # Home page (Phase II)
│   │   │   ├── chat/
│   │   │   │   └── page.tsx      # Chat page (Phase III)
│   │   │   └── login/
│   │   │       └── page.tsx      # Login page (Phase II)
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx # ChatKit UI wrapper
│   │   │   └── TodoList.tsx      # Phase II component
│   │   └── lib/
│   │       └── api.ts            # API client
│   ├── .env.local                # Frontend environment variables
│   └── package.json
├── specs/
│   └── 003-ai-chatbot/
│       ├── spec.md               # Feature specification
│       ├── plan.md               # Implementation plan
│       ├── data-model.md         # Database schema
│       ├── quickstart.md         # This file
│       └── contracts/
│           └── chat-api.yaml     # OpenAPI specification
└── README.md
```

## Development Workflow

### Making Changes

1. **Backend Changes**:
   ```bash
   # Edit code in backend/
   # Uvicorn auto-reloads on file changes
   # Check logs for errors
   ```

2. **Frontend Changes**:
   ```bash
   # Edit code in frontend/src/
   # Next.js auto-reloads on file changes
   # Check browser console for errors
   ```

3. **Database Changes**:
   ```bash
   # Create new migration
   alembic revision --autogenerate -m "Description"

   # Apply migration
   alembic upgrade head

   # Rollback if needed
   alembic downgrade -1
   ```

### Running Tests

```bash
# Backend unit tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm run test

# Integration tests (requires backend + database running)
cd backend
pytest tests/integration/ -v

# E2E tests (requires backend + frontend running)
cd frontend
npm run test:e2e
```

### Debugging

#### Backend Debugging

```bash
# View logs with verbose output
LOG_LEVEL=DEBUG uvicorn main:app --reload

# Test MCP tools directly
python -m mcp.tools.add_task --user-id "test-user-123" --title "Test task"

# Inspect database
psql $DATABASE_URL -c "SELECT * FROM conversations WHERE user_id = 'test-user-123';"
```

#### Frontend Debugging

```bash
# Enable verbose logging
NEXT_PUBLIC_LOG_LEVEL=DEBUG npm run dev

# Check network requests in browser DevTools (Network tab)
# Check console for errors (Console tab)
```

#### Agent Debugging

```python
# Add debug logging in agent_config.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Inspect agent decisions
runner.run(agent, user_input, conversation, debug=True)
```

## Common Issues and Solutions

### Issue: "OpenAI API key not found"

**Solution**: Verify `.env` has `OPENAI_API_KEY=sk-proj-...` and restart backend

```bash
# Check environment variable
echo $OPENAI_API_KEY

# Restart backend
uvicorn main:app --reload
```

### Issue: "Database connection failed"

**Solution**: Verify `DATABASE_URL` is correct and PostgreSQL is running

```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1;"

# Check Neon dashboard for connection string
```

### Issue: "403 Forbidden when sending chat message"

**Solution**: Ensure authenticated user's ID matches `user_id` in API path

```bash
# Check Better Auth session
curl http://localhost:3000/api/auth/session \
  -H "Cookie: better-auth.session_token=<your-token>"

# User ID in response must match path parameter
```

### Issue: "Chatbot not responding"

**Solution**: Check backend logs for agent errors

```bash
# View logs
tail -f backend/logs/app.log

# Common issues:
# - OpenAI API quota exceeded
# - MCP tool execution failure
# - Database timeout
```

### Issue: "Migration fails with 'table already exists'"

**Solution**: Reset Alembic state or drop tables manually

```bash
# Option 1: Mark migration as applied without running
alembic stamp head

# Option 2: Drop tables and re-run migration
psql $DATABASE_URL -c "DROP TABLE IF EXISTS messages, conversations CASCADE;"
alembic upgrade head
```

## Testing the AI Agent

### Test Natural Language Understanding

```bash
# Test intent detection
curl -X POST http://localhost:3000/api/test-user-123/chat \
  -H "Content-Type: application/json" \
  -H "Cookie: better-auth.session_token=<token>" \
  -d '{"message": "remind me to call mom"}'

# Expected: Agent detects "add task" intent
```

### Test MCP Tool Execution

```bash
# Test add_task tool
curl -X POST http://localhost:3000/api/test-user-123/chat \
  -H "Content-Type: application/json" \
  -H "Cookie: better-auth.session_token=<token>" \
  -d '{"message": "add a task to buy milk"}'

# Expected: Task created in database
psql $DATABASE_URL -c "SELECT * FROM todos WHERE user_id = 'test-user-123';"
```

### Test Conversation History

```bash
# Send first message
curl -X POST http://localhost:3000/api/test-user-123/chat \
  -d '{"message": "add a task to buy milk"}'

# Send follow-up (agent should have context)
curl -X POST http://localhost:3000/api/test-user-123/chat \
  -d '{"message": "actually, make that almond milk"}'

# Expected: Agent understands "that" refers to previous task
```

## Performance Benchmarks

Run these commands to verify performance targets:

```bash
# Test response time (should be < 3s for p95)
for i in {1..100}; do
  curl -w "%{time_total}\n" -o /dev/null -s \
    -X POST http://localhost:3000/api/test-user-123/chat \
    -d '{"message": "list my tasks"}'
done | sort -n | awk 'NR==95'

# Test concurrent users (should handle 100 users)
ab -n 1000 -c 100 -p request.json \
  -T "application/json" \
  http://localhost:3000/api/test-user-123/chat
```

## Next Steps

After completing quickstart:

1. **Read the Architecture**: Review `specs/003-ai-chatbot/plan.md` for design decisions
2. **Explore the API**: Open `http://localhost:3000/api/docs` for interactive API documentation
3. **Customize Agent**: Edit `backend/agent/agent_config.py` to modify chatbot behavior
4. **Add New MCP Tools**: Create new tools in `backend/mcp/tools/` for additional functionality
5. **Deploy to Production**: See deployment guide (TBD) for Vercel/Railway setup

## Useful Commands Reference

```bash
# Backend
uvicorn main:app --reload          # Start development server
alembic upgrade head                # Apply migrations
alembic downgrade -1                # Rollback migration
pytest tests/ -v                    # Run tests
python -m mcp.server                # Test MCP server standalone

# Frontend
npm run dev                         # Start development server
npm run build                       # Build for production
npm run test                        # Run tests
npm run lint                        # Lint code

# Database
psql $DATABASE_URL                  # Open PostgreSQL shell
alembic current                     # Show current migration
alembic history                     # Show migration history

# Git
git checkout 003-ai-chatbot         # Switch to feature branch
git status                          # Check working tree
```

## Support and Resources

- **Feature Specification**: `specs/003-ai-chatbot/spec.md`
- **Implementation Plan**: `specs/003-ai-chatbot/plan.md`
- **Database Schema**: `specs/003-ai-chatbot/data-model.md`
- **API Contract**: `specs/003-ai-chatbot/contracts/chat-api.yaml`
- **OpenAI Agents SDK Docs**: https://github.com/openai/openai-agents-python
- **MCP SDK Docs**: https://github.com/modelcontextprotocol/python-sdk
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **ChatKit UI Docs**: https://github.com/openai/chatkit

## Troubleshooting Checklist

Before asking for help, verify:

- [ ] Python 3.13+ installed and in PATH
- [ ] Node.js 18+ installed and in PATH
- [ ] PostgreSQL running and accessible
- [ ] `.env` files exist with all required variables
- [ ] OpenAI API key is valid and has quota
- [ ] Database migrations applied successfully
- [ ] Backend server running on port 3000
- [ ] Frontend server running on port 3001
- [ ] Better Auth session cookie present in requests
- [ ] No errors in backend logs (`tail -f backend/logs/app.log`)
- [ ] No errors in browser console (F12 → Console tab)

## Contributing

When making changes to the AI chatbot feature:

1. Create a new branch from `003-ai-chatbot`
2. Make changes following project constitution (`.specify/memory/constitution.md`)
3. Add tests for new functionality
4. Update documentation if needed
5. Run all tests before committing
6. Create pull request with clear description

## License

See `LICENSE` file in repository root.

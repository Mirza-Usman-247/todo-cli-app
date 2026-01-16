ID: 0005
TITLE: ai-chatbot-plan-update
STAGE: plan
DATE: 2026-01-15
SURFACE: agent
MODEL: claude-sonnet-4-5-20250929
FEATURE: 003-ai-chatbot
BRANCH: 003-ai-chatbot
USER: user
COMMAND: update plan.md and tasks.md
LABELS: ["plan", "tasks", "gemini", "deployment"]
LINKS:
  SPEC: null
  TICKET: null
  ADR: null
  PR: null
FILES:
  - specs/003-ai-chatbot/plan.md
  - specs/003-ai-chatbot/tasks.md
TESTS: []
PROMPT_TEXT: |
  Update `specs/003-ai-chatbot/plan.md` and `specs/003-ai-chatbot/tasks.md` to reflect the new requirements:
  1. Use Gemini 2.5 Flash model (via OpenAI Agents SDK adapter if needed, or compatible endpoint).
  2. Deployment: Frontend to Vercel, Backend to Railway.

  Steps:
  1. Read `specs/003-ai-chatbot/plan.md` and `specs/003-ai-chatbot/tasks.md`.
  2. Update `plan.md`:
     - Add Gemini 2.5 Flash to Tech Stack / Active Technologies.
     - Update Deployment strategy section.
  3. Update `tasks.md`:
     - Add configuration task for Gemini 2.5 Flash (API key, model name).
     - Add/Update deployment tasks for Vercel and Railway.
  4. Create a PHR for this update.
RESPONSE_TEXT: |
  Updated `specs/003-ai-chatbot/plan.md` and `specs/003-ai-chatbot/tasks.md` to incorporate Gemini 2.5 Flash and the Vercel/Railway deployment strategy.

  Key Changes:
  1.  **plan.md**:
      -   Updated Tech Stack to specify **Google Gemini 2.5 Flash** as the model.
      -   Updated Primary Dependencies to reflect the use of Gemini via OpenAI Agents SDK / adapter.
      -   Updated Target Platform to explicit **Railway (Backend)** and **Vercel (Frontend)**.
      -   Added a detailed **Deployment Strategy** section listing build commands and environment variables for both platforms.

  2.  **tasks.md**:
      -   Updated T013 to specify configuring the OpenAI Agent with **Gemini 2.5 Flash**.
      -   Renamed Phase 6 to "Phase 6: Polish, Deployment & Robustness".
      -   Added T032: Backend config for Railway (GEMINI_API_KEY, MODEL_ID, etc.).
      -   Added T033: Frontend config for Vercel (NEXT_PUBLIC_API_URL).
      -   Added T034: Deploy backend to Railway task.
      -   Added T035: Deploy frontend to Vercel task.
      -   Renumbered final task to T036.

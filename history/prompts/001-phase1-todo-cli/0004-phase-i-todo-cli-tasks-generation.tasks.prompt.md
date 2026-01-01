---
id: 0004
title: Phase I Todo CLI Tasks Generation
stage: tasks
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-phase1-todo-cli
branch: 001-phase1-todo-cli
user: Unknown User
command: /sp.tasks
labels: ["tasks", "tdd", "user-stories", "phase-1", "implementation"]
links:
  spec: specs/001-phase1-todo-cli/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-phase1-todo-cli/tasks.md
tests:
 - 18 test tasks across 5 user stories (TDD workflow)
---

## Prompt

Break the Phase-1 implementation plan into executable tasks.

Each task must:
- Be small and atomic
- Reference the Phase-1 spec section
- Be implementable independently
- Clearly state expected outcome

Output:
- Ordered task list
- No code

## Response snapshot

Generated comprehensive task breakdown with 58 atomic tasks organized by user story for Phase I CLI Todo implementation.

### Task Organization

**8 Phases** (Setup → Foundational → 5 User Stories → Polish):

1. **Phase 1: Setup** (9 tasks, T001-T009)
   - UV project initialization
   - Directory structure (src/, tests/, db/)
   - Configuration files (pyproject.toml, .python-version, README.md)
   - All __init__.py files

2. **Phase 2: Foundational** (6 tasks, T010-T015) - BLOCKS all user stories
   - Todo dataclass with validation
   - TodoService initialization
   - File I/O (load, save, backup)
   - Critical: Must complete before any user story work

3. **Phase 3: User Story 1 - Add New Todo** (P1, 7 tasks, T016-T022) 🎯 MVP
   - 3 test tasks (TDD): model validation, service, CLI integration
   - 4 implementation tasks: create_todo service method, CLI menu loop, add command handler, confirmation
   - Independent test: Add todo, restart, verify persistence

4. **Phase 4: User Story 2 - View All Todos** (P1, 7 tasks, T023-T029)
   - 3 test tasks: get_all service, view with data, view empty list
   - 4 implementation tasks: get_all_todos method, view handler, empty message, status formatting
   - Independent test: Add 3 todos, view, verify display with status indicators

5. **Phase 5: User Story 3 - Toggle Status** (P2, 7 tasks, T030-T036)
   - 3 test tasks: toggle service, toggle workflow, invalid ID handling
   - 4 implementation tasks: toggle_todo method, get_by_id helper, toggle handler, error display
   - Independent test: Create, toggle to complete, toggle back to incomplete

6. **Phase 6: User Story 4 - Update Content** (P2, 9 tasks, T037-T044)
   - 4 test tasks: partial updates service, update both, title only, description only
   - 5 implementation tasks: update_todo service, update handler, "keep current" prompts, validation
   - Independent test: Create, update title only (preserve description), verify

7. **Phase 7: User Story 5 - Delete Todo** (P3, 6 tasks, T045-T050)
   - 3 test tasks: delete service, ID not reused, delete persistence
   - 3 implementation tasks: delete_todo method, delete handler, error handling
   - Independent test: Create 5, delete #3, verify 4 remain, create new gets ID 6

8. **Phase 8: Polish** (8 tasks, T051-T058)
   - Exit handler, input validation, error handling
   - Documentation updates, full test suite, manual testing
   - Quickstart verification

### Task Breakdown by Category

| Category | Count | Task Range |
|----------|-------|------------|
| Setup | 9 | T001-T009 |
| Foundational | 6 | T010-T015 |
| Test Tasks (TDD) | 18 | Distributed across US1-US5 |
| Implementation | 25 | Distributed across US1-US5 |
| Polish | 8 | T051-T058 |
| **Total** | **58** | T001-T058 |

### User Story Task Distribution

| Story | Priority | Tests | Implementation | Total | MVP? |
|-------|----------|-------|----------------|-------|------|
| US1: Add Todo | P1 | 3 | 4 | 7 | ✅ Yes |
| US2: View All | P1 | 3 | 4 | 7 | ✅ Yes |
| US3: Toggle | P2 | 3 | 4 | 7 | No |
| US4: Update | P2 | 4 | 5 | 9 | No |
| US5: Delete | P3 | 3 | 3 | 6 | No |

### Parallel Execution Opportunities

**40 tasks** marked with [P] can run in parallel:
- Setup: 8/9 tasks (T002-T009)
- Foundational: 2/6 tasks (T010-T011)
- User Story Tests: All 18 test tasks (after foundational complete)
- Polish: 2/8 tasks (T054-T055)

**Independent User Stories**: All 5 user stories can be worked on in parallel by different team members after foundational phase completes.

### TDD Workflow Enforced

Constitution mandates TDD - tasks structured for Red-Green-Refactor:

1. **Red**: Write tests (marked "TDD - Write FIRST"), verify they fail
2. **Green**: Implement minimum code to pass tests
3. **Refactor**: Clean up (handled in polish phase)

**Example (US1)**:
- T016-T018: Write 3 tests → verify FAIL
- T019-T022: Implement → verify PASS

### MVP Strategy

**Minimum Viable Product**: US1 + US2 (14 tasks after foundational)
- Setup (9) + Foundational (6) + US1 (7) + US2 (7) = **29 tasks**
- Deliverable: Can create and view todos with persistence
- Independent validation possible at this checkpoint

### Dependencies Documented

**Phase Dependencies**:
- Setup → Foundational → User Stories → Polish
- Foundational BLOCKS all user story work (critical path)

**User Story Independence**:
- Each story creates own test data (no cross-story dependencies)
- Can deliver incrementally (MVP → +US3 → +US4 → +US5)
- Each adds value without breaking prior stories

### Checklist Format Compliance

✅ All 58 tasks follow strict format:
- `- [ ] [TaskID] [P?] [Story?] Description with file path`
- Examples:
  - `- [ ] T001 Initialize UV project with Python 3.13+ in project root`
  - `- [ ] T016 [P] [US1] Unit test for Todo model validation in tests/unit/test_todo_model.py`
  - `- [ ] T019 [US1] Implement TodoService.create_todo(title, description) in src/services/todo_service.py`

## Outcome

- ✅ Impact: 58 atomic, executable tasks ready for implementation; organized by user story for independent delivery; TDD workflow enforced with tests before implementation
- 🧪 Tests: 18 test tasks across 5 user stories (3-4 per story); covers unit (models, services) and integration (CLI workflows); validates all 17 acceptance scenarios from spec
- 📁 Files: Created tasks.md with complete task breakdown, dependency graph, parallel execution examples, MVP strategy
- 🔁 Next prompts: /sp.implement to execute tasks in TDD workflow; start with Setup + Foundational, then MVP (US1+US2)
- 🧠 Reflection: Task generation successfully decomposed plan into atomic units; each task has clear file path and outcome; user story organization enables independent testing; foundational phase correctly identified as blocker; MVP scope clear (29 tasks); parallel opportunities maximize team efficiency

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Format validation - PASS (all 58 tasks follow checklist format with TaskID, [P]/[Story] markers, file paths)
- Prompt variant (if applicable): N/A (standard task generation workflow)
- Next experiment (smallest change to try): Execute MVP tasks (T001-T029) in TDD workflow and validate independent testability of US1+US2

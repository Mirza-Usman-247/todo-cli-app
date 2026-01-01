---
description: "Task list for Phase I CLI Todo Application implementation"
---

# Tasks: Phase I CLI Todo Application

**Input**: Design documents from `/specs/001-phase1-todo-cli/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/, research.md

**Tests**: TDD approach mandated by constitution - tests are included and MUST be written BEFORE implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[TaskID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below use single project structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Initialize UV project with Python 3.13+ in project root
- [ ] T002 [P] Create src/ directory structure (models/, services/, cli/, lib/)
- [ ] T003 [P] Create tests/ directory structure (unit/, integration/)
- [ ] T004 [P] Create db/ directory for JSON storage
- [ ] T005 [P] Create pyproject.toml with pytest dependency
- [ ] T006 [P] Create .python-version file specifying Python 3.13
- [ ] T007 [P] Create README.md with installation and usage instructions
- [ ] T008 [P] Create __init__.py files in src/, src/models/, src/services/, src/cli/
- [ ] T009 [P] Create __init__.py files in tests/, tests/unit/, tests/integration/

**Checkpoint**: Project structure ready - foundational work can begin

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T010 [P] Implement Todo dataclass in src/models/todo.py with all fields (id, title, description, completed, created_at, updated_at)
- [ ] T011 [P] Add validation in Todo.__post_init__ for title non-empty and length limits (500 title, 2000 description)
- [ ] T012 Implement TodoService.__init__ in src/services/todo_service.py with file_path, todos list, next_id attributes
- [ ] T013 Implement TodoService.load() method to read /db/todos.json with corruption handling and timestamped backup creation
- [ ] T014 Implement TodoService.save() method with atomic file write (temp file + rename)
- [ ] T015 Implement TodoService._create_timestamped_backup() helper method for corrupted file recovery

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add New Todo (Priority: P1) 🎯 MVP

**Goal**: Users can create todos with title and description, see them persist after restart

**Independent Test**: Launch app, add todo with title "Buy groceries" and description "Milk, eggs, bread", restart app, verify todo still exists with ID 1 and status incomplete

### Tests for User Story 1 (TDD - Write FIRST)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T016 [P] [US1] Unit test for Todo model validation (empty title rejection, length limits) in tests/unit/test_todo_model.py
- [ ] T017 [P] [US1] Unit test for TodoService.create_todo() in tests/unit/test_todo_service.py
- [ ] T018 [P] [US1] Integration test for "add todo" CLI workflow in tests/integration/test_cli_integration.py

### Implementation for User Story 1

- [ ] T019 [US1] Implement TodoService.create_todo(title, description) method with validation, ID assignment, timestamp generation in src/services/todo_service.py
- [ ] T020 [US1] Implement CLI main menu loop in src/cli/main.py with options 1-6 displayed
- [ ] T021 [US1] Implement "Add Todo" command handler (option 1) in src/cli/main.py with title/description prompts and validation error display
- [ ] T022 [US1] Add confirmation message display after successful todo creation in src/cli/main.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - View All Todos (Priority: P1)

**Goal**: Users can see all their todos with status indicators, or empty message if none exist

**Independent Test**: Add 3 todos (2 incomplete, 1 complete using toggle from US3), view list, verify all display with correct status symbols (✓/✗), IDs, titles, descriptions

### Tests for User Story 2 (TDD - Write FIRST)

- [ ] T023 [P] [US2] Unit test for TodoService.get_all_todos() in tests/unit/test_todo_service.py
- [ ] T024 [P] [US2] Integration test for "view all" with multiple todos in tests/integration/test_cli_integration.py
- [ ] T025 [P] [US2] Integration test for "view all" with empty list in tests/integration/test_cli_integration.py

### Implementation for User Story 2

- [ ] T026 [US2] Implement TodoService.get_all_todos() method returning list of all todos in src/services/todo_service.py
- [ ] T027 [US2] Implement "View All Todos" command handler (option 2) in src/cli/main.py with formatted display
- [ ] T028 [US2] Add empty list message ("No todos found. Create one with option 1!") in src/cli/main.py
- [ ] T029 [US2] Add status indicator formatting (✓ for complete, ✗ for incomplete) in src/cli/main.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Toggle Todo Status (Priority: P2)

**Goal**: Users can flip completion status of todos (incomplete ↔ complete)

**Independent Test**: Create todo, toggle status to complete, verify status changes and displays ✓, toggle again, verify returns to incomplete with ✗

### Tests for User Story 3 (TDD - Write FIRST)

- [ ] T030 [P] [US3] Unit test for TodoService.toggle_todo(id) in tests/unit/test_todo_service.py
- [ ] T031 [P] [US3] Integration test for toggle workflow (incomplete → complete → incomplete) in tests/integration/test_cli_integration.py
- [ ] T032 [P] [US3] Unit test for invalid ID error handling in tests/unit/test_todo_service.py

### Implementation for User Story 3

- [ ] T033 [US3] Implement TodoService.toggle_todo(id) method that flips completed status and updates updated_at in src/services/todo_service.py
- [ ] T034 [US3] Implement TodoService.get_todo_by_id(id) helper method with KeyError on not found in src/services/todo_service.py
- [ ] T035 [US3] Implement "Toggle Status" command handler (option 3) in src/cli/main.py with ID prompt and confirmation
- [ ] T036 [US3] Add error handling for invalid ID with user-friendly message in src/cli/main.py

**Checkpoint**: All three priority-1 and priority-2 stories should now be independently functional

---

## Phase 6: User Story 4 - Update Todo Content (Priority: P2)

**Goal**: Users can modify title and/or description of existing todos (partial updates supported)

**Independent Test**: Create todo, update only title (press Enter for description), verify title changed and description preserved, then update only description, verify both fields correct

### Tests for User Story 4 (TDD - Write FIRST)

- [ ] T037 [P] [US4] Unit test for TodoService.update_todo(id, title, description) with partial updates in tests/unit/test_todo_service.py
- [ ] T038 [P] [US4] Integration test for update both fields in tests/integration/test_cli_integration.py
- [ ] T039 [P] [US4] Integration test for partial update (title only) in tests/integration/test_cli_integration.py
- [ ] T040 [P] [US4] Integration test for partial update (description only) in tests/integration/test_cli_integration.py

### Implementation for User Story 4

- [ ] T041 [US4] Implement TodoService.update_todo(id, new_title=None, new_description=None) with partial update logic in src/services/todo_service.py
- [ ] T042 [US4] Implement "Update Todo" command handler (option 4) in src/cli/main.py with current value display
- [ ] T043 [US4] Add "press Enter to keep current" prompts for title and description in src/cli/main.py
- [ ] T044 [US4] Add validation for updated title/description lengths with error messages in src/cli/main.py

**Checkpoint**: All P1 and P2 user stories should be independently functional

---

## Phase 7: User Story 5 - Delete Todo (Priority: P3)

**Goal**: Users can permanently remove todos from list (ID never reused)

**Independent Test**: Create 5 todos, delete ID 3, verify only 4 remain and ID 3 not in list, create new todo, verify it gets ID 6 (not 3)

### Tests for User Story 5 (TDD - Write FIRST)

- [ ] T045 [P] [US5] Unit test for TodoService.delete_todo(id) in tests/unit/test_todo_service.py
- [ ] T046 [P] [US5] Unit test verifying ID not reused after deletion in tests/unit/test_todo_service.py
- [ ] T047 [P] [US5] Integration test for delete and persistence in tests/integration/test_cli_integration.py

### Implementation for User Story 5

- [ ] T048 [US5] Implement TodoService.delete_todo(id) method removing todo from list in src/services/todo_service.py
- [ ] T049 [US5] Implement "Delete Todo" command handler (option 5) in src/cli/main.py with ID prompt and confirmation
- [ ] T050 [US5] Add error handling for invalid ID during deletion in src/cli/main.py

**Checkpoint**: All user stories (P1, P2, P3) should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T051 Implement "Exit" command handler (option 6) with goodbye message in src/cli/main.py
- [ ] T052 Add input validation for menu option selection (1-6 only) in src/cli/main.py
- [ ] T053 Add error handling for non-numeric ID inputs with user-friendly message in src/cli/main.py
- [ ] T054 [P] Add comprehensive file I/O error handling (permissions, disk full) in src/services/todo_service.py
- [ ] T055 [P] Update README.md with actual usage examples and troubleshooting section
- [ ] T056 Run full test suite (pytest) and verify all 17+ acceptance scenarios pass
- [ ] T057 Manual testing of edge cases: corrupted JSON, long inputs, rapid operations
- [ ] T058 Verify quickstart.md instructions work end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (displays empty list if US1 not done)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Works independently (needs existing todo to toggle, but can create in same test)
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Works independently (needs existing todo to update, but can create in same test)
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Works independently (needs existing todo to delete, but can create in same test)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Service methods before CLI handlers
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002-T009)
- All Foundational tasks marked [P] can run in parallel (T010-T011)
- Once Foundational phase completes, all user story test tasks can start in parallel
- All tests for a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task T016: "Unit test for Todo model validation in tests/unit/test_todo_model.py"
Task T017: "Unit test for TodoService.create_todo() in tests/unit/test_todo_service.py"
Task T018: "Integration test for add todo CLI workflow in tests/integration/test_cli_integration.py"

# After tests fail, implement in sequence:
Task T019: "Implement TodoService.create_todo() in src/services/todo_service.py"
Task T020: "Implement CLI main menu loop in src/cli/main.py"
Task T021: "Implement Add Todo command handler in src/cli/main.py"
Task T022: "Add confirmation message in src/cli/main.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only)

1. Complete Phase 1: Setup (T001-T009)
2. Complete Phase 2: Foundational (T010-T015) - CRITICAL
3. Complete Phase 3: User Story 1 (T016-T022)
4. Complete Phase 4: User Story 2 (T023-T029)
5. **STOP and VALIDATE**: Test independently - can add and view todos
6. Deploy/demo if ready

**MVP Deliverable**: Working todo app that can create and display todos

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 + 2 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 3 → Test independently → Deploy/Demo (can now mark complete)
4. Add User Story 4 → Test independently → Deploy/Demo (can now edit)
5. Add User Story 5 → Test independently → Deploy/Demo (can now delete)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T015)
2. Once Foundational is done:
   - Developer A: User Story 1 (T016-T022)
   - Developer B: User Story 2 (T023-T029)
   - Developer C: User Story 3 (T030-T036)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD MANDATORY**: Verify tests fail (Red) before implementing (Green)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All tasks reference exact file paths per plan.md structure
- Total: 58 tasks (9 setup, 6 foundational, 43 user story implementation/tests, 8 polish)

# Implementation Plan: Phase I CLI Todo Application

**Branch**: `001-phase1-todo-cli` | **Date**: 2026-01-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phase1-todo-cli/spec.md`

## Summary

Deliver a command-line todo application with full CRUD operations (create, read, update, delete, toggle status) using file-backed in-memory storage. The application loads todos from `/db/todos.json` on startup, maintains them in memory during execution, and persists all changes back to the JSON file. Implementation follows strict separation of concerns with models, services, and CLI layers, using only Python 3.13+ standard library.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: Python standard library only (json, pathlib, datetime); UV for environment management
**Storage**: File-based JSON (`/db/todos.json`)
**Testing**: pytest
**Target Platform**: Console/terminal (Linux, macOS, Windows)
**Project Type**: Single project (CLI application)
**Performance Goals**: <1 second response time for operations with <1000 todos; <2 seconds startup time
**Constraints**: No external databases; no web/API interfaces; Python standard library only (exception: pytest for testing)
**Scale/Scope**: Support minimum 1000 todos without degradation; title max 500 chars, description max 2000 chars

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Spec-Driven Development (SDD) Mandate
- ✅ **PASS**: Feature has spec.md with user stories, functional requirements, and acceptance criteria
- ✅ **PASS**: This plan.md being generated from spec
- ✅ **PASS**: tasks.md will be generated next via `/sp.tasks`

### II. Phase-Scoped Development
- ✅ **PASS**: Scope limited to CLI-based CRUD operations
- ✅ **PASS**: No web/API interfaces planned
- ✅ **PASS**: No authentication or multi-user features
- ✅ **PASS**: No cloud storage or external databases
- ✅ **PASS**: All features within Phase I boundary (add, view, update, delete, toggle status)

### III. Test-First Development (TDD)
- ✅ **PASS**: pytest chosen for test framework
- ✅ **PASS**: tasks.md will include test tasks BEFORE implementation tasks
- ✅ **PASS**: All 17 acceptance scenarios from spec.md will have corresponding tests

### IV. Minimal Viable Simplicity
- ✅ **PASS**: No unnecessary abstractions (direct file I/O via json module, no ORM)
- ✅ **PASS**: No repository pattern (simple service layer with direct JSON persistence)
- ✅ **PASS**: No dependency injection framework
- ✅ **PASS**: Standard library only (except pytest for testing)
- ✅ **PASS**: No future-proofing beyond Phase I requirements

### V. File-Backed In-Memory Architecture
- ✅ **PASS**: Load `/db/todos.json` into memory on startup
- ✅ **PASS**: Modify in-memory list during user operations
- ✅ **PASS**: Persist to `/db/todos.json` after every change
- ✅ **PASS**: File I/O encapsulated in service layer (not models or CLI)

### VI. Separation of Concerns
- ✅ **PASS**: Three-layer architecture planned:
  - `src/models/todo.py` - Data structures (dataclass)
  - `src/services/todo_service.py` - Business logic, file I/O
  - `src/cli/main.py` - User interface, menu, input/output
- ✅ **PASS**: Models contain no I/O logic
- ✅ **PASS**: Services do not import CLI modules
- ✅ **PASS**: CLI does not perform file I/O directly

**Constitution Check Result**: ✅ ALL GATES PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/001-phase1-todo-cli/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (/sp.plan output)
├── research.md          # Phase 0 output (technical research)
├── data-model.md        # Phase 1 output (entity definitions)
├── quickstart.md        # Phase 1 output (usage guide)
├── contracts/           # Phase 1 output (CLI command contracts)
│   └── cli-commands.md  # Command specifications
└── checklists/
    └── requirements.md  # Spec quality checklist (complete)
```

### Source Code (repository root)

```text
/
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── todo.py          # Todo dataclass
│   ├── services/
│   │   ├── __init__.py
│   │   └── todo_service.py  # CRUD operations, file I/O, validation
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py          # Menu loop, user input/output
│   └── lib/                 # (Optional: shared utilities if needed)
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_todo_model.py
│   │   └── test_todo_service.py
│   └── integration/
│       ├── __init__.py
│       └── test_cli_integration.py
├── db/
│   └── todos.json           # Created on first run
├── pyproject.toml           # UV project configuration
├── README.md
└── .python-version          # Specifies Python 3.13+
```

**Structure Decision**: Single project structure selected (Option 1 from template). This is a standalone CLI application with no web/mobile components. The structure follows the constitution's separation of concerns mandate with distinct models/, services/, and cli/ directories. The db/ directory will be created automatically on first run if missing (per NFR-007).

## Complexity Tracking

> **No violations detected** - Constitution Check passed all gates without exceptions. No complexity justifications required.

---

## Phase 0: Research & Technical Decisions

### Research Questions

All technical decisions are clear from spec and constitution:

1. **JSON Schema Structure** - Defined in spec.md Data Model section
2. **Error Handling Strategy** - Defined in spec.md File-Based Persistence Strategy
3. **CLI Menu Design** - Defined in spec.md CLI Interaction Behavior
4. **Validation Rules** - Defined in spec.md Functional Requirements (FR-012, FR-013)
5. **Testing Approach** - Defined in constitution (TDD mandatory, pytest framework)

### Technical Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| **Python dataclass for Todo model** | Built-in, type-safe, minimal boilerplate; supports validation via `__post_init__` | NamedTuple (immutable, harder to update), dict (no type safety), Pydantic (external dependency) |
| **Standard library `json` module** | Phase I requirement (standard library only); adequate for simple persistence | Third-party JSON libraries (violates constitution), pickle (not human-readable) |
| **Interactive menu loop** | Spec requires menu-driven interface (numbered commands); better UX than command-line args for multiple operations | Click/argparse (command-line args style - less intuitive for interactive session), curses (over-engineered for Phase I) |
| **List[dict] in-memory storage** | Simple, direct mapping to JSON format; easy serialization | Custom collection classes (unnecessary abstraction), SQLite in-memory (external database violates constitution) |
| **pytest for testing** | Industry standard, clean syntax, good discovery; only external dependency allowed | unittest (standard library - acceptable alternative), nose2 (less maintained) |
| **pathlib.Path for file operations** | Modern, cross-platform, Pythonic API; part of standard library | os.path (legacy, less readable), open() directly (less robust path handling) |

### Best Practices Applied

1. **Atomic File Writes**: Write to temporary file, then rename to ensure data integrity (prevents partial writes on crash)
2. **ISO 8601 Timestamps**: Use `datetime.now(timezone.utc).isoformat()` for created_at/updated_at (spec requirement)
3. **Input Validation**: Validate title/description length limits (500/2000 chars) before creating/updating todos (FR-013)
4. **Timestamped Backups**: Corrupted JSON files backed up with format `todos.json.backup.YYYY-MM-DD-HHMMSS` (FR-016)
5. **Type Hints**: Use throughout for better IDE support and error detection (Python 3.13+ feature)
6. **Error Messages**: User-friendly messages with specific guidance (e.g., "Title exceeds 500 character limit" not "Invalid input")

---

## Phase 1: Data Model & Contracts

### Entity: Todo

See `data-model.md` for complete entity definitions.

**Core Fields**:
- `id: int` - Auto-increment, starts at 1, never reused
- `title: str` - Required, non-empty, max 500 chars
- `description: str` - Optional, max 2000 chars
- `completed: bool` - Default False
- `created_at: str` - ISO 8601 timestamp
- `updated_at: str` - ISO 8601 timestamp

**Validation Rules** (enforced in service layer):
- Title: Non-empty after strip(), max 500 chars
- Description: Max 2000 chars (empty string allowed)
- ID: Positive integer, unique
- Timestamps: ISO 8601 format

**State Transitions**:
- Create: completed = False
- Toggle: completed = not completed
- Update: only title/description change; updated_at refreshed
- Delete: removed from list

### CLI Command Contracts

See `contracts/cli-commands.md` for complete command specifications.

**Menu Options** (interactive, numbered 1-6):
1. Add Todo → prompt title, prompt description, create todo, show confirmation
2. View All → display formatted list with IDs and status indicators
3. Toggle Status → prompt ID, flip completed status, show confirmation
4. Update Todo → prompt ID, prompt fields to update (partial allowed), show confirmation
5. Delete Todo → prompt ID, remove from list, show confirmation
6. Exit → persist and quit

**Data Flow**:
```
CLI (main.py) → TodoService (todo_service.py) → In-Memory List → JSON File (todos.json)
      ↑                                               ↓
      └────────────── Load on startup ────────────────┘
```

### Quickstart Guide

See `quickstart.md` for user-facing usage instructions.

**Installation**:
```bash
uv sync
```

**Run**:
```bash
uv run python -m src.cli.main
```

**Example Session**:
```
=== Todo CLI ===
1. Add Todo
2. View All Todos
3. Toggle Status
4. Update Todo
5. Delete Todo
6. Exit

Choose option: 1
Enter title: Buy groceries
Enter description (optional): Milk, eggs, bread
✓ Todo #1 created: Buy groceries
```

---

## Implementation Phases (for `/sp.tasks`)

### Phase 1: Setup
- Initialize UV project with Python 3.13+
- Create directory structure (src/, tests/, db/)
- Configure pyproject.toml

### Phase 2: Models
- Implement Todo dataclass with validation
- Unit tests for Todo model

### Phase 3: Services
- Implement TodoService with file I/O
- Implement CRUD operations
- Implement backup on corruption
- Unit tests for TodoService

### Phase 4: CLI
- Implement interactive menu loop
- Implement user input/output for all operations
- Integration tests for full workflows

### Phase 5: Validation
- Run all tests
- Verify acceptance criteria from spec.md
- Manual testing of edge cases

---

## Next Steps

1. **Generate tasks.md**: Run `/sp.tasks` to break down implementation into atomic, testable tasks
2. **Implement via TDD**: Follow Red-Green-Refactor cycle for each task
3. **Validate**: Ensure all 17 acceptance scenarios pass
4. **Document**: Update quickstart.md with actual usage after implementation

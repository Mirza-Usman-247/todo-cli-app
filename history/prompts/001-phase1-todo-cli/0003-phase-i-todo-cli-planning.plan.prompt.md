---
id: 0003
title: Phase I Todo CLI Planning
stage: plan
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-phase1-todo-cli
branch: 001-phase1-todo-cli
user: Unknown User
command: /sp.plan
labels: ["plan", "architecture", "phase-1", "constitution-check", "tdd"]
links:
  spec: specs/001-phase1-todo-cli/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-phase1-todo-cli/plan.md
 - specs/001-phase1-todo-cli/research.md
 - specs/001-phase1-todo-cli/data-model.md
 - specs/001-phase1-todo-cli/quickstart.md
 - specs/001-phase1-todo-cli/contracts/cli-commands.md
 - CLAUDE.md
tests:
 - N/A (planning phase, test strategy defined for implementation)
---

## Prompt

Generate an implementation plan for Phase-1 Todo CLI app
based strictly on the Phase-1 spec.

The plan must include:
- Project folder structure
- Module responsibilities
- Data flow (CLI → Service → Memory → File)
- Step-by-step execution order
- Files to be created

Do NOT write code.
Do NOT skip steps.
Output must be concise and actionable.

## Response snapshot

Generated comprehensive implementation plan with full constitution compliance check and Phase 0/Phase 1 design artifacts.

### Constitution Check Results

**All 6 Principles: ✅ PASS**

1. **SDD Mandate**: Spec.md complete, plan.md generated, tasks.md next
2. **Phase-Scoped Development**: CLI-only, no web/API/auth/cloud
3. **Test-First Development (TDD)**: pytest chosen, tests before implementation
4. **Minimal Viable Simplicity**: No abstractions, standard library only, no patterns
5. **File-Backed In-Memory Architecture**: Load JSON on startup, persist after every change
6. **Separation of Concerns**: 3-layer (models/ services/ cli/)

**Result**: No violations, no complexity tracking needed

### Project Structure Defined

**Source Code** (single project pattern):
```
src/
├── models/todo.py          # Todo dataclass
├── services/todo_service.py # CRUD + file I/O
└── cli/main.py             # Interactive menu

tests/
├── unit/                   # test_todo_model.py, test_todo_service.py
└── integration/            # test_cli_integration.py

db/todos.json               # Created on first run
```

**Documentation Artifacts Generated**:
- `plan.md` - Full implementation plan with technical context, constitution check, phases
- `research.md` - Technical decisions (dataclass, json module, menu loop, ISO 8601 timestamps)
- `data-model.md` - Todo entity schema, validation rules, state transitions, storage format
- `contracts/cli-commands.md` - 6 menu commands with inputs/outputs/error handling
- `quickstart.md` - Installation, usage examples, troubleshooting

### Technical Decisions (from research.md)

| Decision | Chosen Technology | Rationale |
|----------|-------------------|-----------|
| Data Model | `@dataclass` | Type-safe, minimal boilerplate, supports `__post_init__` validation |
| JSON I/O | `json` module + atomic writes | Standard library, temp file + rename for atomicity |
| CLI | Interactive menu loop | Spec requirement, better UX for multiple operations |
| Timestamps | ISO 8601 via `datetime` | Spec requirement, UTC avoids timezone issues |
| Testing | pytest | Industry standard, only external dependency allowed |
| File Ops | `pathlib.Path` | Modern, cross-platform, standard library |

### Data Flow Architecture

```
CLI (main.py) → TodoService (todo_service.py) → In-Memory List[Todo] → /db/todos.json
      ↑                                                ↓
      └────────────────── Load on startup ────────────┘
```

**Separation enforced**:
- Models: Pure data structures, no I/O
- Services: Business logic, file I/O, validation
- CLI: User interaction, input/output, error display

### Implementation Phases

1. **Setup**: UV project init, directory structure, pyproject.toml
2. **Models**: Todo dataclass with validation, unit tests
3. **Services**: TodoService with CRUD + file I/O, backup on corruption, unit tests
4. **CLI**: Interactive menu loop, all 6 commands, integration tests
5. **Validation**: Run all tests, verify 17 acceptance scenarios

### Performance & Constraints

- <1 second response time (<1000 todos)
- <2 seconds startup time
- Title max 500 chars, description max 2000 chars
- Support minimum 1000 todos without degradation
- Python 3.13+ standard library only (exception: pytest)

## Outcome

- ✅ Impact: Complete implementation plan ready for task generation; constitution validated (all gates pass); technical architecture defined with clear separation of concerns
- 🧪 Tests: Test strategy defined (pytest, TDD workflow, 17 acceptance scenarios from spec)
- 📁 Files: Created plan.md, research.md, data-model.md, quickstart.md, contracts/cli-commands.md; updated CLAUDE.md with active technologies
- 🔁 Next prompts: /sp.tasks to generate atomic, dependency-ordered implementation tasks
- 🧠 Reflection: Planning successfully bridges spec → implementation; all technical decisions justified and aligned with constitution; no scope creep (rejected web/API/auth); data flow clearly defined (CLI → Service → Memory → File); backup strategy ensures data safety

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution Check - PASS (all 6 principles verified, no violations)
- Prompt variant (if applicable): N/A (standard planning workflow)
- Next experiment (smallest change to try): Run /sp.tasks to validate that architecture translates cleanly into testable, atomic tasks with correct dependency ordering

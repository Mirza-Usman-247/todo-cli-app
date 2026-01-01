<!--
Sync Impact Report (2026-01-01)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Version Change: New constitution → 1.0.0
Rationale: Initial ratification for Phase I of "The Evolution of Todo" project

New Principles Added:
  - I. Spec-Driven Development (SDD) Mandate
  - II. Phase-Scoped Development
  - III. Test-First Development (TDD)
  - IV. Minimal Viable Simplicity
  - V. File-Backed In-Memory Architecture
  - VI. Separation of Concerns

New Sections Added:
  - Phase I Technical Constraints
  - Development Workflow
  - Governance

Templates Status:
  ✅ .specify/templates/plan-template.md - Constitution Check section verified
  ✅ .specify/templates/spec-template.md - Requirements alignment verified
  ✅ .specify/templates/tasks-template.md - Task categorization verified
  ⚠ Commands under .claude/commands/ - Agent-specific, no updates required

Follow-up TODOs: None
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-->

# The Evolution of Todo - Phase I Constitution

## Core Principles

### I. Spec-Driven Development (SDD) Mandate

All development MUST follow the Agentic Dev Stack workflow:

1. Write specification using `/sp.specify`
2. Generate implementation plan using `/sp.plan`
3. Break into actionable tasks using `/sp.tasks`
4. Implement via Claude Code following generated artifacts

**Rationale**: Ensures every code change is traceable to documented requirements, preventing scope creep and maintaining alignment with project goals.

**Non-negotiable rules**:
- NEVER write code without a corresponding spec
- NEVER skip planning or task generation steps
- STOP immediately if requirements are unclear and request clarification
- Every feature MUST have artifacts in `/specs/<feature>/` (spec.md, plan.md, tasks.md)

### II. Phase-Scoped Development

Phase I scope is strictly limited to a CLI-based, in-memory Todo application.

**In Scope**:
- Add todo (title + description)
- View todos with status indicators
- Update todo
- Delete todo by ID
- Mark todo complete/incomplete

**Out of Scope** (Failure conditions):
- Web interfaces or REST APIs
- Authentication or multi-user features
- Cloud storage or remote databases
- AI-powered features
- Mobile applications
- Any Phase II+ functionality

**Rationale**: Constraining scope to Phase I prevents premature optimization and ensures a working, testable foundation before expanding.

**Non-negotiable rules**:
- REJECT any implementation request that introduces out-of-scope features
- DOCUMENT scope violations if discovered during implementation
- REQUEST clarification if a requirement could expand beyond Phase I

### III. Test-First Development (TDD)

Test-Driven Development is MANDATORY for all feature implementation.

**Red-Green-Refactor cycle**:
1. **Red**: Write tests that fail (verify failure)
2. **Green**: Implement minimum code to pass tests
3. **Refactor**: Clean up while keeping tests green

**Rationale**: TDD ensures code correctness, prevents regressions, and serves as living documentation.

**Non-negotiable rules**:
- Tests MUST be written BEFORE implementation code
- Tests MUST fail initially (verify red state)
- Implementation proceeds ONLY after test approval
- ALL acceptance criteria MUST have corresponding tests

### IV. Minimal Viable Simplicity

Start with the simplest solution. Complexity requires explicit justification.

**YAGNI (You Aren't Gonna Need It) principles**:
- No abstractions for single use cases
- No architectural patterns without proven need
- No "future-proofing" beyond Phase I requirements
- No external dependencies unless absolutely necessary

**Rationale**: Premature abstraction creates maintenance burden and obscures intent. Simple code is easier to test, understand, and modify.

**Non-negotiable rules**:
- JUSTIFY any abstraction (repository pattern, dependency injection, etc.)
- REJECT unnecessary design patterns
- PREFER inline code over premature extraction
- DOCUMENT complexity violations in plan.md Complexity Tracking table

### V. File-Backed In-Memory Architecture

Todos are stored in `/db/todos.json` and loaded into memory on application startup.

**Data flow**:
- Application startup → Load `/db/todos.json` into memory
- User operation → Modify in-memory data structure
- After every change → Persist to `/db/todos.json`

**Rationale**: Provides persistence without database complexity, suitable for Phase I scope.

**Non-negotiable rules**:
- NO external database systems (PostgreSQL, SQLite, MongoDB, etc.)
- ALL todos MUST persist to `/db/todos.json`
- File I/O MUST be encapsulated in service layer
- Handle file read/write errors gracefully

### VI. Separation of Concerns

Clean architecture with distinct layers:

**Required structure**:
```
src/
├── models/      # Data structures (Todo class/dataclass)
├── services/    # Business logic, persistence
├── cli/         # User interface, command parsing
└── lib/         # Shared utilities (if needed)
```

**Rationale**: Separation enables testing, maintainability, and future refactoring.

**Non-negotiable rules**:
- Models MUST NOT contain business logic or I/O
- Services MUST NOT import CLI modules
- CLI MUST NOT perform file I/O directly
- Each layer has clear, testable responsibilities

## Phase I Technical Constraints

### Language & Environment

- **Python Version**: 3.13+ (REQUIRED)
- **Package Manager**: UV (REQUIRED)
- **Dependency Policy**: Minimize external dependencies; prefer standard library

### User Interface

- **Interface Type**: Console (CLI) based
- **Output Format**: Simple, readable, user-friendly text
- **Input Method**: Command-line arguments or interactive prompts
- **Status Indicators**: Clear visual representation (✓/✗, [Complete]/[Pending], etc.)

### Data Storage

- **Storage Location**: `/db/todos.json`
- **Format**: JSON
- **Loading Strategy**: Load into memory on startup
- **Persistence Strategy**: Write to disk after every modification

### Testing Requirements

- **Framework**: pytest (or standard library unittest if no dependencies preferred)
- **Coverage**: All core functionality (CRUD operations)
- **Test Types**: Unit tests (models, services), integration tests (CLI + service)
- **Validation**: Tests MUST pass before considering task complete

## Development Workflow

### 1. Feature Initiation

```bash
/sp.specify <feature-description>
```

**Output**: `/specs/<feature>/spec.md` with:
- User stories (prioritized P1, P2, P3)
- Acceptance scenarios (Given/When/Then)
- Functional requirements (FR-001, FR-002, etc.)
- Success criteria

### 2. Planning

```bash
/sp.plan
```

**Output**: `/specs/<feature>/plan.md` with:
- Technical context (Python 3.13, UV, pytest)
- Constitution check (validates compliance)
- Project structure (src/, tests/, db/)
- Complexity justifications (if any violations)

### 3. Task Breakdown

```bash
/sp.tasks
```

**Output**: `/specs/<feature>/tasks.md` with:
- Setup tasks (project initialization)
- Foundational tasks (shared infrastructure)
- User story tasks (grouped by priority)
- Test tasks (TDD: written first, fail, then implement)

### 4. Implementation

```bash
/sp.implement
```

**Process**:
- Execute tasks in dependency order
- Write tests → Verify failure → Implement → Verify pass
- Commit after each logical task or group
- Create PHR (Prompt History Record) after implementation

### 5. Quality Gates

**Before considering feature complete**:
- ✅ All tests pass
- ✅ Spec acceptance criteria satisfied
- ✅ No constitution violations (or documented in Complexity Tracking)
- ✅ Code follows separation of concerns
- ✅ PHR created in `history/prompts/<feature>/`

## Governance

### Constitution Authority

This constitution supersedes all other development practices. When conflicts arise:

1. Constitution principles override convenience
2. Phase I scope overrides feature requests
3. Simplicity overrides architectural patterns

### Amendment Process

1. Propose change with rationale
2. Document impact on existing code
3. Update constitution version:
   - **MAJOR**: Backward-incompatible principle changes
   - **MINOR**: New principles or expanded guidance
   - **PATCH**: Clarifications, typo fixes, non-semantic refinements
4. Update dependent templates (plan, spec, tasks)
5. Create migration plan for existing code (if needed)
6. Obtain approval before finalizing

### Compliance Verification

**Every PR/feature MUST**:
- Reference constitution principles in plan.md Constitution Check
- Justify any complexity or deviations in Complexity Tracking table
- Pass all tests (TDD compliance)
- Maintain separation of concerns

**Violations require**:
- Documented justification
- Exploration of simpler alternatives
- Explicit approval before proceeding

### Runtime Guidance

See `CLAUDE.md` for Claude Code-specific development instructions, including:
- PHR creation workflow
- ADR suggestion criteria
- MCP tool usage
- Human-as-Tool invocation triggers

**Version**: 1.0.0 | **Ratified**: 2026-01-01 | **Last Amended**: 2026-01-01

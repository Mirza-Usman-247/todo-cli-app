# Research: Phase I CLI Todo Application

**Feature**: 001-phase1-todo-cli
**Date**: 2026-01-01
**Status**: Complete

## Overview

This document captures technical research and decisions for implementing the Phase I CLI Todo application. All decisions align with the project constitution and Phase I scope constraints.

## Research Areas

### 1. Python Data Structures for Todo Model

**Question**: What's the best way to represent a Todo in Python 3.13+ using only standard library?

**Options Evaluated**:
- `dataclass` (chosen)
- `NamedTuple`
- Plain `dict`
- Custom class with `__init__`

**Decision**: Use `@dataclass` from Python standard library

**Rationale**:
- Type-safe with built-in type hints support
- Minimal boilerplate compared to custom classes
- Supports `__post_init__` for validation logic
- Automatic `__repr__`, `__eq__` methods
- Mutable (allows updates unlike NamedTuple)
- Clean serialization to dict via `asdict()` for JSON conversion

**Example**:
```python
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

@dataclass
class Todo:
    id: int
    title: str
    description: str
    completed: bool
    created_at: str
    updated_at: str

    def __post_init__(self):
        # Validation logic here
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
```

### 2. JSON File I/O Strategy

**Question**: How to safely read/write JSON files with corruption handling?

**Decision**: Use `json.load/dump` with atomic writes via temp file + rename

**Rationale**:
- `json` module is standard library (meets constitution requirement)
- Atomic writes prevent partial file corruption on crash
- Temp file + rename is POSIX atomic operation
- Easy corruption detection via `json.JSONDecodeError`

**Implementation Pattern**:
```python
import json
from pathlib import Path
import tempfile

# Read
try:
    with open(file_path, 'r') as f:
        data = json.load(f)
except json.JSONDecodeError:
    # Create backup and start fresh
    backup_path = create_timestamped_backup(file_path)
    data = {"todos": [], "next_id": 1}

# Atomic Write
tmp_fd, tmp_path = tempfile.mkstemp(dir=file_path.parent, suffix='.tmp')
try:
    with os.fdopen(tmp_fd, 'w') as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, file_path)  # Atomic on POSIX
except Exception:
    os.unlink(tmp_path)
    raise
```

### 3. CLI Menu Implementation

**Question**: Interactive menu loop vs argument-based CLI?

**Decision**: Interactive menu loop with numbered options

**Rationale**:
- Spec explicitly requires "menu-driven interface"
- Better UX for multiple operations in single session
- Simpler than parsing complex command-line arguments
- Natural fit for CRUD workflow (users perform multiple actions)

**Alternatives Rejected**:
- `argparse`: Better for single-command tools, requires re-running for each action
- `click`: External dependency (violates constitution)
- `curses`: Over-engineered for simple menu; cross-platform issues on Windows

**Implementation Pattern**:
```python
while True:
    print("\n=== Todo CLI ===")
    print("1. Add Todo")
    print("2. View All Todos")
    # ...
    print("6. Exit")

    choice = input("\nChoose option: ").strip()

    if choice == '1':
        handle_add_todo()
    elif choice == '6':
        break
    else:
        print("Invalid option")
```

### 4. Timestamp Format

**Question**: What timestamp format should be used?

**Decision**: ISO 8601 format via `datetime.now(timezone.utc).isoformat()`

**Rationale**:
- Spec explicitly requires ISO 8601 (see Key Entities in spec.md)
- Standard library `datetime` module supports this
- UTC avoids timezone ambiguity
- Human-readable and sortable
- JSON-compatible (string format)

**Example**:
```python
from datetime import datetime, timezone

now = datetime.now(timezone.utc).isoformat()
# Returns: "2026-01-01T10:30:00+00:00"
```

### 5. Testing Strategy

**Question**: pytest vs unittest? What test structure?

**Decision**: pytest with unit + integration test separation

**Rationale**:
- pytest: Industry standard, cleaner syntax, better discovery
- Only external dependency explicitly allowed
- Constitution mandates TDD, so robust testing framework necessary
- Separate unit/integration tests for clarity

**Test Structure**:
```
tests/
├── unit/
│   ├── test_todo_model.py      # Test Todo dataclass validation
│   └── test_todo_service.py    # Test CRUD operations, file I/O
└── integration/
    └── test_cli_integration.py # Test full CLI workflows
```

**Alternatives Considered**:
- `unittest`: Standard library (acceptable), but more verbose
- `nose2`: Less actively maintained than pytest

### 6. Error Handling Patterns

**Question**: How to handle validation errors, file errors, and user input errors?

**Decision**: Raise exceptions in service layer, catch and display user-friendly messages in CLI layer

**Rationale**:
- Separation of concerns: services raise exceptions, CLI handles display
- Spec requires "user-friendly error messages" (FR-011)
- Allows programmatic error handling in tests

**Error Categories**:
1. **Validation Errors** (`ValueError`): Title empty, length limits exceeded
2. **File Errors** (`IOError`, `PermissionError`): Cannot read/write JSON file
3. **Not Found Errors** (`KeyError`): Invalid todo ID
4. **Corruption Errors** (`json.JSONDecodeError`): Malformed JSON

**Example**:
```python
# Service layer
def create_todo(title: str, description: str) -> Todo:
    if len(title) > 500:
        raise ValueError(f"Title exceeds 500 character limit (got {len(title)})")
    # ...

# CLI layer
try:
    todo = service.create_todo(title, desc)
    print(f"✓ Todo #{todo.id} created: {todo.title}")
except ValueError as e:
    print(f"Error: {e}")
```

### 7. File Backup Naming Convention

**Question**: What format for corrupted file backups?

**Decision**: `todos.json.backup.YYYY-MM-DD-HHMMSS`

**Rationale**:
- Spec requirement (FR-016)
- Timestamp allows multiple backups without collision
- Sortable chronologically
- Clear original filename preserved in prefix

**Implementation**:
```python
from datetime import datetime

def create_timestamped_backup(file_path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    backup_path = file_path.parent / f"{file_path.name}.backup.{timestamp}"
    shutil.copy2(file_path, backup_path)
    return backup_path
```

## Technology Stack Summary

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Language | Python 3.13+ | Constitution requirement |
| Package Manager | UV | Constitution requirement |
| Data Model | `@dataclass` | Type-safe, minimal boilerplate |
| JSON I/O | `json` module | Standard library |
| File Operations | `pathlib.Path` | Modern, cross-platform |
| Timestamps | `datetime` (ISO 8601) | Spec requirement |
| CLI | Interactive menu loop | Spec requirement |
| Testing | pytest | Industry standard, TDD-friendly |
| Type Hints | Built-in (PEP 484) | Better IDE support, error detection |

## Best Practices

1. **Type Hints Everywhere**: Use for all function signatures and class attributes
2. **Validation at Service Layer**: Keep models simple, validate in services
3. **Atomic File Writes**: Temp file + rename for data integrity
4. **UTC Timestamps**: Avoid timezone issues
5. **User-Friendly Errors**: Specific messages with actionable guidance
6. **Separation of Concerns**: CLI → Service → Model → File (unidirectional dependencies)

## Open Questions

None - all technical decisions resolved and aligned with spec + constitution.

## References

- Spec: `/specs/001-phase1-todo-cli/spec.md`
- Constitution: `/.specify/memory/constitution.md`
- Plan: `/specs/001-phase1-todo-cli/plan.md`

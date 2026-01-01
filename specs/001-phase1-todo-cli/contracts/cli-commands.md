# CLI Command Contracts: Phase I Todo Application

**Feature**: 001-phase1-todo-cli
**Date**: 2026-01-01
**Status**: Complete

## Overview

This document specifies the command-line interface contracts for the Phase I Todo application. The application uses an interactive menu-driven interface with numbered commands.

## General Interface

**Entry Point**: `uv run python -m src.cli.main`

**Menu Structure**: Continuous loop displaying numbered options until user exits

**Input Method**: User types option number and presses Enter

**Output Method**: Text to stdout; errors to stderr (or stdout with "Error:" prefix)

## Main Menu

```
=== Todo CLI ===
1. Add Todo
2. View All Todos
3. Toggle Status
4. Update Todo
5. Delete Todo
6. Exit

Choose option:
```

## Command Specifications

### 1. Add Todo

**Purpose**: Create a new todo with title and optional description

**Flow**:
1. Display prompt: `Enter title: `
2. User inputs title (required)
3. Validate title (non-empty, max 500 chars)
4. Display prompt: `Enter description (optional): `
5. User inputs description or presses Enter to skip
6. Validate description (max 2000 chars)
7. Create todo with `completed = False`
8. Persist to file
9. Display confirmation

**Inputs**:
- `title` (string): Required, 1-500 characters, non-empty after strip
- `description` (string): Optional, 0-2000 characters

**Outputs**:
- Success: `✓ Todo #{id} created: {title}`
- Error (empty title): `Error: Title cannot be empty`
- Error (title too long): `Error: Title exceeds 500 character limit (got {length})`
- Error (description too long): `Error: Description exceeds 2000 character limit (got {length})`

**Example Session**:
```
Enter title: Buy groceries
Enter description (optional): Milk, eggs, bread
✓ Todo #1 created: Buy groceries
```

---

### 2. View All Todos

**Purpose**: Display list of all todos with status indicators

**Flow**:
1. Retrieve all todos from in-memory list
2. If list is empty, display empty message
3. Otherwise, display formatted list with IDs, status, titles, descriptions

**Inputs**: None (no user input required)

**Outputs**:
- Empty list: `No todos found. Create one with option 1!`
- Non-empty list:
```
=== Your Todos ===

[1] ✗ Buy groceries
    Milk, eggs, bread
    Created: 2026-01-01 10:30:00

[2] ✓ Call dentist
    (no description)
    Created: 2026-01-01 11:00:00
```

**Status Indicators**:
- `✓` = completed
- `✗` = incomplete

**Formatting Rules**:
- Show ID in brackets
- Show status symbol (✓ or ✗)
- Show title on same line
- Indent description (or "(no description)" if empty)
- Show created timestamp
- Blank line between todos

---

### 3. Toggle Status

**Purpose**: Flip the completion status of a todo (incomplete ↔ complete)

**Flow**:
1. Display prompt: `Enter todo ID: `
2. User inputs ID (integer)
3. Validate ID exists
4. Toggle `completed` field (True → False or False → True)
5. Update `updated_at` timestamp
6. Persist to file
7. Display confirmation with new status

**Inputs**:
- `id` (integer): Must exist in todo list

**Outputs**:
- Success (marked complete): `✓ Todo #{id} marked as complete: {title}`
- Success (marked incomplete): `✗ Todo #{id} marked as incomplete: {title}`
- Error (invalid ID): `Error: Todo with ID {id} not found`
- Error (non-numeric): `Error: Please enter a valid number`

**Example Session**:
```
Enter todo ID: 1
✓ Todo #1 marked as complete: Buy groceries
```

---

### 4. Update Todo

**Purpose**: Modify the title and/or description of an existing todo (partial updates allowed)

**Flow**:
1. Display prompt: `Enter todo ID: `
2. User inputs ID (integer)
3. Validate ID exists
4. Display current todo details
5. Display prompt: `Enter new title (or press Enter to keep "{current_title}"): `
6. User inputs new title or presses Enter to keep current
7. Display prompt: `Enter new description (or press Enter to keep current): `
8. User inputs new description or presses Enter to keep current
9. Validate new values (if provided)
10. Update modified fields only
11. Update `updated_at` timestamp
12. Persist to file
13. Display confirmation

**Inputs**:
- `id` (integer): Must exist in todo list
- `new_title` (string): Optional (keep current if empty), 1-500 chars if provided
- `new_description` (string): Optional (keep current if empty), 0-2000 chars if provided

**Outputs**:
- Success: `✓ Todo #{id} updated: {new_title}`
- Error (ID not found): `Error: Todo with ID {id} not found`
- Error (title too long): `Error: Title exceeds 500 character limit (got {length})`
- Error (description too long): `Error: Description exceeds 2000 character limit (got {length})`

**Example Session** (update both):
```
Enter todo ID: 1
Current: [1] ✗ Buy groceries - Milk, eggs, bread

Enter new title (or press Enter to keep "Buy groceries"): Buy organic groceries
Enter new description (or press Enter to keep current): From farmer's market
✓ Todo #1 updated: Buy organic groceries
```

**Example Session** (update title only):
```
Enter todo ID: 1
Current: [1] ✗ Buy groceries - Milk, eggs, bread

Enter new title (or press Enter to keep "Buy groceries"): Buy organic groceries
Enter new description (or press Enter to keep current): [User presses Enter]
✓ Todo #1 updated: Buy organic groceries
```

---

### 5. Delete Todo

**Purpose**: Permanently remove a todo from the list

**Flow**:
1. Display prompt: `Enter todo ID: `
2. User inputs ID (integer)
3. Validate ID exists
4. Remove todo from in-memory list
5. Persist to file (ID gap remains, `next_id` unchanged)
6. Display confirmation

**Inputs**:
- `id` (integer): Must exist in todo list

**Outputs**:
- Success: `✓ Todo #{id} deleted: {title}`
- Error (ID not found): `Error: Todo with ID {id} not found`
- Error (non-numeric): `Error: Please enter a valid number`

**Example Session**:
```
Enter todo ID: 3
✓ Todo #3 deleted: Call dentist
```

**Note**: Deleted IDs are never reused. If todos with IDs 1, 2, 3 exist and #2 is deleted, the next created todo will have ID 4 (not 2).

---

### 6. Exit

**Purpose**: Close the application gracefully

**Flow**:
1. Display message: `Goodbye!`
2. Exit program (in-memory data already persisted)

**Inputs**: None

**Outputs**:
- `Goodbye!`

**Example Session**:
```
Choose option: 6
Goodbye!
```

---

## Error Handling

### Input Validation Errors

| Error Type | User Action | System Response |
|------------|-------------|-----------------|
| Empty title | Press Enter without typing | `Error: Title cannot be empty` |
| Title too long | Type >500 characters | `Error: Title exceeds 500 character limit (got {length})` |
| Description too long | Type >2000 characters | `Error: Description exceeds 2000 character limit (got {length})` |
| Invalid option | Type letter or out-of-range number | `Error: Invalid option. Please choose 1-6.` |
| Non-numeric ID | Type letters when ID expected | `Error: Please enter a valid number` |
| Todo not found | Type ID that doesn't exist | `Error: Todo with ID {id} not found` |

### File System Errors

| Error Type | System Response |
|------------|-----------------|
| File corrupted (invalid JSON) | `Warning: Data file corrupted. Created backup at /db/todos.json.backup.{timestamp}. Starting with empty todo list.` |
| File read error | `Error: Cannot read todo file. Check permissions for /db/todos.json` |
| File write error | `Error: Cannot save todos. Changes may be lost. Check disk space and permissions.` |
| Directory missing | Automatically create `/db` directory, initialize with empty todos.json |

## Data Flow

```
User Input → CLI Validation → Service Layer → In-Memory List → JSON File
                ↓                                    ↓
            Error Display                    Success Confirmation
```

## Non-Functional Requirements

**Performance**:
- Command response time: <1 second for <1000 todos
- Startup time: <2 seconds (includes file load)

**Usability**:
- Clear, numbered menu options
- Immediate feedback after every action
- Error messages with specific guidance
- Optional fields clearly marked

**Reliability**:
- All changes persisted immediately
- File corruption handled gracefully with backups
- No data loss on application crash (last successful save preserved)

## References

- Spec: `/specs/001-phase1-todo-cli/spec.md` (CLI Interaction Behavior, Functional Requirements)
- Data Model: `/specs/001-phase1-todo-cli/data-model.md`
- Plan: `/specs/001-phase1-todo-cli/plan.md`

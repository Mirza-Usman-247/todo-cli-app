# Quickstart Guide: Phase I CLI Todo Application

**Feature**: 001-phase1-todo-cli
**Date**: 2026-01-01
**Status**: Ready for implementation

## Overview

This guide provides step-by-step instructions for installing, running, and using the Phase I CLI Todo application.

## Prerequisites

- Python 3.13 or higher
- UV package manager

**Check Python version**:
```bash
python --version
# Should show: Python 3.13.x or higher
```

**Install UV** (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Installation

1. **Clone the repository** (or navigate to project directory):
```bash
cd /path/to/todo-cli-app
```

2. **Sync dependencies** using UV:
```bash
uv sync
```

This will:
- Create a virtual environment
- Install pytest (only external dependency)
- Set up the project for development

## Running the Application

**Start the Todo CLI**:
```bash
uv run python -m src.cli.main
```

You should see:
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

## Usage Examples

### Creating Your First Todo

1. Choose option `1` (Add Todo)
2. Enter a title when prompted: `Buy groceries`
3. Enter a description (or press Enter to skip): `Milk, eggs, bread`
4. You'll see: `✓ Todo #1 created: Buy groceries`

```
Choose option: 1
Enter title: Buy groceries
Enter description (optional): Milk, eggs, bread
✓ Todo #1 created: Buy groceries
```

### Viewing All Todos

1. Choose option `2` (View All Todos)
2. All todos display with status indicators

```
Choose option: 2

=== Your Todos ===

[1] ✗ Buy groceries
    Milk, eggs, bread
    Created: 2026-01-01 10:30:00

[2] ✗ Call dentist
    (no description)
    Created: 2026-01-01 11:00:00
```

**Status Indicators**:
- `✗` = Incomplete
- `✓` = Complete

### Marking a Todo as Complete

1. Choose option `3` (Toggle Status)
2. Enter the todo ID: `1`
3. You'll see: `✓ Todo #1 marked as complete: Buy groceries`

```
Choose option: 3
Enter todo ID: 1
✓ Todo #1 marked as complete: Buy groceries
```

**Note**: Running toggle again will mark it as incomplete.

### Updating a Todo

1. Choose option `4` (Update Todo)
2. Enter the todo ID: `1`
3. Enter new title (or press Enter to keep current)
4. Enter new description (or press Enter to keep current)

**Update both title and description**:
```
Choose option: 4
Enter todo ID: 1
Current: [1] ✗ Buy groceries - Milk, eggs, bread

Enter new title (or press Enter to keep "Buy groceries"): Buy organic groceries
Enter new description (or press Enter to keep current): From farmer's market
✓ Todo #1 updated: Buy organic groceries
```

**Update title only** (press Enter for description):
```
Choose option: 4
Enter todo ID: 1
Current: [1] ✗ Buy groceries - Milk, eggs, bread

Enter new title (or press Enter to keep "Buy groceries"): Buy organic groceries
Enter new description (or press Enter to keep current): [press Enter]
✓ Todo #1 updated: Buy organic groceries
```

### Deleting a Todo

1. Choose option `5` (Delete Todo)
2. Enter the todo ID: `2`
3. You'll see: `✓ Todo #2 deleted: Call dentist`

```
Choose option: 5
Enter todo ID: 2
✓ Todo #2 deleted: Call dentist
```

**Note**: Deleted todo IDs are never reused.

### Exiting the Application

1. Choose option `6` (Exit)
2. You'll see: `Goodbye!`

```
Choose option: 6
Goodbye!
```

All your todos are automatically saved and will be available next time you run the application.

## Data Storage

- **Location**: `/db/todos.json` (in project root)
- **Format**: JSON
- **Automatic Creation**: The `/db` directory and `todos.json` file are created automatically on first run
- **Persistence**: All changes are saved immediately after each operation

**Example `/db/todos.json`**:
```json
{
  "todos": [
    {
      "id": 1,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2026-01-01T10:30:00+00:00",
      "updated_at": "2026-01-01T10:30:00+00:00"
    }
  ],
  "next_id": 2
}
```

## Common Tasks

### Add Multiple Todos Quickly

After creating a todo, you're returned to the main menu. Just choose option `1` again:

```
✓ Todo #1 created: Buy groceries

=== Todo CLI ===
...
Choose option: 1
Enter title: Call dentist
...
```

### Check What's Pending

1. Run the application
2. Choose option `2` (View All)
3. Look for todos with `✗` symbol (incomplete)

### Mark All Todos Complete

For each incomplete todo:
1. Choose option `3` (Toggle Status)
2. Enter the ID
3. Repeat for each incomplete todo

## Troubleshooting

### "Error: Title cannot be empty"

**Cause**: You pressed Enter without typing a title.

**Solution**: Title is required. Type at least one non-whitespace character.

### "Error: Title exceeds 500 character limit"

**Cause**: Your title is too long.

**Solution**: Shorten the title to 500 characters or less. Use the description field for additional details.

### "Error: Description exceeds 2000 character limit"

**Cause**: Your description is too long.

**Solution**: Shorten the description to 2000 characters or less.

### "Error: Todo with ID X not found"

**Cause**: You entered an ID that doesn't exist (either deleted or never created).

**Solution**: Run option `2` (View All) to see valid IDs, then try again.

### "Warning: Data file corrupted..."

**Cause**: The `/db/todos.json` file was corrupted (invalid JSON).

**Solution**:
- The application automatically creates a backup at `/db/todos.json.backup.YYYY-MM-DD-HHMMSS`
- You start with an empty todo list
- Check the backup file if you need to recover data

### "Error: Cannot read todo file"

**Cause**: Permission issues or disk errors.

**Solution**:
- Check that you have read/write permissions for the project directory
- Ensure the disk is not full
- Check that `/db/` directory exists and is writable

## Tips & Best Practices

1. **Keep Titles Concise**: Use titles for quick identification, descriptions for details
2. **Use Descriptive Titles**: Make titles searchable (future feature)
3. **Toggle Instead of Delete**: Mark todos complete rather than deleting (keeps history)
4. **Regular Review**: Periodically view all todos to stay on track
5. **Backup Your Data**: The `/db/todos.json` file contains all your todos - back it up regularly

## Running Tests

**Run all tests**:
```bash
uv run pytest
```

**Run with coverage**:
```bash
uv run pytest --cov=src --cov-report=html
```

**Run specific test file**:
```bash
uv run pytest tests/unit/test_todo_service.py
```

## Development Mode

For development and debugging:

**Run with Python directly** (bypasses UV):
```bash
python -m src.cli.main
```

**Enable debug logging** (future feature):
```bash
DEBUG=1 uv run python -m src.cli.main
```

## Next Steps

- **Learn more**: Read `/specs/001-phase1-todo-cli/spec.md` for complete feature specifications
- **Understand the code**: Review `/specs/001-phase1-todo-cli/plan.md` for architecture details
- **Contribute**: Follow TDD workflow (write tests first, then implement)

## Support

For issues or questions:
1. Check `/specs/001-phase1-todo-cli/spec.md` (feature requirements)
2. Check `/specs/001-phase1-todo-cli/data-model.md` (data structure)
3. Check `/specs/001-phase1-todo-cli/contracts/cli-commands.md` (command details)

## References

- Spec: `/specs/001-phase1-todo-cli/spec.md`
- Plan: `/specs/001-phase1-todo-cli/plan.md`
- Data Model: `/specs/001-phase1-todo-cli/data-model.md`
- CLI Commands: `/specs/001-phase1-todo-cli/contracts/cli-commands.md`

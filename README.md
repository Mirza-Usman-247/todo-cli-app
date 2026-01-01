# Todo CLI Application - Phase I

A simple command-line todo management application built with Python.

## Features

- Add new todos with title and description
- View all todos with status indicators
- Toggle todo completion status
- Update todo title and description
- Delete todos
- Persistent storage in JSON format

## Requirements

- Python 3.12 or higher
- pytest (for development/testing)

## Installation

1. Clone the repository:
```bash
cd /path/to/todo-cli-app
```

2. Install development dependencies:
```bash
pip install -e ".[dev]"
```

## Usage

Run the application:
```bash
python -m src.cli.main
```

You will see an interactive menu with the following options:
1. Add Todo
2. View All Todos
3. Toggle Status
4. Update Todo
5. Delete Todo
6. Exit

## Data Storage

Todos are stored in `/db/todos.json` in the project root. The file is created automatically on first run.

## Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

## Project Structure

```
src/
├── models/         # Data models (Todo dataclass)
├── services/       # Business logic and file I/O
└── cli/           # Command-line interface

tests/
├── unit/          # Unit tests
└── integration/   # Integration tests

db/
└── todos.json     # Data storage (created on first run)
```

## Development

This project follows Test-Driven Development (TDD) principles. All features are implemented with tests written first.

See `/specs/001-phase1-todo-cli/` for complete specifications and design documents.

## License

MIT

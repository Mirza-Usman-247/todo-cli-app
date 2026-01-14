# ORM Modeling Skill

This Claude skill enables the creation of PostgreSQL tables using **SQLModel**, ensuring proper database schema modeling with Neon PostgreSQL compatibility.

## Features

- Creates Task, Conversation, Message models following SQLModel best practices
- Ensures schema matches exactly as specified
- Compatible with Neon PostgreSQL
- Adds indexes only when necessary
- Validates proper SQLModel usage over other ORM frameworks

## Usage

Claude can use this skill when generating or updating database models for the application. The skill ensures that:

- Only SQLModel is used (not SQLAlchemy Core or other ORMs)
- Database models match exactly as specified
- Indexes are added judiciously and only when necessary
- Models are compatible with Neon PostgreSQL
- No in-memory storage is used

## Available Functions

### Model Creation

```python
from orm_modeling import create_task_model, create_conversation_model, create_message_model

# Create standard models
Task = create_task_model()
Conversation = create_conversation_model()
Message = create_message_model()
```

### Model Validation

```python
from orm_modeling import validate_model, ensure_neon_compatibility

# Validate that a model follows ORM Modeling Skill constraints
is_valid = validate_model(MyModel)

# Ensure model is compatible with Neon PostgreSQL
is_compatible = ensure_neon_compatibility(MyModel)
```

## Standard Models

The skill provides three standard models:

### Task Model
- `id`: Primary key (auto-generated)
- `title`: Required string
- `description`: Optional string
- `completed`: Boolean with default False
- `created_at`: Timestamp
- `updated_at`: Timestamp

### Conversation Model
- `id`: Primary key (auto-generated)
- `title`: Required string
- `user_id`: Optional user identifier
- `created_at`: Timestamp
- `updated_at`: Timestamp

### Message Model
- `id`: Primary key (auto-generated)
- `conversation_id`: Foreign key to conversation
- `content`: Required message content
- `role`: Role of the message sender (user, assistant, etc.)
- `created_at`: Timestamp

## Best Practices

When using this skill, Claude will:

- Use SQLModel exclusively for all model definitions
- Follow proper field definitions with appropriate constraints
- Include proper timestamp fields with default factories
- Use foreign keys appropriately between related models
- Apply indexes only when necessary for performance
- Ensure Neon PostgreSQL compatibility

## Constraints

The skill enforces these constraints:

- Only SQLModel can be used (not SQLAlchemy Core or other ORMs)
- Models must match the specified schema exactly
- No in-memory storage solutions
- Compatibility with Neon PostgreSQL required
- Follow SQLModel best practices
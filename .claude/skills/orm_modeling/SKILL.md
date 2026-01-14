# ORM Modeling Skill

## Purpose
This skill allows Claude to correctly model PostgreSQL schemas using **SQLModel**.

## Claude Must:
- Use **SQLModel** exclusively (not SQLAlchemy Core)
- Match database models exactly as specified
- Add indexes **only when necessary**

## Applied In
This skill is applied for:
- `Task` model
- `Conversation` model
- `Message` model

## Constraints
- Must be compatible with **Neon PostgreSQL**
- **No in-memory storage**
- Follow SQLModel best practices
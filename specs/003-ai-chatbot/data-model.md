# Data Model: AI Chatbot Conversations

**Feature**: 003-ai-chatbot
**Created**: 2026-01-15
**Status**: Draft

## Overview

This document defines the database schema for AI chatbot conversation persistence. The design supports **one persistent conversation per user** with full message history stored in PostgreSQL.

## Design Principles

1. **Stateless Architecture**: All conversation state persists in database; no in-memory storage
2. **User Isolation**: Conversations and messages are scoped to user_id with strict access controls
3. **Performance**: Indexed queries for fast retrieval of last 100 messages
4. **Auditability**: All messages timestamped for history tracking
5. **Simplicity**: Minimal schema with only essential fields

## Schema Definition

### Table: `conversations`

Represents a single persistent conversation per user.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique conversation identifier |
| `user_id` | VARCHAR(255) | NOT NULL, UNIQUE, FOREIGN KEY → users(id) | Owner of conversation (Better Auth user ID) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Conversation creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last message timestamp (for sorting/cleanup) |

**Indexes**:
- `PRIMARY KEY (id)` - Default primary key index
- `UNIQUE INDEX idx_conversations_user_id ON conversations(user_id)` - Enforce one conversation per user, fast lookup by user

**Constraints**:
- `FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE` - Delete conversation when user deleted

**Notes**:
- `updated_at` automatically updated on each new message append
- No `title` or `metadata` fields for Phase III (YAGNI principle)

---

### Table: `messages`

Represents individual messages within a conversation (user or assistant).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique message identifier |
| `conversation_id` | UUID | NOT NULL, FOREIGN KEY → conversations(id) | Parent conversation |
| `role` | VARCHAR(20) | NOT NULL, CHECK (role IN ('user', 'assistant')) | Message sender (user or assistant) |
| `content` | TEXT | NOT NULL | Message text content |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Message creation timestamp |

**Indexes**:
- `PRIMARY KEY (id)` - Default primary key index
- `INDEX idx_messages_conversation_created ON messages(conversation_id, created_at DESC)` - Fast retrieval of last 100 messages per conversation

**Constraints**:
- `FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE` - Delete messages when conversation deleted
- `CHECK (role IN ('user', 'assistant'))` - Enforce valid roles

**Notes**:
- `content` is TEXT (unlimited length) to support long messages
- `created_at` provides message ordering within conversation
- No `tokens`, `model`, or `metadata` fields for Phase III (YAGNI principle)

---

## SQLModel Schemas

### Conversation Model

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List

class Conversation(SQLModel, table=True):
    """
    Represents a persistent conversation for a user.
    Each user has exactly one conversation.
    """
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(
        nullable=False,
        unique=True,
        foreign_key="users.id",
        index=True
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to messages (not loaded by default)
    messages: List["Message"] = Relationship(back_populates="conversation")
```

### Message Model

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Literal

class Message(SQLModel, table=True):
    """
    Represents a single message in a conversation.
    Can be from 'user' or 'assistant'.
    """
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(
        nullable=False,
        foreign_key="conversations.id",
        index=True
    )
    role: Literal["user", "assistant"] = Field(nullable=False)
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to conversation
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

---

## Database Queries

### Create or Get User's Conversation

```python
from sqlmodel import Session, select

def get_or_create_conversation(session: Session, user_id: str) -> Conversation:
    """
    Get existing conversation for user, or create new one if not exists.
    """
    statement = select(Conversation).where(Conversation.user_id == user_id)
    conversation = session.exec(statement).first()

    if not conversation:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    return conversation
```

### Fetch Last 100 Messages

```python
from sqlmodel import Session, select

def get_last_messages(
    session: Session,
    conversation_id: UUID,
    limit: int = 100
) -> List[Message]:
    """
    Fetch last N messages for a conversation, ordered by created_at DESC.
    Returns messages in chronological order (oldest first).
    """
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = session.exec(statement).all()

    # Reverse to get chronological order (oldest → newest)
    return list(reversed(messages))
```

### Append Message to Conversation

```python
from sqlmodel import Session
from datetime import datetime

def append_message(
    session: Session,
    conversation_id: UUID,
    role: Literal["user", "assistant"],
    content: str
) -> Message:
    """
    Append a new message to conversation and update conversation.updated_at.
    """
    # Create message
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    session.add(message)

    # Update conversation timestamp
    conversation = session.get(Conversation, conversation_id)
    conversation.updated_at = datetime.utcnow()

    session.commit()
    session.refresh(message)

    return message
```

---

## Migration Strategy

### Alembic Migration Script

```python
"""Add conversations and messages tables

Revision ID: 003_ai_chatbot
Revises: 002_phase2_todo_web
Create Date: 2026-01-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '003_ai_chatbot'
down_revision = '002_phase2_todo_web'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', name='uq_conversations_user_id')
    )
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'], unique=True)

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('conversation_id', UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.TEXT(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.CheckConstraint("role IN ('user', 'assistant')", name='ck_messages_role')
    )
    op.create_index('idx_messages_conversation_created', 'messages', ['conversation_id', sa.text('created_at DESC')])

def downgrade() -> None:
    op.drop_index('idx_messages_conversation_created', table_name='messages')
    op.drop_table('messages')
    op.drop_index('idx_conversations_user_id', table_name='conversations')
    op.drop_table('conversations')
```

### Running Migration

```bash
# Generate migration (auto-detect changes)
alembic revision --autogenerate -m "Add conversations and messages tables"

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

---

## Data Integrity Rules

1. **User Isolation**: All queries MUST filter by `user_id` to prevent cross-user data leaks
2. **Conversation Uniqueness**: System enforces one conversation per user via UNIQUE constraint
3. **Message Ordering**: Messages are ordered by `created_at` (immutable timestamp)
4. **Cascade Deletes**: Deleting user → deletes conversations → deletes messages (automatic cleanup)
5. **Role Validation**: Only 'user' and 'assistant' roles allowed (enforced by CHECK constraint)

---

## Performance Considerations

### Query Performance

- **Last 100 messages**: O(log n) lookup via `idx_messages_conversation_created` index
- **Get conversation by user**: O(1) lookup via `idx_conversations_user_id` unique index
- **Append message**: O(1) insert + O(1) conversation update

### Scalability

- **Storage**: Assuming 100 messages/user @ 500 bytes/message = 50KB/user
- **For 10K users**: ~500MB conversation data (negligible)
- **For 1M users**: ~50GB conversation data (manageable with partitioning if needed)

### Optimization Strategies (if needed)

1. **Partitioning**: Partition `messages` table by `conversation_id` if conversations grow very large
2. **Archival**: Archive messages older than 1 year to cold storage (not needed for Phase III)
3. **Caching**: Cache last 100 messages in Redis (not needed for Phase III - database is fast enough)

---

## Testing Strategy

### Unit Tests

```python
def test_create_conversation(session: Session):
    """Test conversation creation with user_id"""
    conversation = Conversation(user_id="user123")
    session.add(conversation)
    session.commit()

    assert conversation.id is not None
    assert conversation.user_id == "user123"
    assert conversation.created_at is not None

def test_unique_conversation_per_user(session: Session):
    """Test that only one conversation per user is allowed"""
    conversation1 = Conversation(user_id="user123")
    session.add(conversation1)
    session.commit()

    # Attempting to create second conversation for same user should fail
    conversation2 = Conversation(user_id="user123")
    session.add(conversation2)

    with pytest.raises(IntegrityError):
        session.commit()

def test_append_message(session: Session):
    """Test message creation and ordering"""
    conversation = Conversation(user_id="user123")
    session.add(conversation)
    session.commit()

    message1 = append_message(session, conversation.id, "user", "Hello")
    message2 = append_message(session, conversation.id, "assistant", "Hi there!")

    messages = get_last_messages(session, conversation.id, limit=100)
    assert len(messages) == 2
    assert messages[0].content == "Hello"
    assert messages[1].content == "Hi there!"

def test_last_100_messages_limit(session: Session):
    """Test that only last 100 messages are retrieved"""
    conversation = Conversation(user_id="user123")
    session.add(conversation)
    session.commit()

    # Create 150 messages
    for i in range(150):
        append_message(session, conversation.id, "user", f"Message {i}")

    messages = get_last_messages(session, conversation.id, limit=100)
    assert len(messages) == 100
    assert messages[0].content == "Message 50"  # Oldest of last 100
    assert messages[-1].content == "Message 149"  # Newest
```

### Integration Tests

```python
def test_cascade_delete_conversation(session: Session):
    """Test that deleting conversation deletes all messages"""
    conversation = Conversation(user_id="user123")
    session.add(conversation)
    session.commit()

    # Add messages
    append_message(session, conversation.id, "user", "Test")
    append_message(session, conversation.id, "assistant", "Response")

    # Delete conversation
    session.delete(conversation)
    session.commit()

    # Verify messages are deleted
    messages = session.exec(
        select(Message).where(Message.conversation_id == conversation.id)
    ).all()
    assert len(messages) == 0
```

---

## Edge Cases

1. **Empty Conversation**: New conversation with zero messages → `get_last_messages()` returns empty list
2. **First Message**: Creating user's first message → creates conversation automatically via `get_or_create_conversation()`
3. **Exactly 100 Messages**: Fetching last 100 → returns all 100 in chronological order
4. **User Deletion**: Deleting user → cascades to conversations and messages (automatic cleanup)
5. **Concurrent Appends**: Two messages appended simultaneously → both succeed (database handles concurrency)
6. **Very Long Message**: Content exceeds 10KB → supported (TEXT type has no practical limit)

---

## Security Considerations

1. **SQL Injection**: SQLModel parameterized queries prevent injection
2. **User Isolation**: All queries MUST include `user_id` filter (enforced at service layer)
3. **Access Control**: API validates `user_id` in path matches authenticated user (Better Auth)
4. **Data Retention**: No automatic message deletion (users retain full history)
5. **Sensitive Data**: Messages stored in plaintext (no PII should be in chat for Phase III)

---

## Future Enhancements (Out of Scope for Phase III)

- **Message Editing**: Add `edited_at` timestamp and `is_edited` flag
- **Message Deletion**: Add `deleted_at` for soft deletes
- **Rich Content**: Add `attachments` JSONB field for images/files
- **Conversation Metadata**: Add `title`, `tags`, `archived` fields
- **Token Tracking**: Add `tokens` integer field for cost tracking
- **Model Versioning**: Add `model` varchar field to track which agent version generated response
- **Feedback**: Add `feedback` JSONB field for user ratings on assistant responses

---

## Acceptance Criteria

- [x] Schema supports one persistent conversation per user
- [x] Schema supports unlimited message history per conversation
- [x] Queries for last 100 messages are indexed and performant
- [x] Cascade deletes prevent orphaned messages
- [x] User isolation enforced via foreign keys and indexes
- [x] SQLModel schemas match database schema exactly
- [x] Migration script creates tables with correct constraints
- [x] All edge cases documented with expected behavior

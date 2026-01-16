"""
ConversationService for managing chat conversations and messages.

Implements stateless conversation architecture:
- One persistent conversation per user (FR-022a)
- Load last 100 messages per request (FR-022b, FR-107)
- Create/update conversation and messages (FR-106)
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.conversation import Conversation
from src.models.message import Message


class ConversationService:
    """Service for managing conversations and messages."""

    @staticmethod
    async def get_or_create_conversation(
        session: AsyncSession,
        user_id: UUID
    ) -> Conversation:
        """
        Get existing conversation for user or create new one.

        One persistent conversation per user (FR-022a).

        Args:
            session: Database session
            user_id: User UUID

        Returns:
            Conversation instance
        """
        # Check if conversation exists
        statement = select(Conversation).where(Conversation.user_id == user_id)
        result = await session.execute(statement)
        conversation = result.scalars().first()

        if conversation:
            return conversation

        # Create new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        return conversation

    @staticmethod
    async def load_conversation_history(
        session: AsyncSession,
        conversation_id: UUID,
        limit: int = 100
    ) -> list[Message]:
        """
        Load last N messages from conversation (FR-022b).

        Args:
            session: Database session
            conversation_id: Conversation UUID
            limit: Number of messages to load (default: 100)

        Returns:
            List of messages in chronological order
        """
        # Query last N messages ordered by timestamp DESC
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.desc())
            .limit(limit)
        )
        result = await session.execute(statement)
        messages = result.scalars().all()

        # Reverse to get chronological order
        return list(reversed(messages))

    @staticmethod
    async def add_message(
        session: AsyncSession,
        conversation_id: UUID,
        role: str,
        content: str,
        tool_metadata: Optional[dict] = None
    ) -> Message:
        """
        Add a message to conversation (FR-109, FR-024).

        Args:
            session: Database session
            conversation_id: Conversation UUID
            role: Message role ('user' or 'assistant')
            content: Message content
            tool_metadata: Optional tool call metadata

        Returns:
            Created message
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_metadata=tool_metadata
        )
        session.add(message)

        # Update conversation updated_at timestamp
        conversation_statement = select(Conversation).where(
            Conversation.id == conversation_id
        )
        result = await session.execute(conversation_statement)
        conversation = result.scalars().first()
        if conversation:
            conversation.updated_at = datetime.utcnow()
            session.add(conversation)

        await session.commit()
        await session.refresh(message)
        return message

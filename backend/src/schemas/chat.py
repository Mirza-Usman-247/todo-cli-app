"""
Pydantic schemas for Chat API.
"""
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request schema for chat endpoint (FR-004)."""

    message: str = Field(
        ...,
        description="User's message to the chatbot"
    )
    conversation_id: Optional[UUID] = Field(
        default=None,
        description="Optional conversation ID (created if not provided)"
    )


class ToolCall(BaseModel):
    """Tool call metadata."""

    tool: str = Field(description="Tool name that was called")
    status: str = Field(description="Execution status (success/failed)")
    result: Optional[str] = Field(default=None, description="Tool result summary")


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    response: str = Field(
        description="AI assistant's response message"
    )
    conversation_id: UUID = Field(
        description="Conversation UUID"
    )
    tool_calls: list[ToolCall] = Field(
        default_factory=list,
        description="List of tool calls made during this turn"
    )

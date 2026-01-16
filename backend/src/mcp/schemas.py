"""
MCP Tool Schemas for request/response validation.
"""
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class TaskResult(BaseModel):
    """Generic result for MCP tool operations."""
    success: bool = Field(description="Whether operation succeeded")
    message: str = Field(description="Human-readable result message")
    task_id: Optional[UUID] = Field(default=None, description="Task UUID if applicable")


class TaskInfo(BaseModel):
    """Task information returned by list_tasks."""
    id: UUID = Field(description="Task UUID")
    title: str = Field(description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    is_completed: bool = Field(description="Completion status")

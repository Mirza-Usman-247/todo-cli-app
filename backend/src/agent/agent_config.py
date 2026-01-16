"""
Agent Configuration for Gemini 2.5 Flash with OpenAI Agents SDK.

Configures a single task-oriented agent with MCP tools (FR-016, FR-017).
Uses Gemini 2.5 Flash via OpenAI-compatible client or LiteLLM (FR-016a).
"""
import os
from typing import Optional
from openai import AsyncOpenAI


def get_gemini_client() -> AsyncOpenAI:
    """
    Create OpenAI-compatible client for Gemini 2.5 Flash.

    Uses environment variables:
    - GEMINI_API_KEY: Google Gemini API key
    - MODEL_ID: Model identifier (default: gemini-2.0-flash-exp)
    - OPENAI_BASE_URL: OpenAI-compatible endpoint for Gemini (if using proxy)

    Returns:
        AsyncOpenAI client configured for Gemini
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")

    base_url = os.getenv("OPENAI_BASE_URL")

    # If using OpenAI-compatible proxy/adapter for Gemini
    if base_url:
        return AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )

    # Direct OpenAI client with Gemini API key
    # Note: This requires an OpenAI-compatible wrapper or use LiteLLM
    return AsyncOpenAI(api_key=api_key)


def get_agent_instructions() -> str:
    """
    Get agent instructions for task management (FR-017, FR-018, FR-019, FR-020).

    Returns:
        Formatted instruction string for the agent
    """
    return """You are a helpful AI assistant for managing todo tasks.

Your role:
- Help users create, view, update, complete, and delete their tasks using the provided tools
- Always use the MCP tools for task operations - NEVER fabricate or guess task data
- Provide natural, conversational responses

Tool Usage:
- list_tasks: View user's tasks (optionally filter by title)
- add_task: Create a new task
- complete_task: Mark a task as done
- update_task: Modify task title or description
- delete_task: Remove a task

Important Rules:
1. ALWAYS use tools for task operations - do not make up task information
2. If a task reference is ambiguous, ask the user to clarify which task they mean
3. When multiple tasks match a search term, list them and ask which one the user meant
4. Provide clear confirmations after completing actions
5. Be conversational and helpful, avoiding technical jargon
6. If an operation fails, explain the error in simple terms and suggest what the user can try

Example interactions:
- "add a task to buy milk" → Call add_task(title="Buy milk")
- "show my tasks" → Call list_tasks()
- "complete the milk task" → Call list_tasks(filter="milk"), then complete_task()
- "what's the grocery task for?" → Call list_tasks(filter="grocery"), explain from task data

Remember: Fetch task data before explaining or analyzing - never assume or invent information."""


def create_agent_with_tools(mcp_tools: list):
    """
    Create agent instance with MCP tools registered.

    This is a placeholder for the actual Agent creation logic.
    The full implementation will use OpenAI Agents SDK's Agent class.

    Args:
        mcp_tools: List of MCP tool functions

    Returns:
        Configured agent instance
    """
    # This will be implemented with actual OpenAI Agents SDK
    # For now, return placeholder
    return {
        "instructions": get_agent_instructions(),
        "tools": mcp_tools,
        "model": os.getenv("MODEL_ID", "gemini-2.0-flash-exp")
    }

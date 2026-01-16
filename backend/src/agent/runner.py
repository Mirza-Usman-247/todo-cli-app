"""
Agent Runner for executing chatbot with conversation context.

Simplified runner that integrates MCP tools with OpenAI-compatible LLM.
Uses direct OpenAI chat completions API with tool calling (FR-016, FR-017).
"""
import os
import json
from typing import Any
from uuid import UUID
from openai import AsyncOpenAI

from src.models.message import Message
from src.schemas.chat import ToolCall
from src.mcp.tools import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task
)


# Tool registry for MCP tools
TOOLS = {
    "add_task": add_task,
    "list_tasks": list_tasks,
    "complete_task": complete_task,
    "delete_task": delete_task,
    "update_task": update_task,
}


# Tool definitions for OpenAI function calling
# Note: user_id is automatically injected by the backend and should NOT be in the parameters
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the current user",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Task description (optional)"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List the current user's tasks with optional filtering",
            "parameters": {
                "type": "object",
                "properties": {
                    "filter": {"type": "string", "description": "Optional search term for title filtering"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed for the current user",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_ref": {"type": "string", "description": "Task UUID or title substring"}
                },
                "required": ["task_ref"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task for the current user",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_ref": {"type": "string", "description": "Task UUID or title substring"}
                },
                "required": ["task_ref"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update a task's title or description for the current user",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_ref": {"type": "string", "description": "Task UUID or title substring"},
                    "new_title": {"type": "string", "description": "New title (optional)"},
                    "new_description": {"type": "string", "description": "New description (optional)"}
                },
                "required": ["task_ref"]
            }
        }
    }
]


def get_system_prompt() -> str:
    """Get agent system instructions."""
    return """You are a helpful AI assistant for managing todo tasks.

Context:
- You are talking to an authenticated user
- The user's identity is already known to the system
- You DO NOT need to ask for user ID or any authentication information
- All task operations automatically apply to the current user

Your role:
- Help users create, view, update, complete, and delete their tasks using the provided tools
- Always use the tools for task operations - NEVER fabricate or guess task data
- Provide natural, conversational responses

Important Rules:
1. NEVER ask the user for their user ID - you already have access to it
2. ALWAYS use tools for task operations - do not make up task information
3. If a task reference is ambiguous, ask the user to clarify which task they mean
4. When multiple tasks match a search term, list them and ask which one the user meant
5. Provide clear confirmations after completing actions
6. Be conversational and helpful, avoiding technical jargon
7. If an operation fails, explain the error in simple terms

Remember: Fetch task data before explaining or analyzing - never assume or invent information."""


async def run_agent(
    user_id: UUID,
    user_message: str,
    conversation_history: list[Message]
) -> tuple[str, list[ToolCall]]:
    """
    Execute agent with conversation context and MCP tools.

    Args:
        user_id: User UUID for tool calls
        user_message: User's current message
        conversation_history: Last 100 messages from database

    Returns:
        Tuple of (assistant_response, tool_calls)
    """
    # Initialize OpenAI client
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY", "dummy-key")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("MODEL_ID", "gpt-4o")

    # For Gemini OpenAI-compatible API, we need to pass API key differently
    if base_url and "generativelanguage.googleapis.com" in base_url:
        # Use API key as authorization header for Gemini
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers={"x-goog-api-key": api_key}
        )
    else:
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url if base_url else None
        )

    # Convert conversation history to OpenAI format
    messages = [
        {"role": "system", "content": get_system_prompt()}
    ]

    for msg in conversation_history:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    # Add current user message
    messages.append({
        "role": "user",
        "content": user_message
    })

    # Execute chat completion with tools
    tool_calls_made = []

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        # Handle tool calls
        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)  # Parse JSON args

                # Add user_id to tool args
                tool_args["user_id"] = str(user_id)

                # Execute MCP tool with error handling
                if tool_name in TOOLS:
                    tool_result_str = ""
                    try:
                        tool_result = await TOOLS[tool_name](**tool_args)
                        tool_result_str = str(tool_result)

                        tool_calls_made.append(ToolCall(
                            tool=tool_name,
                            status="success" if tool_result.get("success", True) else "failed",
                            result=tool_result.get("message", "")
                        ))
                    except Exception as tool_error:
                        # Log the error for debugging but return user-friendly message
                        print(f"Tool execution error in {tool_name}: {str(tool_error)}")
                        tool_result_str = f"Error: {str(tool_error)}"

                        tool_calls_made.append(ToolCall(
                            tool=tool_name,
                            status="failed",
                            result=f"Error executing {tool_name}: {str(tool_error)}"
                        ))

                    # Add tool result to conversation for final response
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call.model_dump()]
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result_str
                    })

            # Get final response after tool execution
            final_response = await client.chat.completions.create(
                model=model,
                messages=messages
            )
            final_text = final_response.choices[0].message.content or "Done."
        else:
            final_text = assistant_message.content or "I'm here to help with your tasks!"

        return final_text, tool_calls_made

    except Exception as e:
        # Log detailed error for debugging
        import traceback
        print(f"Agent execution error: {str(e)}")
        print(f"Full traceback:\n{traceback.format_exc()}")

        # Return user-friendly error message
        return f"I encountered an error: {str(e)}. Please try again.", []

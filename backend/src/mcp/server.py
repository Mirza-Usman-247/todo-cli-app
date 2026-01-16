"""
FastMCP Server for AI Agent Tool Execution.

Provides MCP tools for task operations that the AI agent will use.
All tools are stateless and delegate to backend services (FR-012).
"""
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("todo-assistant")

# Tools will be registered here using @mcp.tool() decorator
# Import tool modules to register them
try:
    from src.mcp.tools import add_task, list_tasks, complete_task, delete_task, update_task  # noqa: F401
except ImportError:
    # Tools not yet implemented
    pass

# Agent Tool Design Skill (MCP)

## Purpose
Design MCP tools that are:
- Deterministic
- Stateless
- Database-backed

Claude must:
- Expose tools exactly as specified
- Use structured input/output
- Avoid business logic in the agent

## Applied In
- MCP server implementation
- Agent SDK verification
- Tool correctness validation for chatbots

## Constraints
- Tools must not store state in memory
- Tools must validate inputs
- Must adhere strictly to MCP SDK specifications

## How to Use
1. Claude receives tool specifications for MCP.
2. Claude generates Python functions/classes that:
   - Match tool signatures
   - Validate inputs
   - Connect to database if needed
3. Claude outputs structured JSON describing the tool interface and implementation.
4. Claude avoids implementing business logic inside the agent; tool should remain stateless and deterministic.
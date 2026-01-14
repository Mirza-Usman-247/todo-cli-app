# Agent Tool Design Skill (MCP)

This skill allows Claude to design MCP-compliant tools that are deterministic, stateless, and database-backed, ensuring proper tool implementation for chatbot and agent systems.

## Features

- Validates MCP tool specifications for correctness
- Ensures tools are deterministic, stateless, and database-backed
- Generates structured JSON output for MCP tools
- Provides proper input/output validation
- Prevents business logic from being embedded in the agent

## Usage

### Designing a Tool

```python
from agent_tool_design import design_tool

# Define your tool specification
tool_spec = {
    "name": "get_user_info",
    "description": "Retrieves user information by ID",
    "inputs": {
        "user_id": {
            "type": "string",
            "required": True,
            "description": "The unique identifier for the user"
        }
    },
    "outputs": {
        "user_data": {
            "type": "object",
            "description": "User information including name and email"
        },
        "found": {
            "type": "boolean",
            "description": "Whether the user was found"
        }
    },
    "database_required": True,
    "deterministic": True,
    "stateless": True
}

# Design the tool
tool_function = design_tool(tool_spec)
```

### Generating Tool Implementation

```python
from agent_tool_design import generate_tool_implementation

# Generate a structured implementation of the tool
implementation = generate_tool_implementation(tool_spec)

print(implementation['function_code'])
```

### Validating and Exposing Tools

```python
from agent_tool_design import validate_and_expose_tool

# Validate and get structured JSON representation
result = validate_and_expose_tool(tool_spec)
print(result)
```

## Key Features

### Deterministic Tools
- Tools produce the same output for the same input
- No random or time-dependent behavior
- Predictable and reliable operation

### Stateless Operation
- No in-memory state is stored in the agent
- Tools don't maintain session-specific data
- Each call is independent of previous calls

### Database Integration
- Tools connect to databases when persistent storage is needed
- Proper separation between ephemeral and persistent data
- Compliant with Neon PostgreSQL requirements

### Input/Output Validation
- Robust validation of input parameters
- Structured output format as specified
- Type safety and parameter checking

### MCP SDK Compliance
- Adheres strictly to MCP SDK specifications
- Proper tool signature matching
- Correct interface exposure

## Constraints

The skill enforces these important constraints:

- **No in-memory state**: Tools must not store state in memory
- **Input validation required**: All inputs must be properly validated
- **Business logic separation**: Business logic must remain outside the agent
- **Deterministic operation**: Tools must behave predictably
- **Stateless design**: Tools must not maintain internal state between calls
- **Database-backed persistence**: When storage is needed, use database connections

## Implementation Process

When using this skill, Claude will:

1. Receive tool specifications for MCP
2. Generate Python functions that:
   - Match tool signatures exactly
   - Validate all inputs properly
   - Connect to database when needed
3. Output structured JSON describing the tool interface and implementation
4. Ensure tools remain stateless and deterministic with no business logic in the agent

This approach ensures that all tools created with this skill are compliant with MCP specifications and follow best practices for agent development.
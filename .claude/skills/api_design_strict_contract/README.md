# API Design Skill (Strict Contract Mode)

The API Design Skill (Strict Contract Mode) ensures that RESTful APIs are generated that strictly and exactly match the provided endpoint contract, with no deviations whatsoever.

## Purpose

This skill enforces precise adherence to API contracts by:

- Matching HTTP methods exactly as defined in the contract
- Implementing URL paths with exact precision
- Following request and response schemas to the letter
- Preventing any additions or omissions to the specified endpoints
- Using FastAPI and Pydantic for proper validation

## Core Capabilities

- **Exact Method Matching**: Ensures HTTP methods match the contract exactly
- **Precise Path Validation**: Validates URL paths against the contract with no modifications
- **Schema Compliance**: Enforces exact request and response schema matching
- **Endpoint Verification**: Confirms no extra or missing endpoints exist
- **Framework Adherence**: Uses FastAPI and Pydantic as required

## Usage Patterns

### Setting Up a Contract-Based API

```python
from api_design_strict_contract import apply_strict_contract_api, create_strict_endpoint, build_api
from pydantic import BaseModel
from fastapi import FastAPI

# Define your API contract
contract = {
    "/users/{user_id}": {
        "method": "GET",
        "request": {
            "fields": {
                "user_id": {"type": "str", "required": True}
            }
        },
        "response": {
            "fields": {
                "id": {"type": "int"},
                "name": {"type": "str"},
                "email": {"type": "str"}
            }
        },
        "status_codes": [200, 404]
    },
    "/users": {
        "method": "POST",
        "request": {
            "fields": {
                "name": {"type": "str", "required": True},
                "email": {"type": "str", "required": True}
            }
        },
        "response": {
            "fields": {
                "id": {"type": "int"},
                "name": {"type": "str"},
                "email": {"type": "str"}
            }
        },
        "status_codes": [201, 400]
    }
}

# Apply the contract to enforce strict adherence
builder = apply_strict_contract_api(contract)

# Define your Pydantic models matching the contract exactly
class GetUserRequest(BaseModel):
    user_id: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

class CreateUserRequest(BaseModel):
    name: str
    email: str

# Create endpoints that follow the contract exactly
async def get_user_handler(user_id: str) -> UserResponse:
    # Implementation that returns exactly what the contract specifies
    return UserResponse(id=1, name="John Doe", email="john@example.com")

async def create_user_handler(request: CreateUserRequest) -> UserResponse:
    # Implementation that returns exactly what the contract specifies
    return UserResponse(id=2, name=request.name, email=request.email)

# Create the endpoints following the contract exactly
create_strict_endpoint(
    path="/users/{user_id}",
    method="GET",
    handler=get_user_handler,
    response_model=UserResponse,
    status_codes=[200, 404]
)

create_strict_endpoint(
    path="/users",
    method="POST",
    handler=create_user_handler,
    request_model=CreateUserRequest,
    response_model=UserResponse,
    status_codes=[201, 400]
)

# Build the API following the contract exactly
app: FastAPI = build_api()
```

### Direct Validation Approach

```python
from api_design_strict_contract import APIDesignSkill

skill = APIDesignSkill()

# Validate an existing API against a contract
validation_results = skill.validate_implementation(api_app, contract)

if validation_results['valid']:
    print("API matches contract exactly!")
else:
    print(f"Validation errors: {validation_results['errors']}")
```

## Mandatory Rules Enforcement

The skill enforces these non-negotiable rules:

### 1. HTTP Method Compliance
- Validates that each endpoint uses the exact HTTP method specified in the contract
- Raises errors if methods don't match
- Prevents method inference or changes

### 2. URL Path Accuracy
- Ensures paths match exactly as defined in the contract
- Prevents path normalization, version changes, or renaming
- Validates path parameters match the contract

### 3. Schema Precision
- Matches request schemas exactly with field names, types, and required/optional flags
- Implements response schemas with exact field structure and types
- Prevents addition or removal of fields

### 4. Endpoint Integrity
- Ensures no extra endpoints are added beyond the contract
- Confirms no endpoints from the contract are omitted
- Prevents helper, health, debug, or convenience endpoints

### 5. Framework Compliance
- Uses FastAPI exclusively for API creation
- Employs Pydantic models for schema validation
- Applies FastAPI decorators exactly as specified in the contract

## Behavioral Constraints

The skill prevents these behaviors:

- Improving or optimizing the API beyond the contract
- Guessing undocumented behavior
- Adding convenience features not in the contract
- Redesigning the API in any way
- Deviating from the specified contract in any manner

## Error Handling

The skill provides detailed error messages when contracts aren't followed:

- Method mismatches: Shows expected vs. actual HTTP methods
- Path validation: Identifies paths that don't match the contract
- Schema violations: Details field name/type mismatches
- Endpoint completeness: Lists missing or extra endpoints

This ensures that any deviation from the contract is immediately identified and corrected.
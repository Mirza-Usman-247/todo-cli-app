# Auth Integration (Better Auth) Skill

The Auth Integration (Better Auth) skill secures API endpoints and chat interactions using Better Auth, ensuring strict user isolation and ownership enforcement.

## Purpose

This skill provides comprehensive authentication and authorization capabilities using Better Auth to:

- Secure all API endpoints and chat interactions
- Ensure strict user isolation
- Enforce ownership checks on all user-owned data
- Validate Bearer tokens on every protected request
- Prevent cross-user access to resources

## Core Capabilities

- **Token Validation**: Validates Bearer tokens using Better Auth SDK
- **User Extraction**: Extracts authenticated user ID from Better Auth tokens
- **Ownership Enforcement**: Enforces ownership checks using extracted user_id
- **Access Control**: Rejects cross-user access attempts
- **Middleware Integration**: Provides authentication middleware/decorators

## Usage Patterns

### Protecting Endpoints

```python
from auth_better import apply_auth_protection

# Define a function to extract the resource owner ID from the request
def extract_owner_id(request_data):
    # This would typically extract the owner from the request path, params, or DB record
    return request_data.get('user_id') or request_data.get('owner_id')

# Define your handler function
def my_protected_handler(authenticated_user, request_data):
    # This function only executes if authentication and ownership checks pass
    return {"message": f"Hello {authenticated_user.name}", "user_id": authenticated_user.user_id}

# Apply authentication protection
protected_handler = apply_auth_protection(extract_owner_id, my_protected_handler)
```

### Direct Authentication Check

```python
from auth_better import check_authentication

def my_api_endpoint(request_headers, request_data):
    is_authenticated, user, error_response = check_authentication(request_headers)

    if not is_authenticated:
        return error_response  # Returns 401 or 403 error

    # Process the request with authenticated user context
    return {"success": True, "user": user.user_id}
```

## Where This Skill Applies

- All REST API endpoints that handle user data
- Chat endpoints and messaging systems
- Any request that reads or mutates user-owned data
- Database access layers
- File storage and retrieval systems
- User profile management endpoints

## Required Behavior

The skill implements these key behaviors:

1. **Header Reading**: Automatically reads the Authorization header for Bearer tokens
2. **Token Verification**: Verifies tokens using simulated Better Auth SDK (would integrate with real SDK in production)
3. **Context Attachment**: Attaches authenticated user context to requests
4. **Ownership Checking**: Uses user_id from token for database queries, chat session isolation, and resource ownership checks
5. **Access Denial**: Properly denies access with appropriate HTTP status codes:
   - 401 Unauthorized for missing or invalid tokens
   - 403 Forbidden for ownership mismatches

## Security Constraints

The skill enforces these critical constraints:

- Never implements custom authentication systems
- Never hardcodes users or user IDs
- Never mocks authentication in production code
- Never bypasses Better Auth validation
- Always trusts Better Auth as the source of truth for authentication

## Integration Pattern

The skill follows these integration patterns:

- Use auth middleware or decorators to wrap endpoints
- Implement ownership checks before returning or mutating data
- Always verify user identity before accessing user-specific resources
- Return appropriate HTTP status codes for authentication failures

## Error Handling

The skill properly handles these authentication scenarios:

- Missing Authorization headers → Returns 401 Unauthorized
- Invalid or malformed tokens → Returns 401 Unauthorized
- Expired tokens → Returns 401 Unauthorized
- Resource ownership mismatch → Returns 403 Forbidden
- Malformed request data → Returns 403 Forbidden

## Critical Enforcement

If authentication is required for an endpoint and this skill is not applied, the system should:

1. Stop processing the request
2. Apply this skill before proceeding
3. Ensure all user data access is properly authenticated and authorized

This ensures that no user data can be accessed without proper authentication and ownership verification.
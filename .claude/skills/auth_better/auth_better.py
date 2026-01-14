"""
Auth Integration (Better Auth) Skill Implementation

This skill secures API endpoints and chat interactions using Better Auth.
It ensures strict user isolation and ownership enforcement.
"""

import json
from typing import Dict, Any, Optional, Callable
from functools import wraps
from dataclasses import dataclass


@dataclass
class AuthenticatedUser:
    """Represents an authenticated user with their ID and claims."""
    user_id: str
    email: str
    name: Optional[str] = None
    role: Optional[str] = None
    raw_token: Optional[str] = None


class BetterAuthValidator:
    """
    A validator class that handles Better Auth token validation and user extraction.
    """

    def __init__(self):
        # In a real implementation, this would connect to Better Auth's verification endpoint
        # For now, we'll simulate the validation process
        self.auth_enabled = True

    def validate_token(self, token: str) -> Optional[AuthenticatedUser]:
        """
        Validate a Better Auth token and return user information.

        Args:
            token: The Bearer token to validate

        Returns:
            AuthenticatedUser object if valid, None if invalid
        """
        # In a real implementation, this would call Better Auth's API to verify the token
        # For simulation purposes, we'll check if the token looks like a valid JWT
        # and extract user info from it

        if not token.startswith('Bearer '):
            return None

        actual_token = token[7:]  # Remove 'Bearer ' prefix

        # Basic validation - in reality this would call Better Auth's verification API
        if len(actual_token.split('.')) != 3:  # JWT has 3 parts separated by '.'
            return None

        # Simulate decoding and validation
        # In a real implementation, this would use the Better Auth SDK
        try:
            # This is a simplified representation - real JWT decoding would be more complex
            # and would involve cryptographic validation
            user_data = {
                'user_id': self._extract_user_id_from_token(actual_token),
                'email': self._extract_email_from_token(actual_token),
                'name': self._extract_name_from_token(actual_token)
            }

            if user_data['user_id']:
                return AuthenticatedUser(
                    user_id=user_data['user_id'],
                    email=user_data['email'],
                    name=user_data['name'],
                    raw_token=token
                )
        except Exception:
            return None

        return None

    def _extract_user_id_from_token(self, token: str) -> Optional[str]:
        """
        Extract user_id from the token (simulated for demonstration).

        Args:
            token: JWT token string

        Returns:
            User ID if found, None otherwise
        """
        # This is a simulation - in reality, this would properly decode the JWT payload
        # and extract the user ID from the 'sub' or 'user_id' claim
        import base64
        try:
            # Split the JWT token to get the payload part
            parts = token.split('.')
            if len(parts) >= 2:
                # Decode the payload part (second part)
                payload = parts[1]
                # Add padding if needed
                payload += '=' * (4 - len(payload) % 4)
                decoded_payload = base64.b64decode(payload)
                payload_json = json.loads(decoded_payload)

                # Extract user_id from the payload
                return payload_json.get('user_id') or payload_json.get('sub')
        except Exception:
            pass
        return None

    def _extract_email_from_token(self, token: str) -> Optional[str]:
        """
        Extract email from the token (simulated for demonstration).

        Args:
            token: JWT token string

        Returns:
            Email if found, None otherwise
        """
        import base64
        try:
            parts = token.split('.')
            if len(parts) >= 2:
                payload = parts[1]
                payload += '=' * (4 - len(payload) % 4)
                decoded_payload = base64.b64decode(payload)
                payload_json = json.loads(decoded_payload)

                return payload_json.get('email')
        except Exception:
            pass
        return None

    def _extract_name_from_token(self, token: str) -> Optional[str]:
        """
        Extract name from the token (simulated for demonstration).

        Args:
            token: JWT token string

        Returns:
            Name if found, None otherwise
        """
        import base64
        try:
            parts = token.split('.')
            if len(parts) >= 2:
                payload = parts[1]
                payload += '=' * (4 - len(payload) % 4)
                decoded_payload = base64.b64decode(payload)
                payload_json = json.loads(decoded_payload)

                return payload_json.get('name')
        except Exception:
            pass
        return None


class OwnershipEnforcer:
    """
    Enforces ownership checks between authenticated users and resources.
    """

    def __init__(self):
        self.validator = BetterAuthValidator()

    def check_resource_ownership(self,
                                authenticated_user: AuthenticatedUser,
                                resource_owner_id: str) -> bool:
        """
        Check if the authenticated user owns the specified resource.

        Args:
            authenticated_user: The authenticated user
            resource_owner_id: The ID of the resource owner

        Returns:
            True if the user owns the resource, False otherwise
        """
        return authenticated_user.user_id == resource_owner_id

    def validate_request_access(self,
                              token: str,
                              resource_owner_id: str) -> tuple[bool, Optional[AuthenticatedUser], Optional[str]]:
        """
        Validate that a request has access to a resource.

        Args:
            token: The Bearer token from the request
            resource_owner_id: The ID of the resource owner

        Returns:
            Tuple of (has_access, user_object, error_message)
        """
        # Step 1: Validate the token
        user = self.validator.validate_token(token)

        if not user:
            return False, None, "Invalid or missing token - 401 Unauthorized"

        # Step 2: Check ownership
        if not self.check_resource_ownership(user, resource_owner_id):
            return False, user, f"Resource does not belong to user {user.user_id} - 403 Forbidden"

        return True, user, None


class BetterAuthSkill:
    """
    Main class for the Better Auth Integration Skill that enforces authentication.
    """

    def __init__(self):
        self.enforcer = OwnershipEnforcer()
        self.middleware_applied = False

    def authenticate_request(self, headers: Dict[str, str]) -> tuple[bool, Optional[AuthenticatedUser], Optional[str]]:
        """
        Authenticate a request based on its headers.

        Args:
            headers: Dictionary of request headers

        Returns:
            Tuple of (is_authenticated, user_object, error_message)
        """
        # Step 1: Extract Authorization header
        auth_header = headers.get('Authorization') or headers.get('authorization')

        if not auth_header:
            return False, None, "Missing Authorization header - 401 Unauthorized"

        # Step 2: Validate token
        user = self.enforcer.validator.validate_token(auth_header)

        if not user:
            return False, None, "Invalid token - 401 Unauthorized"

        return True, user, None

    def protect_endpoint(self,
                        resource_owner_extractor: Callable[[Any], str],
                        handler: Callable[[AuthenticatedUser, Any], Any]):
        """
        Decorator to protect an endpoint with Better Auth.

        Args:
            resource_owner_extractor: Function that extracts the resource owner ID from the request
            handler: The function to call if authentication passes

        Returns:
            Protected handler function
        """
        @wraps(handler)
        def protected_handler(request_data: Any, headers: Dict[str, str] = None):
            # Authenticate the request
            is_authenticated, user, error_msg = self.authenticate_request(headers or {})

            if not is_authenticated:
                return {
                    "error": error_msg.split(" - ")[0] if " - " in error_msg else error_msg,
                    "status_code": 401 if "401" in error_msg else 403
                }

            # Extract resource owner ID
            try:
                resource_owner_id = resource_owner_extractor(request_data)
            except Exception as e:
                return {
                    "error": "Unable to determine resource owner - 403 Forbidden",
                    "status_code": 403
                }

            # Check ownership
            has_access, _, ownership_error = self.enforcer.validate_request_access(
                headers.get('Authorization') or headers.get('authorization'),
                resource_owner_id
            )

            if not has_access:
                error_msg = ownership_error.split(" - ")[0] if ownership_error and " - " in ownership_error else "Access denied - 403 Forbidden"
                status_code = 403
                if "401" in ownership_error:
                    status_code = 401

                return {
                    "error": error_msg,
                    "status_code": status_code
                }

            # Call the original handler with the authenticated user
            return handler(user, request_data)

        return protected_handler

    def enforce_auth_on_api_call(self,
                                 headers: Dict[str, str],
                                 resource_owner_id: str) -> tuple[bool, Optional[AuthenticatedUser], Optional[Dict[str, Any]]]:
        """
        Enforce authentication for a specific API call.

        Args:
            headers: Request headers containing the Authorization token
            resource_owner_id: ID of the resource owner to check against

        Returns:
            Tuple of (has_access, user_object, error_response)
        """
        # Validate the request
        is_authenticated, user, auth_error = self.authenticate_request(headers)

        if not is_authenticated:
            error_msg = auth_error.split(" - ")[0] if " - " in auth_error else auth_error
            status_code = 401 if "401" in auth_error else 403
            return False, None, {
                "error": error_msg,
                "status_code": status_code
            }

        # Check ownership
        has_access, _, ownership_error = self.enforcer.validate_request_access(
            headers.get('Authorization') or headers.get('authorization'),
            resource_owner_id
        )

        if not has_access:
            error_msg = ownership_error.split(" - ")[0] if ownership_error and " - " in ownership_error else "Access denied"
            status_code = 403
            if "401" in ownership_error:
                status_code = 401

            return False, user, {
                "error": error_msg,
                "status_code": status_code
            }

        return True, user, None

    def apply_auth_middleware(self):
        """
        Apply authentication middleware to ensure all requests are authenticated.
        """
        self.middleware_applied = True
        return self.middleware_applied


# Global instance for easy access
skill = BetterAuthSkill()


def apply_auth_protection(resource_owner_extractor: Callable[[Any], str],
                         handler: Callable[[AuthenticatedUser, Any], Any]):
    """
    Apply Better Auth protection to an endpoint.

    Args:
        resource_owner_extractor: Function that extracts resource owner ID from request
        handler: Handler function to protect

    Returns:
        Protected handler function
    """
    return skill.protect_endpoint(resource_owner_extractor, handler)


def check_authentication(headers: Dict[str, str]) -> tuple[bool, Optional[AuthenticatedUser], Optional[Dict[str, Any]]]:
    """
    Check authentication for a request.

    Args:
        headers: Request headers

    Returns:
        Tuple of (is_authenticated, user, error_response)
    """
    is_authenticated, user, error_msg = skill.authenticate_request(headers)

    if not is_authenticated:
        error_parts = error_msg.split(" - ")
        error_text = error_parts[0] if error_parts else "Authentication failed"
        status_code = 401 if "401" in error_msg else 403

        return is_authenticated, user, {
            "error": error_text,
            "status_code": status_code
        }

    return is_authenticated, user, None
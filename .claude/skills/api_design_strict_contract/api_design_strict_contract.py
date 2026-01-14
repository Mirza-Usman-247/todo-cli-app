"""
API Design Skill (Strict Contract Mode) Implementation

This skill ensures that RESTful APIs are generated that strictly and exactly match
the provided endpoint contract.
"""

from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel, ValidationError
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.routing import APIRoute
import inspect
import json


class ContractValidator:
    """
    Validates that API implementations match the contract exactly.
    """

    def __init__(self):
        self.contract = {}
        self.validation_errors = []

    def set_contract(self, contract: Dict[str, Any]):
        """
        Set the API contract to validate against.

        Args:
            contract: The API contract definition
        """
        self.contract = contract
        self.validation_errors = []

    def validate_http_method(self, endpoint_path: str, actual_method: str) -> bool:
        """
        Validate that the HTTP method matches the contract.

        Args:
            endpoint_path: The API endpoint path
            actual_method: The method being implemented

        Returns:
            True if method matches contract, False otherwise
        """
        if endpoint_path not in self.contract:
            self.validation_errors.append(f"Endpoint {endpoint_path} not found in contract")
            return False

        expected_method = self.contract[endpoint_path].get('method', '').upper()
        if expected_method != actual_method.upper():
            self.validation_errors.append(
                f"Method mismatch for {endpoint_path}: expected {expected_method}, got {actual_method}"
            )
            return False

        return True

    def validate_path(self, actual_path: str) -> bool:
        """
        Validate that the endpoint path matches the contract.

        Args:
            actual_path: The path being implemented

        Returns:
            True if path matches contract, False otherwise
        """
        if actual_path not in self.contract:
            self.validation_errors.append(f"Path {actual_path} not found in contract")
            return False

        return True

    def validate_request_schema(self, endpoint_path: str, request_model: type) -> bool:
        """
        Validate that the request schema matches the contract.

        Args:
            endpoint_path: The API endpoint path
            request_model: The Pydantic model for the request

        Returns:
            True if schema matches contract, False otherwise
        """
        if endpoint_path not in self.contract:
            self.validation_errors.append(f"Endpoint {endpoint_path} not found in contract")
            return False

        expected_request = self.contract[endpoint_path].get('request', {})
        expected_fields = expected_request.get('fields', {})

        # Get actual fields from the Pydantic model
        if hasattr(request_model, '__annotations__'):
            actual_fields = request_model.__annotations__
        else:
            # For Pydantic v2, use model_fields
            actual_fields = getattr(request_model, 'model_fields', {})
            if actual_fields:
                actual_fields = {k: v.annotation for k, v in actual_fields.items()}

        # Compare fields
        for field_name, field_def in expected_fields.items():
            if field_name not in actual_fields:
                self.validation_errors.append(
                    f"Field {field_name} missing from request schema for {endpoint_path}"
                )
                return False

            # Check field type if specified
            expected_type = field_def.get('type')
            if expected_type and str(expected_type).lower() != str(actual_fields[field_name]).lower():
                self.validation_errors.append(
                    f"Field {field_name} type mismatch for {endpoint_path}: expected {expected_type}, got {actual_fields[field_name]}"
                )

        # Check for extra fields not in contract
        for field_name in actual_fields:
            if field_name not in expected_fields:
                self.validation_errors.append(
                    f"Extra field {field_name} in request schema for {endpoint_path} not in contract"
                )
                return False

        return True

    def validate_response_schema(self, endpoint_path: str, response_model: type) -> bool:
        """
        Validate that the response schema matches the contract.

        Args:
            endpoint_path: The API endpoint path
            response_model: The Pydantic model for the response

        Returns:
            True if schema matches contract, False otherwise
        """
        if endpoint_path not in self.contract:
            self.validation_errors.append(f"Endpoint {endpoint_path} not found in contract")
            return False

        expected_response = self.contract[endpoint_path].get('response', {})
        expected_fields = expected_response.get('fields', {})

        # Get actual fields from the Pydantic model
        if hasattr(response_model, '__annotations__'):
            actual_fields = response_model.__annotations__
        else:
            # For Pydantic v2, use model_fields
            actual_fields = getattr(response_model, 'model_fields', {})
            if actual_fields:
                actual_fields = {k: v.annotation for k, v in actual_fields.items()}

        # Compare fields
        for field_name, field_def in expected_fields.items():
            if field_name not in actual_fields:
                self.validation_errors.append(
                    f"Field {field_name} missing from response schema for {endpoint_path}"
                )
                return False

            # Check field type if specified
            expected_type = field_def.get('type')
            if expected_type and str(expected_type).lower() != str(actual_fields[field_name]).lower():
                self.validation_errors.append(
                    f"Field {field_name} type mismatch in response for {endpoint_path}: expected {expected_type}, got {actual_fields[field_name]}"
                )

        # Check for extra fields not in contract
        for field_name in actual_fields:
            if field_name not in expected_fields:
                self.validation_errors.append(
                    f"Extra field {field_name} in response schema for {endpoint_path} not in contract"
                )
                return False

        return True

    def validate_status_codes(self, endpoint_path: str, expected_codes: List[int]) -> bool:
        """
        Validate that the status codes match the contract.

        Args:
            endpoint_path: The API endpoint path
            expected_codes: The status codes expected

        Returns:
            True if status codes match contract, False otherwise
        """
        if endpoint_path not in self.contract:
            self.validation_errors.append(f"Endpoint {endpoint_path} not found in contract")
            return False

        contract_codes = self.contract[endpoint_path].get('status_codes', [])

        # Convert to sets for comparison
        expected_set = set(expected_codes)
        contract_set = set(contract_codes)

        if expected_set != contract_set:
            self.validation_errors.append(
                f"Status codes mismatch for {endpoint_path}: expected {contract_set}, got {expected_set}"
            )
            return False

        return True


class StrictContractAPIBuilder:
    """
    Builds FastAPI applications that strictly follow the contract.
    """

    def __init__(self):
        self.validator = ContractValidator()
        self.app = FastAPI()
        self.contract_enforced = False

    def set_contract(self, contract: Dict[str, Any]):
        """
        Set the API contract to enforce.

        Args:
            contract: The API contract definition
        """
        self.validator.set_contract(contract)

    def add_endpoint(self, path: str, method: str, handler: Callable,
                     request_model: Optional[type] = None,
                     response_model: Optional[type] = None,
                     status_codes: Optional[List[int]] = None):
        """
        Add an endpoint that strictly follows the contract.

        Args:
            path: The endpoint path
            method: The HTTP method
            handler: The endpoint handler function
            request_model: The request Pydantic model
            response_model: The response Pydantic model
            status_codes: Expected status codes
        """
        # Validate against contract before adding
        if not self.validator.validate_path(path):
            raise ValueError(f"Path {path} does not match contract: {'; '.join(self.validator.validation_errors)}")

        if not self.validator.validate_http_method(path, method):
            raise ValueError(f"HTTP method for {path} does not match contract: {'; '.join(self.validator.validation_errors)}")

        if request_model and not self.validator.validate_request_schema(path, request_model):
            raise ValueError(f"Request schema for {path} does not match contract: {'; '.join(self.validator.validation_errors)}")

        if response_model and not self.validator.validate_response_schema(path, response_model):
            raise ValueError(f"Response schema for {path} does not match contract: {'; '.join(self.validator.validation_errors)}")

        if status_codes and not self.validator.validate_status_codes(path, status_codes):
            raise ValueError(f"Status codes for {path} do not match contract: {'; '.join(self.validator.validation_errors)}")

        # Reset validation errors after successful validation
        self.validator.validation_errors = []

        # Add the route to the FastAPI app
        if method.upper() == 'GET':
            self.app.get(path, response_model=response_model)(handler)
        elif method.upper() == 'POST':
            self.app.post(path, response_model=response_model)(handler)
        elif method.upper() == 'PUT':
            self.app.put(path, response_model=response_model)(handler)
        elif method.upper() == 'DELETE':
            self.app.delete(path, response_model=response_model)(handler)
        elif method.upper() == 'PATCH':
            self.app.patch(path, response_model=response_model)(handler)
        elif method.upper() == 'HEAD':
            self.app.head(path, response_model=response_model)(handler)
        elif method.upper() == 'OPTIONS':
            self.app.options(path, response_model=response_model)(handler)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        self.contract_enforced = True

    def finalize_api(self) -> FastAPI:
        """
        Finalize the API and return the FastAPI app.

        Returns:
            The FastAPI application
        """
        if not self.contract_enforced:
            raise ValueError("No endpoints were added. API must follow the contract.")

        # Verify all contract endpoints were implemented
        contract_endpoints = set(self.validator.contract.keys())
        app_routes = {route.path for route in self.app.routes if isinstance(route, APIRoute)}

        missing_endpoints = contract_endpoints - app_routes
        if missing_endpoints:
            raise ValueError(f"Missing endpoints from contract: {missing_endpoints}")

        extra_endpoints = app_routes - contract_endpoints
        if extra_endpoints:
            raise ValueError(f"Extra endpoints not in contract: {extra_endpoints}")

        return self.app


class APIDesignSkill:
    """
    Main class for the API Design (Strict Contract Mode) Skill.
    """

    def __init__(self):
        self.builder = StrictContractAPIBuilder()
        self.contract_followed = False

    def enforce_contract(self, contract: Dict[str, Any]):
        """
        Enforce the API contract for all subsequent operations.

        Args:
            contract: The API contract to enforce
        """
        self.builder.set_contract(contract)

    def create_strict_endpoint(self, path: str, method: str, handler: Callable,
                               request_model: Optional[type] = None,
                               response_model: Optional[type] = None,
                               status_codes: Optional[List[int]] = None):
        """
        Create an endpoint that strictly follows the contract.

        Args:
            path: The endpoint path
            method: The HTTP method
            handler: The endpoint handler function
            request_model: The request Pydantic model
            response_model: The response Pydantic model
            status_codes: Expected status codes
        """
        self.builder.add_endpoint(
            path=path,
            method=method,
            handler=handler,
            request_model=request_model,
            response_model=response_model,
            status_codes=status_codes
        )
        self.contract_followed = True

    def build_api(self) -> FastAPI:
        """
        Build and return the API following the contract.

        Returns:
            The FastAPI application
        """
        if not self.contract_followed:
            raise ValueError("No endpoints were created following the contract. API must follow the contract exactly.")

        return self.builder.finalize_api()

    def validate_implementation(self, api_app: FastAPI, contract: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that an API implementation follows the contract.

        Args:
            api_app: The FastAPI application to validate
            contract: The contract to validate against

        Returns:
            Validation results
        """
        validator = ContractValidator()
        validator.set_contract(contract)

        results = {
            'valid': True,
            'errors': [],
            'missing_endpoints': [],
            'extra_endpoints': [],
            'method_mismatches': []
        }

        # Get routes from the API app
        app_routes = {route.path: route.methods for route in api_app.routes if isinstance(route, APIRoute)}

        # Check for missing endpoints
        contract_endpoints = set(contract.keys())
        app_endpoints = set(app_routes.keys())

        results['missing_endpoints'] = list(contract_endpoints - app_endpoints)
        results['extra_endpoints'] = list(app_endpoints - contract_endpoints)

        # Check method matches for common endpoints
        for path, path_config in contract.items():
            if path in app_routes:
                expected_method = path_config.get('method', '').upper()
                actual_methods = {m.upper() for m in app_routes[path]}

                if expected_method not in actual_methods:
                    results['method_mismatches'].append(
                        f"Path {path}: expected {expected_method}, got {actual_methods}"
                    )

        # Overall validation
        if results['missing_endpoints'] or results['extra_endpoints'] or results['method_mismatches']:
            results['valid'] = False
            results['errors'].extend(results['method_mismatches'])

        return results


# Global instance for easy access
skill = APIDesignSkill()


def apply_strict_contract_api(contract: Dict[str, Any]) -> StrictContractAPIBuilder:
    """
    Apply the strict contract API design pattern.

    Args:
        contract: The API contract to follow

    Returns:
        A builder for creating the API
    """
    skill.enforce_contract(contract)
    return skill.builder


def create_strict_endpoint(path: str, method: str, handler: Callable,
                          request_model: Optional[type] = None,
                          response_model: Optional[type] = None,
                          status_codes: Optional[List[int]] = None):
    """
    Create an endpoint that strictly follows the contract.

    Args:
        path: The endpoint path
        method: The HTTP method
        handler: The endpoint handler function
        request_model: The request Pydantic model
        response_model: The response Pydantic model
        status_codes: Expected status codes
    """
    skill.create_strict_endpoint(
        path=path,
        method=method,
        handler=handler,
        request_model=request_model,
        response_model=response_model,
        status_codes=status_codes
    )


def build_api() -> FastAPI:
    """
    Build the API following the contract.

    Returns:
        The FastAPI application
    """
    return skill.build_api()
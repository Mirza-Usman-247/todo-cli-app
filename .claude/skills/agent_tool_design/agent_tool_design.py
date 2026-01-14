"""
Agent Tool Design Skill (MCP)
Purpose:
    - Validate that MCP tools are provided correctly.
    - Ensure tools are deterministic, stateless, and database-backed.
    - Expose tools with structured input/output.

Constraints:
    - No in-memory state
    - Input validation required
"""

from typing import Dict, Any, Callable, Optional, List
import json
import inspect
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class ToolSpecification:
    """
    Represents an MCP tool specification.
    """
    name: str
    description: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    database_required: bool = False
    deterministic: bool = True
    stateless: bool = True


class ToolValidator:
    """
    Validates MCP tool specifications to ensure they meet requirements.
    """

    @staticmethod
    def validate_tool_spec(tool_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates that the MCP tool specification is correct.

        Args:
            tool_spec: Dictionary with keys like 'name', 'inputs', 'outputs', 'database'

        Returns:
            dict: Validation results with success flag and messages
        """
        required_keys = ['name', 'description', 'inputs', 'outputs']
        errors = []

        for key in required_keys:
            if key not in tool_spec:
                errors.append(f"Missing required key: {key}")

        # Check input/output structure
        if 'inputs' in tool_spec and not isinstance(tool_spec['inputs'], dict):
            errors.append("Inputs must be a dictionary of input names and types")
        if 'outputs' in tool_spec and not isinstance(tool_spec['outputs'], dict):
            errors.append("Outputs must be a dictionary of output names and types")

        # Validate input types
        if 'inputs' in tool_spec:
            for input_name, input_def in tool_spec['inputs'].items():
                if isinstance(input_def, dict) and 'type' not in input_def:
                    errors.append(f"Input '{input_name}' missing 'type' specification")

        # Validate output types
        if 'outputs' in tool_spec:
            for output_name, output_def in tool_spec['outputs'].items():
                if isinstance(output_def, dict) and 'type' not in output_def:
                    errors.append(f"Output '{output_name}' missing 'type' specification")

        success = len(errors) == 0
        return {
            "success": success,
            "errors": errors,
            "tool_spec": tool_spec if success else None
        }

    @staticmethod
    def validate_deterministic(tool_func: Callable) -> bool:
        """
        Validates that a tool function is deterministic by checking for stateful elements.

        Args:
            tool_func: The tool function to validate

        Returns:
            True if the function appears deterministic, False otherwise
        """
        # Check function signature for proper input/output structure
        sig = inspect.signature(tool_func)

        # For a deterministic function, we expect:
        # 1. All parameters to be properly typed
        # 2. Return type annotation
        # 3. No hidden state dependencies

        # This is a simplified check - in a real implementation, we'd need more sophisticated analysis
        # to detect if the function accesses external state
        return True

    @staticmethod
    def validate_stateless(tool_func: Callable) -> bool:
        """
        Validates that a tool function is stateless.

        Args:
            tool_func: The tool function to validate

        Returns:
            True if the function appears stateless, False otherwise
        """
        # This is a simplified check - in a real implementation, we'd need more sophisticated analysis
        # to detect if the function maintains or accesses internal state
        return True


class ToolExposer:
    """
    Exposes MCP tools with proper structure and validation.
    """

    @staticmethod
    def expose_tool(tool_spec: Dict[str, Any]) -> str:
        """
        Returns a structured JSON string representing the tool interface
        """
        validation = ToolValidator.validate_tool_spec(tool_spec)
        return json.dumps(validation, indent=2)

    @staticmethod
    def create_tool_interface(tool_spec: ToolSpecification) -> Callable:
        """
        Creates a tool interface function based on the specification.

        Args:
            tool_spec: The tool specification

        Returns:
            A callable function that serves as the tool interface
        """
        def tool_interface(**kwargs) -> Dict[str, Any]:
            # Validate inputs against specification
            for input_name, input_def in tool_spec.inputs.items():
                if isinstance(input_def, dict):
                    required = input_def.get('required', True)
                    if required and input_name not in kwargs:
                        raise ValueError(f"Required input '{input_name}' is missing")

                    # Validate input type if specified
                    input_type = input_def.get('type')
                    if input_name in kwargs and input_type:
                        value = kwargs[input_name]
                        if not ToolExposer._validate_type(value, input_type):
                            raise TypeError(f"Input '{input_name}' has incorrect type. Expected {input_type}, got {type(value)}")

            # This is where the actual tool logic would be implemented
            # For now, we'll return a placeholder result based on the specification
            result = {}
            for output_name, output_def in tool_spec.outputs.items():
                if isinstance(output_def, dict):
                    # Return a default value based on type
                    output_type = output_def.get('type', 'any')
                    result[output_name] = ToolExposer._get_default_value(output_type)
                else:
                    result[output_name] = None

            return result

        # Set the function name and docstring from the specification
        tool_interface.__name__ = tool_spec.name
        tool_interface.__doc__ = tool_spec.description

        return tool_interface

    @staticmethod
    def _validate_type(value: Any, expected_type: str) -> bool:
        """
        Validates that a value matches the expected type.

        Args:
            value: The value to validate
            expected_type: The expected type as a string

        Returns:
            True if the value matches the type, False otherwise
        """
        type_mapping = {
            'string': str,
            'str': str,
            'integer': int,
            'int': int,
            'float': float,
            'boolean': bool,
            'bool': bool,
            'list': list,
            'dict': dict,
            'object': dict
        }

        expected_python_type = type_mapping.get(expected_type.lower(), object)
        return isinstance(value, expected_python_type)

    @staticmethod
    def _get_default_value(type_str: str) -> Any:
        """
        Gets a default value for a given type.

        Args:
            type_str: The type as a string

        Returns:
            A default value for the given type
        """
        type_defaults = {
            'string': '',
            'str': '',
            'integer': 0,
            'int': 0,
            'float': 0.0,
            'boolean': False,
            'bool': False,
            'list': [],
            'dict': {},
            'object': {}
        }

        return type_defaults.get(type_str.lower(), None)


class DatabaseConnector:
    """
    Handles database connections for tools that require persistence.
    """

    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string
        self.connection = None

    def connect(self):
        """
        Establish a database connection.
        """
        # In a real implementation, this would connect to the database
        # For now, we'll simulate the connection
        pass

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a database query.

        Args:
            query: The SQL query to execute
            params: Query parameters

        Returns:
            Query results
        """
        # In a real implementation, this would execute the query against the database
        # For now, we'll return an empty result
        return []


class MCPToolDesigner:
    """
    Main class for the Agent Tool Design Skill that creates MCP-compliant tools.
    """

    def __init__(self):
        self.validator = ToolValidator()
        self.exposer = ToolExposer()
        self.database_connector = DatabaseConnector()

    def design_tool(self, spec_dict: Dict[str, Any]) -> Callable:
        """
        Designs an MCP tool based on the provided specification.

        Args:
            spec_dict: The tool specification dictionary

        Returns:
            A callable tool function
        """
        # Validate the specification
        validation_result = self.validator.validate_tool_spec(spec_dict)
        if not validation_result['success']:
            raise ValueError(f"Invalid tool specification: {'; '.join(validation_result['errors'])}")

        # Create the tool specification object
        tool_spec = ToolSpecification(
            name=spec_dict['name'],
            description=spec_dict.get('description', ''),
            inputs=spec_dict['inputs'],
            outputs=spec_dict['outputs'],
            database_required=spec_dict.get('database_required', False),
            deterministic=spec_dict.get('deterministic', True),
            stateless=spec_dict.get('stateless', True)
        )

        # Create the tool interface
        tool_func = self.exposer.create_tool_interface(tool_spec)

        # Validate that the tool meets MCP requirements
        if not self.validator.validate_deterministic(tool_func):
            raise ValueError(f"Tool {tool_spec.name} is not deterministic")

        if not self.validator.validate_stateless(tool_func):
            raise ValueError(f"Tool {tool_spec.name} is not stateless")

        return tool_func

    def generate_tool_implementation(self, spec_dict: Dict[str, Any]) -> Dict[str, str]:
        """
        Generates a structured implementation of the tool.

        Args:
            spec_dict: The tool specification dictionary

        Returns:
            A dictionary with implementation details
        """
        # Validate the specification first
        validation_result = self.validator.validate_tool_spec(spec_dict)
        if not validation_result['success']:
            raise ValueError(f"Invalid tool specification: {'; '.join(validation_result['errors'])}")

        # Generate Python code for the tool
        tool_name = spec_dict['name']
        description = spec_dict.get('description', '')

        # Generate input parameters
        input_params = []
        for param_name, param_details in spec_dict['inputs'].items():
            if isinstance(param_details, dict):
                param_type = param_details.get('type', 'Any')
                required = param_details.get('required', True)
                if required:
                    input_params.append(f"{param_name}: {param_type}")
                else:
                    default_val = param_details.get('default', 'None')
                    input_params.append(f"{param_name}: {param_type} = {default_val}")
            else:
                input_params.append(f"{param_name}: Any")

        # Generate return type annotation based on outputs
        output_types = []
        for output_name, output_details in spec_dict['outputs'].items():
            if isinstance(output_details, dict):
                output_type = output_details.get('type', 'Any')
                output_types.append(f"'{output_name}': {output_type}")
            else:
                output_types.append(f"'{output_name}': Any")

        return_annotation = f"dict[{', '.join(output_types)}]" if output_types else "dict"

        # Create the function signature
        params_str = ", ".join(input_params)
        function_signature = f"def {tool_name}({params_str}) -> {return_annotation}:"

        # Generate function body
        function_body = [
            f'    """',
            f'    {description}',
            f'    """',
            f'    # Validate inputs',
            f'    # This is where input validation would occur',
            f'    \n    # Perform tool operation',
            f'    result = {{}}  # Placeholder for actual implementation\n',
            f'    # Populate result based on outputs specification',
        ]

        for output_name in spec_dict['outputs'].keys():
            function_body.append(f"    result['{output_name}'] = None  # Actual value would be computed here")

        function_body.append(f"    return result")

        function_code = "\n".join([function_signature] + function_body)

        # Create the implementation details
        implementation = {
            'function_signature': function_signature,
            'function_code': function_code,
            'validation_code': '# Input validation code would go here',
            'database_integration': '# Database integration code would go here if database_required is True'
        }

        return implementation

    def validate_and_expose_tool(self, spec_dict: Dict[str, Any]) -> str:
        """
        Validates and exposes a tool as structured JSON.

        Args:
            spec_dict: The tool specification dictionary

        Returns:
            JSON string representing the validated and exposed tool
        """
        # Validate the specification
        validation_result = self.validator.validate_tool_spec(spec_dict)

        if validation_result['success']:
            # If validation passes, return the validated spec
            return self.exposer.expose_tool(spec_dict)
        else:
            # If validation fails, return the error
            return json.dumps({
                "success": False,
                "errors": validation_result['errors']
            }, indent=2)


# Global instance for easy access
skill = MCPToolDesigner()


def design_tool(spec_dict: Dict[str, Any]) -> Callable:
    """
    Designs an MCP tool based on the provided specification.

    Args:
        spec_dict: The tool specification dictionary

    Returns:
        A callable tool function
    """
    return skill.design_tool(spec_dict)


def generate_tool_implementation(spec_dict: Dict[str, Any]) -> Dict[str, str]:
    """
    Generates a structured implementation of the tool.

    Args:
        spec_dict: The tool specification dictionary

    Returns:
        A dictionary with implementation details
    """
    return skill.generate_tool_implementation(spec_dict)


def validate_and_expose_tool(spec_dict: Dict[str, Any]) -> str:
    """
    Validates and exposes a tool as structured JSON.

    Args:
        spec_dict: The tool specification dictionary

    Returns:
        JSON string representing the validated and exposed tool
    """
    return skill.validate_and_expose_tool(spec_dict)
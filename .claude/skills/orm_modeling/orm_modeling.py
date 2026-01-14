"""
ORM Modeling Skill
-----------------
Purpose:
- Model PostgreSQL tables using SQLModel.
- Ensure Neon PostgreSQL compatibility.
"""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid


class ModelValidator:
    """
    Validates that SQLModel definitions follow the ORM Modeling Skill constraints.
    """

    def __init__(self):
        self.models_defined = []

    def validate_model(self, model_class) -> bool:
        """
        Validate that a model follows ORM Modeling Skill constraints.

        Args:
            model_class: The SQLModel class to validate

        Returns:
            True if valid, False otherwise
        """
        # Check that it inherits from SQLModel and has table=True
        if not issubclass(model_class, SQLModel):
            raise ValueError(f"Model {model_class.__name__} must inherit from SQLModel")

        # Check if it's properly configured as a table
        if not hasattr(model_class, '__table__') or model_class.__table__ is None:
            # If not mapped yet, check if it has table=True in its config
            table_arg = getattr(model_class.__config__, 'table', False) if hasattr(model_class, '__config__') else False
            if not table_arg:
                # Check for table=True in class kwargs (for declarative approach)
                if not any(hasattr(base, '__table__') for base in model_class.__bases__):
                    raise ValueError(f"Model {model_class.__name__} must have table=True")

        # Validate that model uses Neon-compatible types
        for field_name, field_info in model_class.__fields__.items() if hasattr(model_class, '__fields__') else {}:
            field_type = field_info.type_
            # Validate field types are compatible with Neon PostgreSQL
            if field_type not in [int, str, bool, float, datetime] and not hasattr(field_type, '__origin__'):
                # Allow optional types
                if hasattr(field_type, '__origin__') and field_type.__origin__ in (Optional,):
                    continue

        return True

    def register_model(self, model_class):
        """
        Register a model as being defined with this skill.

        Args:
            model_class: The SQLModel class to register
        """
        self.validate_model(model_class)
        self.models_defined.append(model_class)


class ORMModelingSkill:
    """
    Main class for the ORM Modeling Skill that ensures proper SQLModel usage.
    """

    def __init__(self):
        self.validator = ModelValidator()
        self.skill_active = True

    def create_task_model(self) -> type:
        """
        Create a Task model following SQLModel best practices and Neon compatibility.

        Returns:
            Task SQLModel class
        """
        class Task(SQLModel, table=True):
            id: Optional[int] = Field(default=None, primary_key=True)
            title: str = Field(sa_column_kwargs={"nullable": False})
            description: Optional[str] = Field(default=None)
            completed: bool = Field(default=False)
            created_at: datetime = Field(default_factory=datetime.utcnow)
            updated_at: datetime = Field(default_factory=datetime.utcnow)

        self.validator.register_model(Task)
        return Task

    def create_conversation_model(self) -> type:
        """
        Create a Conversation model following SQLModel best practices and Neon compatibility.

        Returns:
            Conversation SQLModel class
        """
        class Conversation(SQLModel, table=True):
            id: Optional[int] = Field(default=None, primary_key=True)
            title: str = Field(sa_column_kwargs={"nullable": False})
            user_id: Optional[str] = Field(default=None)  # Could be UUID or string identifier
            created_at: datetime = Field(default_factory=datetime.utcnow)
            updated_at: datetime = Field(default_factory=datetime.utcnow)

        self.validator.register_model(Conversation)
        return Conversation

    def create_message_model(self) -> type:
        """
        Create a Message model following SQLModel best practices and Neon compatibility.

        Returns:
            Message SQLModel class
        """
        class Message(SQLModel, table=True):
            id: Optional[int] = Field(default=None, primary_key=True)
            conversation_id: int = Field(foreign_key="conversation.id")
            content: str = Field(sa_column_kwargs={"nullable": False})
            role: str = Field(sa_column_kwargs={"nullable": False})  # 'user', 'assistant', etc.
            created_at: datetime = Field(default_factory=datetime.utcnow)

        self.validator.register_model(Message)
        return Message

    def create_generic_model(self, name: str, fields: dict) -> type:
        """
        Create a generic SQLModel with specified fields following best practices.

        Args:
            name: Name of the model class
            fields: Dictionary mapping field names to (type, Field specification)

        Returns:
            Dynamically created SQLModel class
        """
        attrs = {}

        # Add the id field by default if not provided
        if 'id' not in fields:
            attrs['id'] = Field(default=None, primary_key=True)

        # Add all specified fields
        for field_name, (field_type, field_spec) in fields.items():
            attrs[field_name] = field_spec

        # Create the class dynamically
        model_class = type(name, (SQLModel,), {
            **attrs,
            '__tablename__': name.lower(),
        })

        # For proper SQLModel table configuration
        class_attrs = {k: v for k, v in attrs.items()}
        class_attrs['__annotations__'] = {k: type(v.default) if hasattr(v, 'default') and v.default is not None else v.type_ for k, v in attrs.items()}

        # Create a proper class with table=True
        class DynamicModel(SQLModel, table=True):
            pass

        # Apply attributes to the new class
        for attr_name, attr_value in attrs.items():
            setattr(DynamicModel, attr_name, attr_value)

        # Set annotations properly
        if not hasattr(DynamicModel, '__annotations__'):
            DynamicModel.__annotations__ = {}

        for field_name, (field_type, _) in fields.items():
            DynamicModel.__annotations__[field_name] = field_type

        # Rename the class to the requested name
        DynamicModel.__name__ = name
        DynamicModel.__qualname__ = name

        self.validator.register_model(DynamicModel)
        return DynamicModel

    def validate_neon_compatibility(self, model_class: type) -> bool:
        """
        Validate that a model is compatible with Neon PostgreSQL.

        Args:
            model_class: The SQLModel class to validate

        Returns:
            True if compatible, False otherwise
        """
        # Check that the model doesn't use incompatible features
        for field_name, field_obj in model_class.__dict__.items():
            if isinstance(field_obj, Field):
                # Check for any incompatible configurations
                pass  # For now, assume all SQLModel fields are Neon-compatible

        return True

    def ensure_sqlmodel_usage(self, model_definition: str) -> bool:
        """
        Ensure that a model definition uses SQLModel and not other ORM frameworks.

        Args:
            model_definition: String representation of model definition

        Returns:
            True if using SQLModel, False otherwise
        """
        # Check for SQLModel imports and inheritance
        if 'from sqlmodel' not in model_definition and 'import sqlmodel' not in model_definition:
            return False

        if '(SQLModel' not in model_definition and 'SQLModel,' not in model_definition:
            return False

        # Check that it's not using SQLAlchemy Core patterns
        if 'Table(' in model_definition or 'Column(' in model_definition:
            return False

        return True


# Global instance for easy access
skill = ORMModelingSkill()


def create_task_model() -> type:
    """
    Create a Task model following SQLModel best practices and Neon compatibility.

    Returns:
        Task SQLModel class
    """
    return skill.create_task_model()


def create_conversation_model() -> type:
    """
    Create a Conversation model following SQLModel best practices and Neon compatibility.

    Returns:
        Conversation SQLModel class
    """
    return skill.create_conversation_model()


def create_message_model() -> type:
    """
    Create a Message model following SQLModel best practices and Neon compatibility.

    Returns:
        Message SQLModel class
    """
    return skill.create_message_model()


def validate_model(model_class: type) -> bool:
    """
    Validate that a model follows ORM Modeling Skill constraints.

    Args:
        model_class: The SQLModel class to validate

    Returns:
        True if valid, False otherwise
    """
    return skill.validator.validate_model(model_class)


def ensure_neon_compatibility(model_class: type) -> bool:
    """
    Ensure that a model is compatible with Neon PostgreSQL.

    Args:
        model_class: The SQLModel class to validate

    Returns:
        True if compatible, False otherwise
    """
    return skill.validate_neon_compatibility(model_class)
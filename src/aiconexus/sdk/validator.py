"""
Message Validation Service
Validates messages against agent schemas
"""

from typing import Any, Dict, List, Optional
import json
import re
from abc import ABC, abstractmethod
import logging

from .types import (
    Message,
    InputSchema,
    OutputSchema,
    FieldSchema,
    ValidationResult,
    AgentSchema
)

logger = logging.getLogger(__name__)


class FieldValidator(ABC):
    """Base validator for a field"""
    
    @abstractmethod
    def validate(self, value: Any, schema: FieldSchema) -> tuple[bool, Optional[str]]:
        """Validate a value against a field schema"""
        pass


class StringValidator(FieldValidator):
    def validate(self, value: Any, schema: FieldSchema) -> tuple[bool, Optional[str]]:
        if not isinstance(value, str):
            return False, f"Expected string, got {type(value).__name__}"
        
        if schema.pattern:
            if not re.match(schema.pattern, value):
                return False, f"String does not match pattern: {schema.pattern}"
        
        return True, None


class NumberValidator(FieldValidator):
    def validate(self, value: Any, schema: FieldSchema) -> tuple[bool, Optional[str]]:
        if not isinstance(value, (int, float)):
            return False, f"Expected number, got {type(value).__name__}"
        
        if schema.min_value is not None and value < schema.min_value:
            return False, f"Value {value} is less than minimum {schema.min_value}"
        
        if schema.max_value is not None and value > schema.max_value:
            return False, f"Value {value} is greater than maximum {schema.max_value}"
        
        return True, None


class BooleanValidator(FieldValidator):
    def validate(self, value: Any, schema: FieldSchema) -> tuple[bool, Optional[str]]:
        if not isinstance(value, bool):
            return False, f"Expected boolean, got {type(value).__name__}"
        return True, None


class ArrayValidator(FieldValidator):
    def validate(self, value: Any, schema: FieldSchema) -> tuple[bool, Optional[str]]:
        if not isinstance(value, list):
            return False, f"Expected array, got {type(value).__name__}"
        return True, None


class ObjectValidator(FieldValidator):
    def validate(self, value: Any, schema: FieldSchema) -> tuple[bool, Optional[str]]:
        if not isinstance(value, dict):
            return False, f"Expected object, got {type(value).__name__}"
        return True, None


class MessageValidator:
    """
    Validates messages against schemas
    Ensures type safety and contract compliance
    """
    
    def __init__(self):
        self.validators = {
            "string": StringValidator(),
            "number": NumberValidator(),
            "boolean": BooleanValidator(),
            "array": ArrayValidator(),
            "object": ObjectValidator(),
        }
    
    async def validate_request(
        self,
        message: Dict[str, Any],
        target_agent_id: str,
        agent_schema: AgentSchema
    ) -> ValidationResult:
        """
        Validate a request message against input schema
        """
        errors = []
        warnings = []
        
        schema = agent_schema.input_schema
        
        # Check 1: Valid JSON
        try:
            payload = json.loads(json.dumps(message))
        except Exception as e:
            return ValidationResult(
                valid=False,
                errors=[f"Invalid JSON: {str(e)}"]
            )
        
        # Check 2: Required fields present
        for required_field in schema.required_fields:
            if required_field not in payload:
                errors.append(f"Missing required field: {required_field}")
        
        # Check 3: Type validation for each field
        for field_name, field_schema in schema.fields.items():
            if field_name not in payload:
                if field_schema.required:
                    errors.append(f"Missing required field: {field_name}")
                continue
            
            value = payload[field_name]
            
            # Check enum
            if field_schema.enum and value not in field_schema.enum:
                errors.append(
                    f"Field '{field_name}': value '{value}' not in enum {field_schema.enum}"
                )
                continue
            
            # Check type
            validator = self.validators.get(field_schema.type)
            if validator:
                valid, error = validator.validate(value, field_schema)
                if not valid:
                    errors.append(f"Field '{field_name}': {error}")
        
        # Check 4: No unknown fields in strict mode
        if schema.strict_mode:
            allowed_fields = set(schema.fields.keys())
            provided_fields = set(payload.keys())
            unknown_fields = provided_fields - allowed_fields
            
            if unknown_fields:
                errors.append(f"Unknown fields: {list(unknown_fields)}")
        
        valid = len(errors) == 0
        
        return ValidationResult(
            valid=valid,
            errors=errors,
            warnings=warnings,
            validated_payload=payload if valid else None
        )
    
    async def validate_response(
        self,
        response: Dict[str, Any],
        target_agent_id: str,
        agent_schema: AgentSchema
    ) -> ValidationResult:
        """
        Validate a response message against output schema
        """
        errors = []
        warnings = []
        
        schema = agent_schema.output_schema
        
        # Check 1: Valid JSON
        try:
            payload = json.loads(json.dumps(response))
        except Exception as e:
            return ValidationResult(
                valid=False,
                errors=[f"Invalid JSON: {str(e)}"]
            )
        
        # Check 2: Required fields present
        for required_field in schema.required_fields:
            if required_field not in payload:
                errors.append(f"Missing required field in response: {required_field}")
        
        # Check 3: Type validation
        for field_name, field_schema in schema.fields.items():
            if field_name not in payload:
                if field_schema.required:
                    errors.append(f"Missing required field: {field_name}")
                continue
            
            value = payload[field_name]
            
            validator = self.validators.get(field_schema.type)
            if validator:
                valid, error = validator.validate(value, field_schema)
                if not valid:
                    errors.append(f"Field '{field_name}': {error}")
        
        valid = len(errors) == 0
        
        return ValidationResult(
            valid=valid,
            errors=errors,
            warnings=warnings,
            validated_payload=payload if valid else None
        )
    
    def validate_payload_structure(self, payload: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Quick validation of basic payload structure"""
        errors = []
        
        required_fields = ["task", "context"]
        for field in required_fields:
            if field not in payload:
                errors.append(f"Missing required field: {field}")
        
        return len(errors) == 0, errors

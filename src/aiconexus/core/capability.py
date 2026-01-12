"""Capability definitions and utilities"""

from typing import Any, Dict

from pydantic import BaseModel, Field


class CapabilityInput(BaseModel):
    """Input specification for a capability"""

    param_name: str
    param_type: str
    description: str
    required: bool = True
    default: Any = None


class CapabilityOutput(BaseModel):
    """Output specification for a capability"""

    param_name: str
    param_type: str
    description: str


class CapabilityMetadata(BaseModel):
    """Metadata about a capability"""

    capability_id: str
    name: str
    description: str
    version: str
    inputs: list[CapabilityInput] = []
    outputs: list[CapabilityOutput] = []
    examples: Dict[str, Any] = Field(default_factory=dict)
    documentation_url: str = ""

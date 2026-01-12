"""Core domain classes for AIConexus"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from aiconexus.types import CapabilitySpec, ReputationScore


class Capability(BaseModel):
    """Capability offered by an agent"""

    capability_id: str
    name: str
    description: str
    version: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    sla: Dict[str, Any]
    pricing: Dict[str, Any]
    tags: List[str] = []
    requires_authentication: bool = False

    class Config:
        arbitrary_types_allowed = True


class Agent(ABC):
    """Base class for AI agents in the network"""

    def __init__(self, agent_id: Optional[UUID] = None, name: str = "Agent"):
        """
        Initialize an agent.

        Args:
            agent_id: Unique identifier (generated if not provided)
            name: Human-readable name
        """
        self.agent_id = agent_id or uuid4()
        self.name = name
        self.created_at = datetime.utcnow()
        self.capabilities: Dict[str, Capability] = {}
        self.reputation = ReputationScore(agent_id=self.agent_id)

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the agent and connect to network"""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Clean shutdown of the agent"""
        pass

    def register_capability(
        self,
        capability_id: str,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
        sla: Dict[str, Any],
        pricing: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """
        Register a new capability.

        Args:
            capability_id: Unique identifier for capability
            name: Human-readable name
            description: Detailed description
            input_schema: JSON schema for inputs
            output_schema: JSON schema for outputs
            sla: Service level agreement terms
            pricing: Pricing model
            **kwargs: Additional metadata
        """
        capability = Capability(
            capability_id=capability_id,
            name=name,
            description=description,
            version=kwargs.get("version", "1.0"),
            input_schema=input_schema,
            output_schema=output_schema,
            sla=sla,
            pricing=pricing,
            tags=kwargs.get("tags", []),
            requires_authentication=kwargs.get("requires_authentication", False),
        )
        self.capabilities[capability_id] = capability

    def get_capability(self, capability_id: str) -> Optional[Capability]:
        """Get a registered capability"""
        return self.capabilities.get(capability_id)

    def list_capabilities(self) -> List[Capability]:
        """List all registered capabilities"""
        return list(self.capabilities.values())

    @abstractmethod
    async def execute_capability(
        self, capability_id: str, input_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a capability.

        Args:
            capability_id: Which capability to execute
            input_params: Input parameters

        Returns:
            Execution result
        """
        pass

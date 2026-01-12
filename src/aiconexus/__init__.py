"""AIConexus - Universal Agent Communication Protocol & Infrastructure"""

__version__ = "0.1.0"
__author__ = "AIConexus Team"
__email__ = "team@aiconexus.io"
__license__ = "MIT"

# Core imports for public API
from aiconexus.core.agent import Agent
from aiconexus.core.capability import Capability
from aiconexus.exceptions import (
    AIConexusError,
    AgentError,
    ProtocolError,
    RegistryError,
    NegotiationError,
    ExecutionError,
    SecurityError,
)

__all__ = [
    "Agent",
    "Capability",
    "AIConexusError",
    "AgentError",
    "ProtocolError",
    "RegistryError",
    "NegotiationError",
    "ExecutionError",
    "SecurityError",
]

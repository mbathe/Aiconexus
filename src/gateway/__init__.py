"""
Gateway package - Signaling server for agent communication.

The Gateway is a separate service that:
- Manages WebSocket connections from agents
- Routes signaling messages (OFFER, ANSWER, ICE_CANDIDATE)
- Maintains agent presence/registry
- Handles connection lifecycle

The Gateway intentionally does NOT route data plane messages (INTENT, EXEC_REQUEST, etc.)
Those go directly P2P after signaling is complete.
"""

from .server import GatewayServer, create_app
from .registry import AgentRegistry, RegistryEntry

__version__ = "0.1.0"

__all__ = [
    "GatewayServer",
    "create_app",
    "AgentRegistry",
    "RegistryEntry",
]

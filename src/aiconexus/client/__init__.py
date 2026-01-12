"""
Client package - Agent SDK for connecting to the Gateway.

Provides high-level APIs for agents:
- Connect to Gateway
- Register/unregister
- Send signaling messages
- Manage WebSocket connection lifecycle
"""

from .socket import GatewayClient, ConnectionState

__all__ = [
    "GatewayClient",
    "ConnectionState",
]

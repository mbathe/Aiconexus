"""
WebSocket client for connecting agents to the Gateway.

Provides:
- Connection management
- Message sending/receiving
- Automatic reconnection
- Event handlers for lifecycle
"""

from typing import Callable, Optional, Any, Dict
from enum import Enum
import asyncio


class ConnectionState(str, Enum):
    """WebSocket connection states."""
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    DISCONNECTING = "DISCONNECTING"
    ERROR = "ERROR"


class GatewayClient:
    """
    Async WebSocket client for agents to connect to the Gateway.
    
    Usage:
        client = GatewayClient(gateway_url="ws://localhost:8000")
        client.on_message(handle_message)
        
        async with client:
            await client.register(agent_id, public_key)
            # Send/receive messages...
    """
    
    def __init__(self, gateway_url: str, agent_did: str):
        """
        Initialize Gateway client.
        
        Args:
            gateway_url: WebSocket URL (e.g., "ws://localhost:8000/ws")
            agent_did: Agent's decentralized identifier (did:key:...)
        """
        self.gateway_url = gateway_url
        self.agent_did = agent_did
        self.state = ConnectionState.DISCONNECTED
        
        self._message_handlers: list[Callable] = []
        self._error_handlers: list[Callable] = []
    
    def on_message(self, handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        Register a message handler.
        
        Args:
            handler: Async function(message_dict) called on incoming messages
        """
        self._message_handlers.append(handler)
    
    def on_error(self, handler: Callable[[Exception], None]) -> None:
        """
        Register an error handler.
        
        Args:
            handler: Async function(exception) called on errors
        """
        self._error_handlers.append(handler)
    
    async def connect(self) -> None:
        """Connect to Gateway and maintain connection."""
        pass  # Stub - will be implemented in Sprint 2
    
    async def disconnect(self) -> None:
        """Gracefully disconnect from Gateway."""
        pass  # Stub
    
    async def register(self, public_key: str) -> None:
        """
        Register with Gateway.
        
        Args:
            public_key: Base58-encoded Ed25519 public key
        """
        pass  # Stub
    
    async def send(self, message: Dict[str, Any]) -> None:
        """
        Send a message through Gateway.
        
        Args:
            message: Message dict (will be validated)
        """
        pass  # Stub
    
    async def __aenter__(self):
        """Context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.disconnect()

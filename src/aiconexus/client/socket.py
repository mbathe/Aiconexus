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
import json
import logging
import uuid
from datetime import datetime

import websockets
from websockets.client import WebSocketClientProtocol

from aiconexus.protocol.models import Message, MessageType, RegisterPayload, ErrorPayload
from aiconexus.protocol.security import DIDKey, MessageSigner
from aiconexus.protocol.errors import ProtocolError, ConnectionError
from aiconexus.protocol.serialization import MessageSerializer

logger = logging.getLogger(__name__)


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
    
    Features:
    - Automatic connection management
    - Message serialization/deserialization
    - Event handler dispatch
    - Connection state tracking
    - Automatic reconnection with exponential backoff
    
    Usage:
        from aiconexus.client import GatewayClient
        from aiconexus.protocol.security import DIDKey
        
        # Create agent identity
        did_key = DIDKey.generate()
        client = GatewayClient(
            gateway_url="ws://localhost:8000/ws",
            did_key=did_key
        )
        
        # Register handlers
        client.on_message(handle_offer)
        client.on_error(handle_error)
        
        # Connect and use
        async with client:
            await client.register(did_key.public_key_base58)
            # Listen for messages...
    """
    
    def __init__(
        self,
        gateway_url: str,
        did_key: DIDKey,
        reconnect_interval: float = 1.0,
        max_reconnect_attempts: int = 5,
    ):
        """
        Initialize Gateway client.
        
        Args:
            gateway_url: WebSocket URL (e.g., "ws://localhost:8000/ws")
            did_key: DIDKey instance for identity and message signing
            reconnect_interval: Initial reconnection interval in seconds
            max_reconnect_attempts: Maximum reconnection attempts (0 = infinite)
        """
        self.gateway_url = gateway_url
        self.did_key = did_key
        self.agent_did = did_key.did
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_attempts = max_reconnect_attempts
        
        self.state = ConnectionState.DISCONNECTED
        self._websocket: Optional[WebSocketClientProtocol] = None
        self._receive_task: Optional[asyncio.Task] = None
        self._reconnect_task: Optional[asyncio.Task] = None
        
        self._message_handlers: list[Callable] = []
        self._error_handlers: list[Callable] = []
        self._registered = False
    
    @property
    def is_connected(self) -> bool:
        """Whether client is currently connected."""
        return self.state == ConnectionState.CONNECTED and self._websocket is not None
    
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
    
    async def _set_state(self, new_state: ConnectionState) -> None:
        """Update connection state."""
        old_state = self.state
        self.state = new_state
        logger.debug(f"Connection state: {old_state.value} → {new_state.value}")
    
    async def _dispatch_message(self, message_dict: Dict[str, Any]) -> None:
        """Dispatch message to all registered handlers."""
        for handler in self._message_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message_dict)
                else:
                    handler(message_dict)
            except Exception as e:
                logger.exception(f"Error in message handler: {e}")
                await self._dispatch_error(e)
    
    async def _dispatch_error(self, error: Exception) -> None:
        """Dispatch error to all registered handlers."""
        for handler in self._error_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(error)
                else:
                    handler(error)
            except Exception as e:
                logger.exception(f"Error in error handler: {e}")
    
    async def _receive_messages(self) -> None:
        """
        Listen for incoming messages and dispatch them.
        
        Runs until connection is closed.
        """
        try:
            if not self._websocket:
                return
            
            async for raw_message in self._websocket:
                try:
                    # Parse JSON
                    message_dict = json.loads(raw_message)
                    
                    # Validate message structure
                    message = Message(**message_dict)
                    
                    # For signaling messages, verify signature
                    if message.type in [
                        MessageType.OFFER,
                        MessageType.ANSWER,
                        MessageType.ICE_CANDIDATE,
                    ]:
                        # Signature verification would happen here
                        # For now, just validate structure
                        pass
                    
                    # Dispatch to handlers
                    await self._dispatch_message(message_dict)
                    
                except json.JSONDecodeError as e:
                    error = ConnectionError(f"Invalid JSON received: {e}")
                    await self._dispatch_error(error)
                except Exception as e:
                    error = ProtocolError(f"Error processing message: {e}")
                    await self._dispatch_error(error)
        
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            await self._set_state(ConnectionState.DISCONNECTED)
        except Exception as e:
            logger.exception(f"Error in message receive loop: {e}")
            await self._dispatch_error(e)
            await self._set_state(ConnectionState.ERROR)
    
    async def connect(self, timeout: float = 10.0) -> None:
        """
        Connect to Gateway and start receiving messages.
        
        Args:
            timeout: Connection timeout in seconds
        
        Raises:
            ConnectionError: If connection fails
        """
        if self.state == ConnectionState.CONNECTED:
            return
        
        if self.state == ConnectionState.CONNECTING:
            logger.warning("Connection already in progress")
            return
        
        await self._set_state(ConnectionState.CONNECTING)
        
        reconnect_count = 0
        current_interval = self.reconnect_interval
        
        while True:
            try:
                logger.debug(f"Connecting to {self.gateway_url}...")
                
                # Connect to WebSocket
                async with asyncio.timeout(timeout):
                    self._websocket = await websockets.connect(
                        self.gateway_url,
                        subprotocols=["ioap.v1"],
                    )
                
                await self._set_state(ConnectionState.CONNECTED)
                logger.info(f"Connected to Gateway at {self.gateway_url}")
                
                # Start message receive loop
                if self._receive_task:
                    self._receive_task.cancel()
                self._receive_task = asyncio.create_task(self._receive_messages())
                
                return
            
            except (websockets.exceptions.WebSocketException, asyncio.TimeoutError) as e:
                reconnect_count += 1
                
                # Check if we should keep trying
                if self.max_reconnect_attempts > 0 and reconnect_count > self.max_reconnect_attempts:
                    error = ConnectionError(
                        f"Failed to connect after {reconnect_count} attempts: {e}"
                    )
                    await self._set_state(ConnectionState.ERROR)
                    await self._dispatch_error(error)
                    raise error
                
                logger.warning(
                    f"Connection failed (attempt {reconnect_count}): {e}. "
                    f"Retrying in {current_interval}s..."
                )
                
                await asyncio.sleep(current_interval)
                current_interval = min(current_interval * 2, 30.0)  # Exponential backoff, max 30s
            
            except Exception as e:
                error = ConnectionError(f"Unexpected connection error: {e}")
                await self._set_state(ConnectionState.ERROR)
                await self._dispatch_error(error)
                raise error
    
    async def disconnect(self) -> None:
        """Gracefully disconnect from Gateway."""
        if self.state == ConnectionState.DISCONNECTED:
            return
        
        await self._set_state(ConnectionState.DISCONNECTING)
        
        try:
            # Cancel receive task
            if self._receive_task and not self._receive_task.done():
                self._receive_task.cancel()
                try:
                    await self._receive_task
                except asyncio.CancelledError:
                    pass
            
            # Cancel reconnect task
            if self._reconnect_task and not self._reconnect_task.done():
                self._reconnect_task.cancel()
                try:
                    await self._reconnect_task
                except asyncio.CancelledError:
                    pass
            
            # Close WebSocket
            if self._websocket:
                await self._websocket.close()
                self._websocket = None
            
            self._registered = False
            await self._set_state(ConnectionState.DISCONNECTED)
            logger.info("Disconnected from Gateway")
        
        except Exception as e:
            logger.exception(f"Error during disconnect: {e}")
            await self._set_state(ConnectionState.ERROR)
    
    async def register(self, public_key: str) -> None:
        """
        Register with Gateway.
        
        Args:
            public_key: Base58-encoded Ed25519 public key
        
        Raises:
            ConnectionError: If not connected
            ProtocolError: If registration fails
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to Gateway")
        
        # Create REGISTER message
        payload = RegisterPayload(public_key=public_key)
        message = Message(
            id=str(uuid.uuid4()),
            type=MessageType.REGISTER,
            **{"from": self.agent_did, "to": self.agent_did},  # Self-registration
            payload=payload.model_dump(),
            timestamp=datetime.utcnow(),
            signature="",  # Will be filled in below
        )
        
        # Sign message - need to convert to dict with ISO formatted timestamp
        message_dict = message.model_dump(exclude={'signature'}, by_alias=True)
        message_dict['timestamp'] = message_dict['timestamp'].isoformat()
        signature = MessageSigner.sign_message(message_dict, self.did_key)
        message.signature = signature
        
        # Send message
        send_dict = message.model_dump(by_alias=True)
        send_dict['timestamp'] = send_dict['timestamp'].isoformat()
        await self.send(send_dict)
        self._registered = True
        logger.info(f"Registered with Gateway as {self.agent_did}")
    
    async def send(self, message: Dict[str, Any]) -> None:
        """
        Send a message through Gateway.
        
        Args:
            message: Message dict (will be validated against Message schema)
        
        Raises:
            ConnectionError: If not connected
            ProtocolError: If message validation fails
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to Gateway")
        
        try:
            # Validate message structure
            msg_obj = Message(**message)
            
            # Serialize and send
            json_str = MessageSerializer.to_json(msg_obj.model_dump(by_alias=True))
            
            if not self._websocket:
                raise ConnectionError("WebSocket not available")
            
            await self._websocket.send(json_str)
            logger.debug(f"Sent {msg_obj.type.value} message")
        
        except Exception as e:
            error = ProtocolError(f"Failed to send message: {e}")
            await self._dispatch_error(error)
            raise error
    
    async def __aenter__(self):
        """Context manager entry - connect to Gateway."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - disconnect from Gateway."""
        await self.disconnect()

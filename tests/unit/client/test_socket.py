"""
Unit tests for GatewayClient WebSocket client.

Tests:
- Connection management (connect, disconnect, state transitions)
- Message handling (serialization, dispatch, validation)
- Registration with Gateway
- Error handling and handler dispatch
- Context manager usage
"""

import pytest
import asyncio
import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch, call
from datetime import datetime

from aiconexus.client.socket import GatewayClient, ConnectionState
from aiconexus.protocol.models import Message, MessageType, RegisterPayload
from aiconexus.protocol.security import DIDKey, MessageSigner
from aiconexus.protocol.errors import ConnectionError, ProtocolError


@pytest.fixture
def did_key() -> DIDKey:
    """Generate test DID key."""
    return DIDKey.generate()


@pytest.fixture
def client(did_key: DIDKey) -> GatewayClient:
    """Create test Gateway client."""
    return GatewayClient(
        gateway_url="ws://localhost:8000/ws",
        did_key=did_key,
        reconnect_interval=0.1,
        max_reconnect_attempts=1,
    )


class TestConnectionState:
    """Test ConnectionState enum."""
    
    def test_connection_state_values(self):
        """Test that ConnectionState has all required values."""
        assert ConnectionState.DISCONNECTED.value == "DISCONNECTED"
        assert ConnectionState.CONNECTING.value == "CONNECTING"
        assert ConnectionState.CONNECTED.value == "CONNECTED"
        assert ConnectionState.DISCONNECTING.value == "DISCONNECTING"
        assert ConnectionState.ERROR.value == "ERROR"


class TestGatewayClientInit:
    """Test GatewayClient initialization."""
    
    def test_init(self, client: GatewayClient, did_key: DIDKey):
        """Test client initialization."""
        assert client.gateway_url == "ws://localhost:8000/ws"
        assert client.agent_did == did_key.did
        assert client.state == ConnectionState.DISCONNECTED
        assert client.is_connected is False
        assert client._message_handlers == []
        assert client._error_handlers == []
    
    def test_is_connected_when_disconnected(self, client: GatewayClient):
        """Test is_connected property when disconnected."""
        assert client.is_connected is False
    
    def test_custom_reconnect_settings(self, did_key: DIDKey):
        """Test custom reconnection settings."""
        client = GatewayClient(
            gateway_url="ws://localhost:8000/ws",
            did_key=did_key,
            reconnect_interval=2.0,
            max_reconnect_attempts=10,
        )
        assert client.reconnect_interval == 2.0
        assert client.max_reconnect_attempts == 10


class TestHandlerRegistration:
    """Test message and error handler registration."""
    
    def test_on_message_handler(self, client: GatewayClient):
        """Test registering message handler."""
        handler = AsyncMock()
        client.on_message(handler)
        assert handler in client._message_handlers
    
    def test_on_error_handler(self, client: GatewayClient):
        """Test registering error handler."""
        handler = AsyncMock()
        client.on_error(handler)
        assert handler in client._error_handlers
    
    def test_multiple_handlers(self, client: GatewayClient):
        """Test registering multiple handlers."""
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        
        client.on_message(handler1)
        client.on_message(handler2)
        
        assert len(client._message_handlers) == 2


@pytest.mark.asyncio
class TestDispatchMessage:
    """Test message dispatch to handlers."""
    
    async def test_dispatch_message_to_single_handler(self, client: GatewayClient):
        """Test dispatching message to single handler."""
        handler = AsyncMock()
        client.on_message(handler)
        
        message = {"type": "PING"}
        await client._dispatch_message(message)
        
        handler.assert_called_once_with(message)
    
    async def test_dispatch_message_to_multiple_handlers(self, client: GatewayClient):
        """Test dispatching message to multiple handlers."""
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        client.on_message(handler1)
        client.on_message(handler2)
        
        message = {"type": "PONG"}
        await client._dispatch_message(message)
        
        handler1.assert_called_once_with(message)
        handler2.assert_called_once_with(message)
    
    async def test_dispatch_message_with_sync_handler(self, client: GatewayClient):
        """Test dispatching message to sync handler."""
        handler = MagicMock()  # Sync function
        client.on_message(handler)
        
        message = {"type": "TEST"}
        await client._dispatch_message(message)
        
        handler.assert_called_once_with(message)
    
    async def test_dispatch_message_handler_exception(self, client: GatewayClient):
        """Test that handler exceptions are caught and dispatched as errors."""
        message_handler = AsyncMock(side_effect=RuntimeError("Test error"))
        error_handler = AsyncMock()
        
        client.on_message(message_handler)
        client.on_error(error_handler)
        
        message = {"type": "TEST"}
        await client._dispatch_message(message)
        
        # Error handler should be called
        assert error_handler.called


@pytest.mark.asyncio
class TestDispatchError:
    """Test error dispatch to handlers."""
    
    async def test_dispatch_error_to_single_handler(self, client: GatewayClient):
        """Test dispatching error to single handler."""
        handler = AsyncMock()
        client.on_error(handler)
        
        error = RuntimeError("Test error")
        await client._dispatch_error(error)
        
        handler.assert_called_once_with(error)
    
    async def test_dispatch_error_to_multiple_handlers(self, client: GatewayClient):
        """Test dispatching error to multiple handlers."""
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        client.on_error(handler1)
        client.on_error(handler2)
        
        error = ConnectionError("Connection failed")
        await client._dispatch_error(error)
        
        handler1.assert_called_once_with(error)
        handler2.assert_called_once_with(error)


@pytest.mark.asyncio
class TestRegister:
    """Test agent registration."""
    
    async def test_register_when_connected(self, client: GatewayClient):
        """Test registration when connected."""
        # Mock WebSocket
        client._websocket = AsyncMock()
        client.state = ConnectionState.CONNECTED
        
        public_key = "test_public_key"
        await client.register(public_key)
        
        # Should send REGISTER message
        assert client._websocket.send.called
        
        # Check that message was sent
        sent_data = client._websocket.send.call_args[0][0]
        message_dict = json.loads(sent_data)
        assert message_dict["type"] == "REGISTER"
        assert message_dict["from"] == client.agent_did
        assert message_dict["payload"]["public_key"] == public_key
    
    async def test_register_when_disconnected(self, client: GatewayClient):
        """Test registration when disconnected raises error."""
        client.state = ConnectionState.DISCONNECTED
        
        with pytest.raises(ConnectionError):
            await client.register("test_key")
    
    async def test_register_sets_registered_flag(self, client: GatewayClient):
        """Test that register sets _registered flag."""
        client._websocket = AsyncMock()
        client.state = ConnectionState.CONNECTED
        
        assert client._registered is False
        await client.register("test_key")
        assert client._registered is True


@pytest.mark.asyncio
class TestSend:
    """Test message sending."""
    
    async def test_send_when_connected(self, client: GatewayClient):
        """Test sending message when connected."""
        client._websocket = AsyncMock()
        client.state = ConnectionState.CONNECTED
        
        message = {
            "id": str(uuid.uuid4()),
            "type": "PING",
            "from": client.agent_did,
            "to": client.agent_did,
            "payload": {},
            "timestamp": datetime.utcnow().isoformat(),
            "signature": "test_sig",
        }
        
        await client.send(message)
        
        # Should have called send on WebSocket
        assert client._websocket.send.called
    
    async def test_send_when_disconnected(self, client: GatewayClient):
        """Test sending when disconnected raises error."""
        client.state = ConnectionState.DISCONNECTED
        
        message = {"type": "PING"}
        
        with pytest.raises(ConnectionError):
            await client.send(message)
    
    async def test_send_validates_message(self, client: GatewayClient):
        """Test that send validates message structure."""
        client._websocket = AsyncMock()
        client.state = ConnectionState.CONNECTED
        
        # Invalid message (missing required fields)
        invalid_message = {"type": "INVALID_TYPE"}
        
        with pytest.raises(ProtocolError):
            await client.send(invalid_message)
    
    async def test_send_dispatches_error_on_failure(self, client: GatewayClient):
        """Test that send errors are dispatched to error handlers."""
        # Make websocket.send() fail
        ws_mock = AsyncMock()
        ws_mock.send = AsyncMock(side_effect=RuntimeError("Network error"))
        client._websocket = ws_mock
        client.state = ConnectionState.CONNECTED
        
        error_handler = AsyncMock()
        client.on_error(error_handler)
        
        message = {
            "id": str(uuid.uuid4()),
            "type": "PING",
            "from": client.agent_did,
            "to": client.agent_did,
            "payload": {},
            "timestamp": datetime.utcnow().isoformat(),
            "signature": "test_sig",
        }
        
        with pytest.raises(ProtocolError):
            await client.send(message)
        
        # Error handler should have been called
        assert error_handler.called


@pytest.mark.asyncio
class TestContextManager:
    """Test context manager functionality."""
    
    async def test_context_manager_connect_disconnect(self, client: GatewayClient):
        """Test using client as context manager."""
        # Mock connect and disconnect
        client.connect = AsyncMock()
        client.disconnect = AsyncMock()
        
        async with client:
            pass
        
        client.connect.assert_called_once()
        client.disconnect.assert_called_once()
    
    async def test_context_manager_returns_self(self, client: GatewayClient):
        """Test that context manager returns self."""
        client.connect = AsyncMock()
        client.disconnect = AsyncMock()
        
        async with client as c:
            assert c is client


@pytest.mark.asyncio
class TestDisconnect:
    """Test disconnection."""
    
    async def test_disconnect_when_connected(self, client: GatewayClient):
        """Test disconnecting when connected."""
        ws_mock = AsyncMock()
        task_mock = AsyncMock()
        task_mock.done.return_value = False
        
        client._websocket = ws_mock
        client._receive_task = task_mock
        client.state = ConnectionState.CONNECTED
        
        await client.disconnect()
        
        # Should close WebSocket
        ws_mock.close.assert_called_once()
        assert client.state == ConnectionState.DISCONNECTED
        assert client._registered is False
    
    async def test_disconnect_when_already_disconnected(self, client: GatewayClient):
        """Test disconnecting when already disconnected."""
        client.state = ConnectionState.DISCONNECTED
        
        # Should not raise
        await client.disconnect()
        
        assert client.state == ConnectionState.DISCONNECTED
    
    async def test_disconnect_cancels_receive_task(self, client: GatewayClient):
        """Test that disconnect cancels receive task."""
        ws_mock = AsyncMock()
        # Create a real Task mock that behaves like asyncio.Task
        task_mock = MagicMock()
        task_mock.done.return_value = False
        task_mock.__bool__.return_value = True  # Make the mock truthy
        
        client._websocket = ws_mock
        client._receive_task = task_mock
        client.state = ConnectionState.CONNECTED
        
        await client.disconnect()
        
        # Verify cancel was called
        task_mock.cancel.assert_called_once()


@pytest.mark.asyncio
class TestSetState:
    """Test connection state management."""
    
    async def test_set_state_updates_state(self, client: GatewayClient):
        """Test that set_state updates the state."""
        assert client.state == ConnectionState.DISCONNECTED
        
        await client._set_state(ConnectionState.CONNECTING)
        assert client.state == ConnectionState.CONNECTING
        
        await client._set_state(ConnectionState.CONNECTED)
        assert client.state == ConnectionState.CONNECTED

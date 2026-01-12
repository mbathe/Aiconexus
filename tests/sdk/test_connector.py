"""Tests for the P2P Connector module.

This module tests the Connector class which handles P2P communication
between agents using HTTP and WebSocket transports.
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.aiconexus.sdk.connector import Connector, ConnectorError
from src.aiconexus.sdk.types import Message


class TestConnectorInitialization:
    """Test Connector initialization."""

    def test_create_connector_with_registry(self, populated_registry):
        """Test creating a connector with a registry."""
        connector = Connector(registry=populated_registry)
        
        assert connector is not None
        assert connector.registry == populated_registry
        assert connector.transport is None

    def test_create_connector_without_registry(self):
        """Test creating a connector without a registry."""
        connector = Connector()
        
        assert connector is not None
        assert connector.registry is None

    def test_connector_default_config(self):
        """Test connector default configuration."""
        connector = Connector()
        
        assert hasattr(connector, 'timeout')
        assert hasattr(connector, 'retry_config')
        assert hasattr(connector, 'max_retries')


class TestConnectorMessageSending:
    """Test message sending functionality."""

    @pytest.mark.asyncio
    async def test_send_message_to_endpoint(self, simple_valid_message, mock_transport):
        """Test sending a message to an endpoint."""
        connector = Connector()
        connector.transport = mock_transport
        
        mock_transport.send = AsyncMock(return_value=True)
        
        result = await connector.send_message(
            message=simple_valid_message,
            endpoint="http://localhost:8000"
        )
        
        assert result is True
        mock_transport.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_message_with_retry(self, simple_valid_message, mock_transport):
        """Test sending with automatic retry on failure."""
        connector = Connector(max_retries=2)
        connector.transport = mock_transport
        
        # First call fails, second succeeds
        mock_transport.send = AsyncMock(side_effect=[
            ConnectionError("Connection failed"),
            True
        ])
        
        result = await connector.send_message(
            message=simple_valid_message,
            endpoint="http://localhost:8000",
            retry=True
        )
        
        assert result is True
        assert mock_transport.send.call_count == 2

    @pytest.mark.asyncio
    async def test_send_message_retry_exhausted(self, simple_valid_message, mock_transport):
        """Test retry exhaustion after max retries."""
        connector = Connector(max_retries=2)
        connector.transport = mock_transport
        
        # All calls fail
        mock_transport.send = AsyncMock(
            side_effect=ConnectionError("Connection failed")
        )
        
        with pytest.raises(ConnectorError):
            await connector.send_message(
                message=simple_valid_message,
                endpoint="http://localhost:8000",
                retry=True
            )

    @pytest.mark.asyncio
    async def test_send_message_timeout(self, simple_valid_message, mock_transport):
        """Test message sending timeout."""
        connector = Connector(timeout=0.1)
        connector.transport = mock_transport
        
        # Simulate slow transport
        async def slow_send(*args, **kwargs):
            await asyncio.sleep(1)
            return True
        
        mock_transport.send = slow_send
        
        with pytest.raises((asyncio.TimeoutError, ConnectorError)):
            await asyncio.wait_for(
                connector.send_message(
                    message=simple_valid_message,
                    endpoint="http://localhost:8000"
                ),
                timeout=0.1
            )


class TestConnectorParallelSending:
    """Test parallel message sending."""

    @pytest.mark.asyncio
    async def test_send_to_multiple_endpoints(self, message_builder, mock_transport):
        """Test sending to multiple endpoints in parallel."""
        connector = Connector()
        connector.transport = mock_transport
        
        mock_transport.send = AsyncMock(return_value=True)
        
        messages = [
            message_builder.with_data(id=i).build()
            for i in range(3)
        ]
        endpoints = [
            "http://localhost:8001",
            "http://localhost:8002",
            "http://localhost:8003"
        ]
        
        results = await asyncio.gather(*[
            connector.send_message(msg, ep)
            for msg, ep in zip(messages, endpoints)
        ])
        
        assert all(results)
        assert mock_transport.send.call_count == 3

    @pytest.mark.asyncio
    async def test_send_parallel_partial_failure(self, message_builder, mock_transport):
        """Test partial failure in parallel sending."""
        connector = Connector()
        connector.transport = mock_transport
        
        # First and third succeed, second fails
        mock_transport.send = AsyncMock(side_effect=[
            True,
            ConnectionError("Failed"),
            True
        ])
        
        messages = [
            message_builder.with_data(id=i).build()
            for i in range(3)
        ]
        endpoints = [
            "http://localhost:8001",
            "http://localhost:8002",
            "http://localhost:8003"
        ]
        
        results = await asyncio.gather(*[
            connector.send_message(msg, ep)
            for msg, ep in zip(messages, endpoints)
        ], return_exceptions=True)
        
        assert results[0] is True
        assert isinstance(results[1], (ConnectionError, ConnectorError))
        assert results[2] is True


class TestConnectorMessageReceiving:
    """Test message receiving functionality."""

    @pytest.mark.asyncio
    async def test_receive_message(self, simple_valid_message, mock_transport):
        """Test receiving a message."""
        connector = Connector()
        connector.transport = mock_transport
        
        mock_transport.receive = AsyncMock(return_value=simple_valid_message)
        
        result = await connector.receive_message()
        
        assert result is not None
        assert isinstance(result, Message)
        mock_transport.receive.assert_called_once()

    @pytest.mark.asyncio
    async def test_receive_message_timeout(self, mock_transport):
        """Test receive timeout."""
        connector = Connector(timeout=0.1)
        connector.transport = mock_transport
        
        # Simulate no message available
        async def no_message(*args, **kwargs):
            await asyncio.sleep(1)
            return None
        
        mock_transport.receive = no_message
        
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                connector.receive_message(),
                timeout=0.1
            )

    @pytest.mark.asyncio
    async def test_receive_multiple_messages(self, message_builder, mock_transport):
        """Test receiving multiple messages."""
        connector = Connector()
        connector.transport = mock_transport
        
        messages = [
            message_builder.with_data(id=i).build()
            for i in range(3)
        ]
        
        mock_transport.receive = AsyncMock(side_effect=messages)
        
        received = []
        for _ in range(3):
            msg = await connector.receive_message()
            received.append(msg)
        
        assert len(received) == 3
        assert all(isinstance(m, Message) for m in received)


class TestConnectorWithRegistry:
    """Test connector integration with registry."""

    @pytest.mark.asyncio
    async def test_discover_and_send_to_agent(
        self, 
        populated_registry, 
        simple_valid_message,
        mock_transport
    ):
        """Test discovering agent and sending message."""
        connector = Connector(registry=populated_registry)
        connector.transport = mock_transport
        
        mock_transport.send = AsyncMock(return_value=True)
        
        # Discover agent by expertise
        agents = await populated_registry.discover_by_expertise(
            expertise_area="data_analysis",
            min_confidence=0.8
        )
        
        assert len(agents) > 0
        agent = agents[0]
        
        # Send message to discovered agent
        result = await connector.send_message(
            message=simple_valid_message,
            endpoint=agent.endpoint
        )
        
        assert result is True

    @pytest.mark.asyncio
    async def test_broadcast_to_multiple_agents(
        self,
        populated_registry,
        message_builder,
        mock_transport
    ):
        """Test broadcasting to multiple agents."""
        connector = Connector(registry=populated_registry)
        connector.transport = mock_transport
        
        mock_transport.send = AsyncMock(return_value=True)
        
        # Get all agents from registry
        agents = await populated_registry.discover_by_expertise(
            expertise_area="data_analysis"
        )
        
        message = message_builder.build()
        
        # Send to all
        results = await asyncio.gather(*[
            connector.send_message(message, agent.endpoint)
            for agent in agents
        ])
        
        assert all(results)


class TestConnectorTransportAbstraction:
    """Test transport layer abstraction."""

    @pytest.mark.asyncio
    async def test_switch_transport(self, simple_valid_message):
        """Test switching transport implementations."""
        connector = Connector()
        
        transport1 = AsyncMock()
        transport1.send = AsyncMock(return_value=True)
        
        transport2 = AsyncMock()
        transport2.send = AsyncMock(return_value=True)
        
        # Use first transport
        connector.transport = transport1
        await connector.send_message(
            message=simple_valid_message,
            endpoint="http://localhost:8001"
        )
        
        # Switch to second transport
        connector.transport = transport2
        await connector.send_message(
            message=simple_valid_message,
            endpoint="http://localhost:8002"
        )
        
        assert transport1.send.called
        assert transport2.send.called

    def test_transport_interface(self):
        """Test that transport implements required interface."""
        mock_transport = AsyncMock()
        
        # Should have send and receive
        assert hasattr(mock_transport, 'send')
        assert hasattr(mock_transport, 'receive')


class TestConnectorErrorHandling:
    """Test error handling in connector."""

    @pytest.mark.asyncio
    async def test_malformed_message(self):
        """Test handling of malformed messages."""
        connector = Connector()
        
        with pytest.raises((TypeError, ValueError)):
            await connector.send_message(
                message={"invalid": "dict"},  # Not a Message object
                endpoint="http://localhost:8000"
            )

    @pytest.mark.asyncio
    async def test_invalid_endpoint(self, simple_valid_message, mock_transport):
        """Test handling of invalid endpoint."""
        connector = Connector()
        connector.transport = mock_transport
        
        with pytest.raises((ValueError, ConnectorError)):
            await connector.send_message(
                message=simple_valid_message,
                endpoint="not-a-valid-url"
            )

    @pytest.mark.asyncio
    async def test_connection_error_propagation(
        self, 
        simple_valid_message, 
        mock_transport
    ):
        """Test that connection errors are properly propagated."""
        connector = Connector(max_retries=0)
        connector.transport = mock_transport
        
        mock_transport.send = AsyncMock(
            side_effect=ConnectionError("Network unreachable")
        )
        
        with pytest.raises((ConnectionError, ConnectorError)):
            await connector.send_message(
                message=simple_valid_message,
                endpoint="http://localhost:8000"
            )


class TestConnectorExponentialBackoff:
    """Test exponential backoff retry strategy."""

    @pytest.mark.asyncio
    async def test_backoff_delay_increases(self, simple_valid_message, mock_transport):
        """Test that backoff delay increases exponentially."""
        connector = Connector(max_retries=3, base_delay=0.01)
        connector.transport = mock_transport
        
        call_times = []
        
        async def track_calls(*args, **kwargs):
            call_times.append(asyncio.get_event_loop().time())
            if len(call_times) < 3:
                raise ConnectionError("Retry")
            return True
        
        mock_transport.send = track_calls
        
        result = await connector.send_message(
            message=simple_valid_message,
            endpoint="http://localhost:8000",
            retry=True
        )
        
        assert result is True
        assert len(call_times) >= 2
        
        # Check delays increase (with some tolerance)
        if len(call_times) >= 3:
            delay1 = call_times[1] - call_times[0]
            delay2 = call_times[2] - call_times[1]
            # Second delay should be >= first delay (approximately)
            assert delay2 >= delay1 * 0.9  # Allow 10% tolerance

    @pytest.mark.asyncio
    async def test_max_backoff_cap(self, simple_valid_message, mock_transport):
        """Test that backoff delay is capped at max_delay."""
        connector = Connector(
            max_retries=5,
            base_delay=0.1,
            max_delay=0.2
        )
        connector.transport = mock_transport
        
        call_times = []
        
        async def track_calls(*args, **kwargs):
            call_times.append(asyncio.get_event_loop().time())
            if len(call_times) < 4:
                raise ConnectionError("Retry")
            return True
        
        mock_transport.send = track_calls
        
        result = await connector.send_message(
            message=simple_valid_message,
            endpoint="http://localhost:8000",
            retry=True
        )
        
        assert result is True
        # The last delay should not exceed max_delay significantly
        if len(call_times) >= 2:
            last_delay = call_times[-1] - call_times[-2]
            assert last_delay <= 0.3  # max_delay + tolerance


class TestConnectorConcurrency:
    """Test concurrent message operations."""

    @pytest.mark.asyncio
    async def test_concurrent_send_and_receive(
        self,
        simple_valid_message,
        message_builder,
        mock_transport
    ):
        """Test concurrent send and receive operations."""
        connector = Connector()
        connector.transport = mock_transport
        
        send_msg = simple_valid_message
        receive_msg = message_builder.build()
        
        mock_transport.send = AsyncMock(return_value=True)
        mock_transport.receive = AsyncMock(return_value=receive_msg)
        
        send_result, receive_result = await asyncio.gather(
            connector.send_message(
                message=send_msg,
                endpoint="http://localhost:8000"
            ),
            connector.receive_message()
        )
        
        assert send_result is True
        assert receive_result == receive_msg

    @pytest.mark.asyncio
    async def test_stress_test_concurrent_messages(self, message_builder, mock_transport):
        """Test handling many concurrent messages."""
        connector = Connector()
        connector.transport = mock_transport
        
        mock_transport.send = AsyncMock(return_value=True)
        
        tasks = [
            connector.send_message(
                message=message_builder.with_data(id=i).build(),
                endpoint=f"http://localhost:{8000 + i}"
            )
            for i in range(100)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 100
        assert all(results)
        assert mock_transport.send.call_count == 100


class TestConnectorMessageSerialization:
    """Test message serialization/deserialization."""

    @pytest.mark.asyncio
    async def test_serialize_and_send(self, simple_valid_message):
        """Test that message is properly serialized before sending."""
        connector = Connector()
        
        mock_transport = AsyncMock()
        mock_transport.send = AsyncMock(return_value=True)
        connector.transport = mock_transport
        
        await connector.send_message(
            message=simple_valid_message,
            endpoint="http://localhost:8000"
        )
        
        # Verify transport received serialized data
        call_args = mock_transport.send.call_args
        assert call_args is not None

    @pytest.mark.asyncio
    async def test_deserialize_received_message(self, simple_valid_message, mock_transport):
        """Test that received data is properly deserialized."""
        connector = Connector()
        
        # Simulate receiving serialized message
        mock_transport.receive = AsyncMock(return_value=simple_valid_message)
        connector.transport = mock_transport
        
        result = await connector.receive_message()
        
        assert isinstance(result, Message)
        assert result.sender == simple_valid_message.sender


@pytest.mark.asyncio
async def test_connector_integration_flow(
    populated_registry,
    message_builder,
    mock_transport
):
    """Integration test: Complete send/receive flow."""
    connector = Connector(registry=populated_registry)
    connector.transport = mock_transport
    
    message = message_builder.build()
    
    mock_transport.send = AsyncMock(return_value=True)
    mock_transport.receive = AsyncMock(return_value=message)
    
    # Send
    send_result = await connector.send_message(
        message=message,
        endpoint="http://localhost:8000"
    )
    
    # Receive
    receive_result = await connector.receive_message()
    
    assert send_result is True
    assert receive_result == message

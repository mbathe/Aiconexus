"""
Pytest fixtures for integration tests.

Provides:
- Running Gateway server instance
- Connected client instances
- Test DIDs and credentials
"""

import pytest
import asyncio
from typing import Tuple, List
from unittest.mock import AsyncMock

from gateway.server import create_app
from aiconexus.client.socket import GatewayClient
from aiconexus.protocol.security import DIDKey
from fastapi.testclient import TestClient
from httpx import AsyncClient


@pytest.fixture
async def gateway_app():
    """Create Gateway FastAPI app for testing."""
    return create_app(agent_timeout=30, cleanup_interval=10)


@pytest.fixture
def test_did_keys() -> List[DIDKey]:
    """Generate test DID keys for agents."""
    return [DIDKey.generate() for _ in range(5)]


@pytest.fixture
def test_client_sync(gateway_app):
    """Create sync test client for Gateway HTTP endpoints."""
    return TestClient(gateway_app)


@pytest.fixture
async def gateway_server_running(gateway_app):
    """
    Start Gateway server for testing.
    
    Note: This is a complex fixture that would need uvicorn or similar
    to run the server. For now, it's a placeholder for real server testing.
    """
    # In a real scenario, you'd start uvicorn programmatically
    # For unit tests, we'll use direct async testing
    yield gateway_app


@pytest.fixture
async def connected_client(test_did_keys):
    """Create a connected client for testing."""
    did_key = test_did_keys[0]
    
    # Note: This would need a real server running
    # For integration tests, we'll test the components separately first
    client = GatewayClient(
        gateway_url="ws://localhost:8000/ws",
        did_key=did_key,
        reconnect_interval=0.1,
        max_reconnect_attempts=1,
    )
    
    yield client
    
    # Cleanup
    if client.is_connected:
        await client.disconnect()


@pytest.fixture
async def two_connected_clients(test_did_keys):
    """Create two connected clients for message routing tests."""
    client_a = GatewayClient(
        gateway_url="ws://localhost:8000/ws",
        did_key=test_did_keys[0],
        reconnect_interval=0.1,
        max_reconnect_attempts=1,
    )
    
    client_b = GatewayClient(
        gateway_url="ws://localhost:8000/ws",
        did_key=test_did_keys[1],
        reconnect_interval=0.1,
        max_reconnect_attempts=1,
    )
    
    yield client_a, client_b
    
    # Cleanup
    if client_a.is_connected:
        await client_a.disconnect()
    if client_b.is_connected:
        await client_b.disconnect()

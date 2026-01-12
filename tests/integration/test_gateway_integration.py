"""
Integration tests for Gateway and Client communication.

Tests:
- HTTP endpoints (health, agents list)
- Message routing between connected agents
- Agent presence tracking
- Timeout and cleanup
"""

import pytest
import json
import asyncio
from datetime import datetime

from fastapi.testclient import TestClient
from gateway.server import create_app, GatewayServer
from gateway.registry import RegistryEntry
from aiconexus.protocol.models import Message, MessageType
from aiconexus.protocol.security import DIDKey


@pytest.fixture
def test_app():
    """Create test Gateway app."""
    return create_app(agent_timeout=30, cleanup_interval=10)


@pytest.fixture
def test_client(test_app):
    """Create test client for Gateway."""
    return TestClient(test_app)


class TestGatewayEndpoints:
    """Test Gateway HTTP endpoints."""
    
    def test_health_check(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "connected_agents" in data
        assert "timestamp" in data
    
    def test_list_agents_empty(self, test_client):
        """Test listing agents when none connected."""
        response = test_client.get("/agents")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["agents"] == []
    
    def test_list_agents_after_registration(self, test_client):
        """Test listing agents after one registers."""
        # This test would need a real WebSocket connection
        # For now, we test the registry directly
        pass


class TestRegistryIntegration:
    """Test registry with real data structures."""
    
    @pytest.mark.asyncio
    async def test_register_and_list_agents(self):
        """Test registering agents and listing them."""
        # Create a gateway server instance
        gateway = GatewayServer(agent_timeout=30)
        
        # Register some agents
        agent1_did = "did:key:agent1"
        agent2_did = "did:key:agent2"
        
        entry1 = RegistryEntry(
            agent_did=agent1_did,
            public_key="key1",
            connected_at=datetime.utcnow(),
            ip_address="127.0.0.1"
        )
        
        entry2 = RegistryEntry(
            agent_did=agent2_did,
            public_key="key2",
            connected_at=datetime.utcnow(),
            ip_address="127.0.0.2"
        )
        
        await gateway.registry.register(agent1_did, entry1)
        await gateway.registry.register(agent2_did, entry2)
        
        # List agents
        agents = await gateway.registry.list_agents()
        assert len(agents) == 2
        agent_dids = [agent.agent_did for agent in agents]
        assert agent1_did in agent_dids
        assert agent2_did in agent_dids
    
    @pytest.mark.asyncio
    async def test_agent_registration_flow(self):
        """Test complete agent registration flow."""
        gateway = GatewayServer(agent_timeout=30)
        
        # Register agent
        did_key = DIDKey.generate()
        entry = RegistryEntry(
            agent_did=did_key.did,
            public_key=did_key.public_key_base58,
            connected_at=datetime.utcnow(),
            ip_address="192.168.1.1"
        )
        
        await gateway.registry.register(did_key.did, entry)
        
        # Verify agent is online
        agent = await gateway.registry.get(did_key.did)
        assert agent is not None
        assert agent.agent_did == did_key.did
        assert agent.public_key == did_key.public_key_base58
        assert agent.ip_address == "192.168.1.1"
        
        # Unregister agent
        removed = await gateway.registry.unregister(did_key.did)
        assert removed is True
        
        # Verify agent is offline
        agent = await gateway.registry.get(did_key.did)
        assert agent is None


class TestMessageValidation:
    """Test message validation and structure."""
    
    def test_register_message_structure(self):
        """Test REGISTER message structure."""
        did_key = DIDKey.generate()
        
        # Create valid REGISTER message
        message = {
            "id": "test_id_1",
            "type": "REGISTER",
            "from": did_key.did,
            "to": did_key.did,
            "payload": {
                "public_key": did_key.public_key_base58
            },
            "timestamp": datetime.utcnow().isoformat(),
            "signature": "test_signature",
        }
        
        # Should validate without errors
        msg_obj = Message(**message)
        assert msg_obj.type == MessageType.REGISTER
        assert msg_obj.from_did == did_key.did
    
    def test_offer_message_structure(self):
        """Test OFFER message structure."""
        did_key_a = DIDKey.generate()
        did_key_b = DIDKey.generate()
        
        message = {
            "id": "test_id_2",
            "type": "OFFER",
            "from": did_key_a.did,
            "to": did_key_b.did,
            "payload": {
                "sdp": "v=0\r\no=..."
            },
            "timestamp": datetime.utcnow().isoformat(),
            "signature": "test_signature",
        }
        
        msg_obj = Message(**message)
        assert msg_obj.type == MessageType.OFFER
        assert msg_obj.from_did == did_key_a.did
        assert msg_obj.to_did == did_key_b.did
    
    def test_answer_message_structure(self):
        """Test ANSWER message structure."""
        did_key_a = DIDKey.generate()
        did_key_b = DIDKey.generate()
        
        message = {
            "id": "test_id_3",
            "type": "ANSWER",
            "from": did_key_b.did,
            "to": did_key_a.did,
            "payload": {
                "sdp": "v=0\r\no=..."
            },
            "timestamp": datetime.utcnow().isoformat(),
            "signature": "test_signature",
        }
        
        msg_obj = Message(**message)
        assert msg_obj.type == MessageType.ANSWER
    
    def test_ice_candidate_message_structure(self):
        """Test ICE_CANDIDATE message structure."""
        did_key_a = DIDKey.generate()
        did_key_b = DIDKey.generate()
        
        message = {
            "id": "test_id_4",
            "type": "ICE_CANDIDATE",
            "from": did_key_a.did,
            "to": did_key_b.did,
            "payload": {
                "candidate": "candidate:1 1 UDP 2122260223...",
                "sdp_mline_index": 0,
                "sdp_mid": "0"
            },
            "timestamp": datetime.utcnow().isoformat(),
            "signature": "test_signature",
        }
        
        msg_obj = Message(**message)
        assert msg_obj.type == MessageType.ICE_CANDIDATE


class TestConcurrentOperations:
    """Test concurrent agent operations."""
    
    @pytest.mark.asyncio
    async def test_multiple_agents_registration(self):
        """Test multiple agents registering concurrently."""
        gateway = GatewayServer(agent_timeout=30)
        
        # Create multiple agents
        agents = []
        for i in range(5):
            did_key = DIDKey.generate()
            entry = RegistryEntry(
                agent_did=did_key.did,
                public_key=did_key.public_key_base58,
                connected_at=datetime.utcnow(),
            )
            agents.append((did_key, entry))
        
        # Register all concurrently
        tasks = [
            gateway.registry.register(did_key.did, entry)
            for did_key, entry in agents
        ]
        await asyncio.gather(*tasks)
        
        # Verify all registered
        registered = await gateway.registry.list_agents()
        assert len(registered) == 5
    
    @pytest.mark.asyncio
    async def test_concurrent_touch_operations(self):
        """Test concurrent activity updates."""
        gateway = GatewayServer(agent_timeout=30)
        
        # Register an agent
        did_key = DIDKey.generate()
        entry = RegistryEntry(
            agent_did=did_key.did,
            public_key=did_key.public_key_base58,
            connected_at=datetime.utcnow(),
        )
        await gateway.registry.register(did_key.did, entry)
        
        # Touch concurrently
        tasks = [
            gateway.registry.touch(did_key.did)
            for _ in range(10)
        ]
        await asyncio.gather(*tasks)
        
        # Should still be alive
        agent = await gateway.registry.get(did_key.did)
        assert agent is not None


class TestAgentTimeout:
    """Test agent timeout and cleanup."""
    
    @pytest.mark.asyncio
    async def test_agent_expiration_detection(self):
        """Test that expired agents are detected and removed."""
        from datetime import timedelta
        
        # Create registry with short timeout
        gateway = GatewayServer(agent_timeout=5)
        
        # Register agent with old timestamp
        old_time = datetime.utcnow() - timedelta(seconds=10)
        did_key = DIDKey.generate()
        
        entry = RegistryEntry(
            agent_did=did_key.did,
            public_key=did_key.public_key_base58,
            connected_at=old_time,
            last_activity=old_time,
        )
        
        await gateway.registry.register(did_key.did, entry)
        assert len(gateway.registry) == 1
        
        # Try to get expired agent
        agent = await gateway.registry.get(did_key.did)
        assert agent is None
        assert len(gateway.registry) == 0
    
    @pytest.mark.asyncio
    async def test_cleanup_removes_expired_agents(self):
        """Test cleanup task removes expired agents."""
        from datetime import timedelta
        
        gateway = GatewayServer(agent_timeout=5)
        
        # Register mix of fresh and expired agents
        now = datetime.utcnow()
        old_time = now - timedelta(seconds=10)
        
        for i in range(3):
            fresh_entry = RegistryEntry(
                agent_did=f"did:key:fresh{i}",
                public_key=f"key{i}",
                connected_at=now,
            )
            await gateway.registry.register(f"did:key:fresh{i}", fresh_entry)
        
        for i in range(2):
            old_entry = RegistryEntry(
                agent_did=f"did:key:old{i}",
                public_key=f"key{i}",
                connected_at=old_time,
                last_activity=old_time,
            )
            await gateway.registry.register(f"did:key:old{i}", old_entry)
        
        assert len(gateway.registry) == 5
        
        # Cleanup
        removed = await gateway.registry.cleanup_expired()
        assert removed == 2
        assert len(gateway.registry) == 3

"""
Unit tests for Gateway registry and server.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from gateway.registry import AgentRegistry, RegistryEntry


@pytest.fixture
def registry() -> AgentRegistry:
    """Create test registry."""
    return AgentRegistry(timeout_seconds=10)


class TestRegistryEntry:
    """Test RegistryEntry dataclass."""
    
    def test_entry_creation(self):
        """Test creating a registry entry."""
        now = datetime.utcnow()
        entry = RegistryEntry(
            agent_did="did:key:test",
            public_key="test_key",
            connected_at=now,
            ip_address="127.0.0.1"
        )
        
        assert entry.agent_did == "did:key:test"
        assert entry.public_key == "test_key"
        assert entry.connected_at == now
        assert entry.ip_address == "127.0.0.1"
    
    def test_entry_default_last_activity(self):
        """Test that last_activity defaults to now."""
        entry = RegistryEntry(
            agent_did="did:key:test",
            public_key="test_key",
            connected_at=datetime.utcnow(),
        )
        
        # Should have been set recently
        assert (datetime.utcnow() - entry.last_activity).total_seconds() < 1


class TestAgentRegistry:
    """Test AgentRegistry."""
    
    def test_init(self, registry: AgentRegistry):
        """Test registry initialization."""
        assert registry.timeout_seconds == 10
        assert len(registry) == 0
    
    def test_custom_timeout(self):
        """Test custom timeout setting."""
        registry = AgentRegistry(timeout_seconds=600)
        assert registry.timeout_seconds == 600
    
    @pytest.mark.asyncio
    async def test_register_agent(self, registry: AgentRegistry):
        """Test registering an agent."""
        entry = RegistryEntry(
            agent_did="did:key:agent1",
            public_key="key1",
            connected_at=datetime.utcnow(),
        )
        
        await registry.register("did:key:agent1", entry)
        
        assert len(registry) == 1
        retrieved = await registry.get("did:key:agent1")
        assert retrieved is not None
        assert retrieved.agent_did == "did:key:agent1"
    
    @pytest.mark.asyncio
    async def test_unregister_agent(self, registry: AgentRegistry):
        """Test unregistering an agent."""
        entry = RegistryEntry(
            agent_did="did:key:agent1",
            public_key="key1",
            connected_at=datetime.utcnow(),
        )
        
        await registry.register("did:key:agent1", entry)
        assert len(registry) == 1
        
        removed = await registry.unregister("did:key:agent1")
        assert removed is True
        assert len(registry) == 0
    
    @pytest.mark.asyncio
    async def test_unregister_nonexistent_agent(self, registry: AgentRegistry):
        """Test unregistering agent that doesn't exist."""
        removed = await registry.unregister("did:key:nonexistent")
        assert removed is False
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_agent(self, registry: AgentRegistry):
        """Test getting agent that doesn't exist."""
        entry = await registry.get("did:key:nonexistent")
        assert entry is None
    
    @pytest.mark.asyncio
    async def test_agent_expiration(self, registry: AgentRegistry):
        """Test that agents expire after timeout."""
        # Create agent with old timestamp
        old_time = datetime.utcnow() - timedelta(seconds=20)
        entry = RegistryEntry(
            agent_did="did:key:old_agent",
            public_key="key1",
            connected_at=old_time,
            last_activity=old_time,
        )
        
        await registry.register("did:key:old_agent", entry)
        assert len(registry) == 1
        
        # Try to get expired agent - should return None and remove it
        result = await registry.get("did:key:old_agent")
        assert result is None
        assert len(registry) == 0
    
    @pytest.mark.asyncio
    async def test_list_agents(self, registry: AgentRegistry):
        """Test listing all agents."""
        # Add multiple agents
        for i in range(3):
            entry = RegistryEntry(
                agent_did=f"did:key:agent{i}",
                public_key=f"key{i}",
                connected_at=datetime.utcnow(),
            )
            await registry.register(f"did:key:agent{i}", entry)
        
        agents = await registry.list_agents()
        assert len(agents) == 3
    
    @pytest.mark.asyncio
    async def test_list_agents_removes_expired(self, registry: AgentRegistry):
        """Test that list_agents removes expired agents."""
        # Add fresh and old agents
        fresh_entry = RegistryEntry(
            agent_did="did:key:fresh",
            public_key="fresh_key",
            connected_at=datetime.utcnow(),
        )
        await registry.register("did:key:fresh", fresh_entry)
        
        old_time = datetime.utcnow() - timedelta(seconds=20)
        old_entry = RegistryEntry(
            agent_did="did:key:old",
            public_key="old_key",
            connected_at=old_time,
            last_activity=old_time,
        )
        await registry.register("did:key:old", old_entry)
        
        # List should only return fresh agent
        agents = await registry.list_agents()
        assert len(agents) == 1
        assert agents[0].agent_did == "did:key:fresh"
    
    @pytest.mark.asyncio
    async def test_touch_agent(self, registry: AgentRegistry):
        """Test updating agent activity."""
        entry = RegistryEntry(
            agent_did="did:key:agent1",
            public_key="key1",
            connected_at=datetime.utcnow(),
            last_activity=datetime.utcnow() - timedelta(seconds=5),
        )
        await registry.register("did:key:agent1", entry)
        
        old_activity = entry.last_activity
        
        # Touch agent
        await registry.touch("did:key:agent1")
        
        # Get updated entry
        updated = await registry.get("did:key:agent1")
        assert updated is not None
        assert updated.last_activity > old_activity
    
    @pytest.mark.asyncio
    async def test_touch_nonexistent_agent(self, registry: AgentRegistry):
        """Test touching agent that doesn't exist."""
        # Should not raise
        await registry.touch("did:key:nonexistent")
    
    @pytest.mark.asyncio
    async def test_cleanup_expired(self, registry: AgentRegistry):
        """Test cleanup of expired agents."""
        # Add mix of fresh and expired agents
        for i in range(3):
            entry = RegistryEntry(
                agent_did=f"did:key:fresh{i}",
                public_key=f"fresh_key{i}",
                connected_at=datetime.utcnow(),
            )
            await registry.register(f"did:key:fresh{i}", entry)
        
        old_time = datetime.utcnow() - timedelta(seconds=20)
        for i in range(2):
            entry = RegistryEntry(
                agent_did=f"did:key:old{i}",
                public_key=f"old_key{i}",
                connected_at=old_time,
                last_activity=old_time,
            )
            await registry.register(f"did:key:old{i}", entry)
        
        assert len(registry) == 5
        
        # Cleanup should remove 2 old agents
        removed = await registry.cleanup_expired()
        assert removed == 2
        assert len(registry) == 3
    
    @pytest.mark.asyncio
    async def test_concurrent_register_unregister(self, registry: AgentRegistry):
        """Test concurrent registration and unregistration."""
        async def register_agents(count: int, prefix: str):
            for i in range(count):
                entry = RegistryEntry(
                    agent_did=f"did:key:{prefix}{i}",
                    public_key=f"key{i}",
                    connected_at=datetime.utcnow(),
                )
                await registry.register(f"did:key:{prefix}{i}", entry)
        
        # Run concurrent registrations
        await asyncio.gather(
            register_agents(5, "task1_agent"),
            register_agents(5, "task2_agent"),
        )
        
        assert len(registry) == 10

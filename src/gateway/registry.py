"""
Agent presence registry for the Gateway.

Tracks:
- Which agents are currently online
- Their public keys (for signature verification)
- Last activity timestamp (for timeout detection)
"""

from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class RegistryEntry:
    """Entry in the agent presence registry."""
    agent_did: str
    public_key: str
    connected_at: datetime
    last_activity: datetime = field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None


class AgentRegistry:
    """
    In-memory registry of online agents.
    
    Thread-safe, async-compatible.
    Can be replaced with Redis/etcd for clustering.
    
    Usage:
        registry = AgentRegistry(timeout_seconds=300)
        
        # Register agent
        entry = RegistryEntry(
            agent_did=did,
            public_key=key,
            connected_at=now,
            ip_address=ip
        )
        await registry.register(did, entry)
        
        # Check if agent is online
        agent = await registry.get(did)
        if agent:
            print(f"Agent online: {agent.agent_did}")
        
        # List all agents
        agents = await registry.list_agents()
        
        # Unregister
        await registry.unregister(did)
    """
    
    def __init__(self, timeout_seconds: int = 300):
        """
        Initialize registry.
        
        Args:
            timeout_seconds: Agent considered offline after this duration
        """
        self.timeout_seconds = timeout_seconds
        self._agents: Dict[str, RegistryEntry] = {}
        self._lock = asyncio.Lock()
    
    def __len__(self) -> int:
        """Return number of registered agents."""
        return len(self._agents)
    
    async def register(self, agent_did: str, entry: RegistryEntry) -> None:
        """
        Register an agent.
        
        Args:
            agent_did: Agent's DID
            entry: RegistryEntry with agent information
        """
        async with self._lock:
            self._agents[agent_did] = entry
            logger.debug(f"Registered agent: {agent_did}")
    
    async def unregister(self, agent_did: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            agent_did: Agent's DID
        
        Returns:
            True if agent was registered, False otherwise
        """
        async with self._lock:
            if agent_did in self._agents:
                del self._agents[agent_did]
                logger.debug(f"Unregistered agent: {agent_did}")
                return True
            return False
    
    async def get(self, agent_did: str) -> Optional[RegistryEntry]:
        """
        Get agent information.
        
        Args:
            agent_did: Agent's DID
        
        Returns:
            RegistryEntry if found and not expired, None otherwise
        """
        async with self._lock:
            entry = self._agents.get(agent_did)
            if entry is None:
                return None
            
            # Check if expired
            now = datetime.utcnow()
            age = (now - entry.last_activity).total_seconds()
            if age > self.timeout_seconds:
                logger.debug(f"Agent expired: {agent_did} (age: {age}s)")
                del self._agents[agent_did]
                return None
            
            return entry
    
    async def list_agents(self) -> List[RegistryEntry]:
        """
        Get all registered (non-expired) agents.
        
        Returns:
            List of RegistryEntry objects
        """
        async with self._lock:
            now = datetime.utcnow()
            active_agents = []
            expired_dids = []
            
            for did, entry in list(self._agents.items()):
                age = (now - entry.last_activity).total_seconds()
                if age > self.timeout_seconds:
                    expired_dids.append(did)
                else:
                    active_agents.append(entry)
            
            # Remove expired agents
            for did in expired_dids:
                del self._agents[did]
                logger.debug(f"Cleaned up expired agent: {did}")
            
            return active_agents
    
    async def touch(self, agent_did: str) -> None:
        """
        Update last activity timestamp for agent.
        
        Args:
            agent_did: Agent's DID
        """
        async with self._lock:
            if agent_did in self._agents:
                self._agents[agent_did].last_activity = datetime.utcnow()
    
    async def cleanup_expired(self) -> int:
        """
        Remove all expired agents.
        
        Returns:
            Number of agents removed
        """
        async with self._lock:
            now = datetime.utcnow()
            expired_dids = []
            
            for did, entry in self._agents.items():
                age = (now - entry.last_activity).total_seconds()
                if age > self.timeout_seconds:
                    expired_dids.append(did)
            
            for did in expired_dids:
                del self._agents[did]
            
            if expired_dids:
                logger.debug(f"Cleaned up {len(expired_dids)} expired agents")
            
            return len(expired_dids)

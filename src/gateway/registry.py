"""
Agent presence registry for the Gateway.

Tracks:
- Which agents are currently online
- Their public keys (for signature verification)
- Last activity timestamp (for timeout detection)
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import asyncio


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
    
    async def register(self, agent_did: str, public_key: str, 
                      ip_address: Optional[str] = None) -> None:
        """
        Register an agent.
        
        Args:
            agent_did: Agent identifier
            public_key: Public key for signature verification
            ip_address: Optional IP address
        """
        pass  # Stub - will be implemented in Sprint 2
    
    async def unregister(self, agent_did: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            agent_did: Agent to remove
            
        Returns:
            True if agent was registered, False otherwise
        """
        pass  # Stub
    
    async def get(self, agent_did: str) -> Optional[RegistryEntry]:
        """
        Get registry entry for an agent.
        
        Args:
            agent_did: Agent identifier
            
        Returns:
            RegistryEntry if found and not timed out
        """
        pass  # Stub
    
    async def list_agents(self) -> Dict[str, str]:
        """
        Get list of all online agents.
        
        Returns:
            Dict mapping agent_did -> public_key
        """
        pass  # Stub
    
    async def touch(self, agent_did: str) -> None:
        """
        Update last activity timestamp for an agent.
        
        Args:
            agent_did: Agent to touch
        """
        pass  # Stub
    
    async def cleanup_expired(self) -> int:
        """
        Remove agents that exceeded timeout.
        
        Returns:
            Number of agents removed
        """
        pass  # Stub

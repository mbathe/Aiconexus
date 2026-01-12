"""
Agent Registry Service
Handles agent discovery, matching, and information retrieval
"""

from typing import List, Optional, Dict, Any
import asyncio
from abc import ABC, abstractmethod
import numpy as np
from functools import lru_cache
import logging

from .types import ExpertiseArea, AgentInfo, AgentSchema, ConnectionInfo

logger = logging.getLogger(__name__)


class RegistryBackend(ABC):
    """Abstract backend for agent registry"""
    
    @abstractmethod
    async def register_agent(self, agent_info: AgentInfo) -> None:
        """Register a new agent"""
        pass
    
    @abstractmethod
    async def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent info by ID"""
        pass
    
    @abstractmethod
    async def find_agents(self, expertise: List[str], min_confidence: float = 0.7) -> List[AgentInfo]:
        """Find agents with specific expertise"""
        pass


class InMemoryRegistry(RegistryBackend):
    """In-memory registry for development and testing"""
    
    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
        self.cache: Dict[str, List[AgentInfo]] = {}
    
    async def register_agent(self, agent_info: AgentInfo) -> None:
        self.agents[agent_info.agent_id] = agent_info
        self.cache.clear()  # Invalidate cache
        logger.info(f"Registered agent: {agent_info.agent_id}")
    
    async def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        return self.agents.get(agent_id)
    
    async def find_agents(self, expertise: List[str], min_confidence: float = 0.7) -> List[AgentInfo]:
        """Find agents matching expertise"""
        expertise_set = set(e.lower() for e in expertise)
        
        candidates = []
        for agent in self.agents.values():
            # Calculate match score
            agent_domains = set(e.domain.lower() for e in agent.expertise)
            matched_domains = expertise_set & agent_domains
            
            if not matched_domains:
                continue
            
            # Get average confidence for matched domains
            matched_expertise = [e for e in agent.expertise if e.domain.lower() in matched_domains]
            avg_confidence = sum(e.confidence for e in matched_expertise) / len(matched_expertise)
            
            if avg_confidence >= min_confidence:
                agent.match_score = avg_confidence
                candidates.append(agent)
        
        # Sort by confidence
        candidates.sort(key=lambda a: a.match_score, reverse=True)
        return candidates


class EmbeddingMatcher:
    """
    Semantic matching using embeddings
    Matches tasks to agent expertise
    """
    
    def __init__(self, embedding_provider: Optional[str] = None):
        self.embedding_provider = embedding_provider or "default"
        self._embedding_cache = {}
    
    async def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text"""
        if text in self._embedding_cache:
            return self._embedding_cache[text]
        
        # In production, use OpenAI or other providers
        # For now, use simple hash-based mock
        embedding = self._mock_embedding(text)
        self._embedding_cache[text] = embedding
        return embedding
    
    def _mock_embedding(self, text: str) -> np.ndarray:
        """Mock embedding function for development"""
        # In production, replace with real embeddings
        import hashlib
        hash_val = hashlib.md5(text.encode()).hexdigest()
        # Convert to vector
        vector = np.array([int(c, 16) for c in hash_val[:32]]) / 16.0
        return vector / np.linalg.norm(vector)
    
    async def semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        emb1 = await self.get_embedding(text1)
        emb2 = await self.get_embedding(text2)
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(similarity)


class AgentRegistry:
    """
    Main Agent Registry Service
    Combines multiple matching strategies
    """
    
    def __init__(
        self,
        backend: Optional[RegistryBackend] = None,
        enable_semantic_matching: bool = True,
        similarity_threshold: float = 0.75
    ):
        self.backend = backend or InMemoryRegistry()
        self.matcher = EmbeddingMatcher() if enable_semantic_matching else None
        self.similarity_threshold = similarity_threshold
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    async def register_agent(
        self,
        agent_id: str,
        name: str,
        expertise: List[ExpertiseArea],
        connection_info: ConnectionInfo,
        schema: Optional[AgentSchema] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a new agent"""
        agent_info = AgentInfo(
            agent_id=agent_id,
            name=name,
            expertise=expertise,
            connection_info=connection_info,
            schema=schema,
            metadata=metadata or {}
        )
        
        await self.backend.register_agent(agent_info)
        self._invalidate_cache()
    
    async def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent by ID"""
        return await self.backend.get_agent(agent_id)
    
    async def find_agents_by_expertise(
        self,
        expertise: List[str],
        min_confidence: float = 0.7,
        limit: int = 5
    ) -> List[AgentInfo]:
        """
        Find agents with specific expertise
        Uses multiple matching strategies
        """
        
        # Step 1: Exact domain matching via backend
        candidates = await self.backend.find_agents(expertise, min_confidence)
        
        # Step 2: Semantic matching for better results
        if self.matcher and len(candidates) < limit:
            enhanced_candidates = await self._semantic_find(
                expertise,
                candidates,
                min_confidence
            )
            candidates = enhanced_candidates
        
        return candidates[:limit]
    
    async def _semantic_find(
        self,
        expertise: List[str],
        existing_candidates: List[AgentInfo],
        min_confidence: float
    ) -> List[AgentInfo]:
        """Enhanced finding using semantic similarity"""
        expertise_text = " ".join(expertise)
        
        all_agents = list(self.backend.agents.values()) if hasattr(self.backend, 'agents') else []
        
        for agent in all_agents:
            if agent.agent_id in [c.agent_id for c in existing_candidates]:
                continue
            
            # Check semantic similarity
            agent_expertise_text = " ".join([e.domain for e in agent.expertise])
            similarity = await self.matcher.semantic_similarity(expertise_text, agent_expertise_text)
            
            if similarity >= self.similarity_threshold:
                # Boost confidence with semantic match
                agent.match_score = min(0.99, agent.expertise[0].confidence * (0.8 + similarity * 0.2))
                existing_candidates.append(agent)
        
        # Re-sort
        existing_candidates.sort(key=lambda a: a.match_score, reverse=True)
        return existing_candidates
    
    async def get_agent_schema(self, agent_id: str) -> Optional[AgentSchema]:
        """Get schema for an agent"""
        agent = await self.get_agent(agent_id)
        return agent.schema if agent else None
    
    async def get_connection_info(self, agent_id: str) -> Optional[ConnectionInfo]:
        """Get connection info for an agent"""
        agent = await self.get_agent(agent_id)
        return agent.connection_info if agent else None
    
    def _invalidate_cache(self):
        """Invalidate all caches"""
        self._cache.clear()

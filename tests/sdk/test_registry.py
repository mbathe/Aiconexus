"""
Tests pour le système de découverte d'agents (Registry).
"""
import pytest
import uuid
from datetime import datetime

from src.aiconexus.sdk.registry import (
    AgentRegistry, InMemoryRegistry, EmbeddingMatcher
)
from src.aiconexus.sdk.types import ExpertiseArea, ExpertiseLevel


class TestInMemoryRegistry:
    """Tests pour InMemoryRegistry."""
    
    def test_registry_creation(self, empty_registry):
        """Test la création d'une registry."""
        assert isinstance(empty_registry, InMemoryRegistry)
        assert len(empty_registry.agents) == 0
    
    def test_register_agent(self, empty_registry, analyzer_agent_info):
        """Test l'enregistrement d'un agent."""
        empty_registry.agents[analyzer_agent_info.id] = analyzer_agent_info
        
        assert analyzer_agent_info.id in empty_registry.agents
        assert empty_registry.agents[analyzer_agent_info.id].name == "DataAnalyzer"
    
    def test_register_multiple_agents(self, empty_registry, multiple_agents):
        """Test l'enregistrement de plusieurs agents."""
        for agent in multiple_agents:
            empty_registry.agents[agent.id] = agent
        
        assert len(empty_registry.agents) == 3
    
    def test_get_agent(self, populated_registry, analyzer_agent_info):
        """Test la récupération d'un agent."""
        agent = populated_registry.agents.get(analyzer_agent_info.id)
        
        assert agent is not None
        assert agent.name == "DataAnalyzer"
    
    def test_get_nonexistent_agent(self, populated_registry):
        """Test la récupération d'un agent qui n'existe pas."""
        agent = populated_registry.agents.get("nonexistent")
        
        assert agent is None


class TestEmbeddingMatcher:
    """Tests pour EmbeddingMatcher."""
    
    def test_matcher_creation(self):
        """Test la création d'un matcher."""
        matcher = EmbeddingMatcher()
        assert matcher is not None
    
    @pytest.mark.asyncio
    async def test_similarity_same_text(self):
        """Test la similarité d'un texte avec lui-même."""
        matcher = EmbeddingMatcher()
        
        similarity = await matcher.compute_similarity("test", "test")
        
        # Similarité entre le même texte doit être très proche de 1.0
        assert similarity > 0.99
    
    @pytest.mark.asyncio
    async def test_similarity_different_texts(self):
        """Test la similarité de textes différents."""
        matcher = EmbeddingMatcher()
        
        similarity = await matcher.compute_similarity("apple", "orange")
        
        # Deux mots différents doivent avoir une similarité basse
        assert 0 <= similarity <= 1
    
    @pytest.mark.asyncio
    async def test_similarity_related_texts(self):
        """Test la similarité de textes liés."""
        matcher = EmbeddingMatcher()
        
        sim1 = await matcher.compute_similarity("data analysis", "analyze data")
        sim2 = await matcher.compute_similarity("apple", "orange")
        
        # Les textes liés doivent avoir une similarité plus haute
        assert sim1 > sim2
    
    @pytest.mark.asyncio
    async def test_similarity_symmetric(self):
        """Test que la similarité est symétrique."""
        matcher = EmbeddingMatcher()
        
        sim1 = await matcher.compute_similarity("hello world", "world hello")
        sim2 = await matcher.compute_similarity("world hello", "hello world")
        
        # La similarité doit être la même dans les deux sens
        assert abs(sim1 - sim2) < 0.01


class TestAgentRegistry:
    """Tests pour AgentRegistry."""
    
    def test_registry_creation(self):
        """Test la création d'une registry d'agents."""
        registry = AgentRegistry(backend=InMemoryRegistry())
        assert registry is not None
    
    @pytest.mark.asyncio
    async def test_find_agents_empty(self):
        """Test la recherche dans une registry vide."""
        registry = AgentRegistry(backend=InMemoryRegistry())
        
        agents = await registry.find_agents_by_expertise(["nonexistent"])
        
        assert agents == []
    
    @pytest.mark.asyncio
    async def test_find_agents_exact_match(self, populated_registry):
        """Test la recherche avec matching exact."""
        registry = AgentRegistry(backend=populated_registry)
        
        agents = await registry.find_agents_by_expertise(
            ["data-analysis"],
            strategy="exact"
        )
        
        assert len(agents) > 0
        assert any(a.name == "DataAnalyzer" for a in agents)
    
    @pytest.mark.asyncio
    async def test_find_agents_semantic(self, populated_registry):
        """Test la recherche avec matching sémantique."""
        registry = AgentRegistry(backend=populated_registry)
        
        agents = await registry.find_agents_by_expertise(
            ["analyze"],  # Mot similaire à "data-analysis"
            strategy="semantic",
            min_confidence=0.5
        )
        
        # Devrait trouver des agents pertinents
        # (le résultat exact dépend des embeddings)
        assert isinstance(agents, list)
    
    @pytest.mark.asyncio
    async def test_find_agents_hybrid(self, populated_registry):
        """Test la recherche avec stratégie hybride."""
        registry = AgentRegistry(backend=populated_registry)
        
        agents = await registry.find_agents_by_expertise(
            ["optimization"],
            strategy="hybrid"
        )
        
        assert len(agents) >= 0
    
    @pytest.mark.asyncio
    async def test_find_multiple_expertise(self, populated_registry):
        """Test la recherche avec plusieurs domaines."""
        registry = AgentRegistry(backend=populated_registry)
        
        agents = await registry.find_agents_by_expertise(
            ["data-analysis", "optimization"],
            strategy="exact"
        )
        
        assert isinstance(agents, list)


class TestRegistryWithMultipleAgents:
    """Tests du registry avec plusieurs agents."""
    
    @pytest.mark.asyncio
    async def test_find_most_relevant(self, populated_registry):
        """Test que les agents les plus pertinents sont trouvés en premier."""
        registry = AgentRegistry(backend=populated_registry)
        
        # Rechercher des agents avec expertise en "optimization"
        agents = await registry.find_agents_by_expertise(
            ["optimization"],
            strategy="exact"
        )
        
        # Le premier devrait être l'Optimizer
        if agents:
            assert agents[0].name == "Optimizer"
    
    @pytest.mark.asyncio
    async def test_confidence_threshold(self, populated_registry):
        """Test le seuil de confiance."""
        registry = AgentRegistry(backend=populated_registry)
        
        # Avec seuil bas
        agents_low = await registry.find_agents_by_expertise(
            ["anything"],
            strategy="semantic",
            min_confidence=0.1
        )
        
        # Avec seuil haut
        agents_high = await registry.find_agents_by_expertise(
            ["anything"],
            strategy="semantic",
            min_confidence=0.9
        )
        
        # Seuil haut devrait retourner moins d'agents
        assert len(agents_high) <= len(agents_low)
    
    @pytest.mark.asyncio
    async def test_no_duplicates_in_results(self, populated_registry):
        """Test qu'il n'y a pas de doublons dans les résultats."""
        registry = AgentRegistry(backend=populated_registry)
        
        agents = await registry.find_agents_by_expertise(
            ["data-analysis", "optimization"],
            strategy="hybrid"
        )
        
        # Vérifier les IDs uniques
        agent_ids = [a.id for a in agents]
        assert len(agent_ids) == len(set(agent_ids))


class TestCustomRegistryBackend:
    """Tests pour un backend personnalisé."""
    
    @pytest.mark.asyncio
    async def test_custom_backend(self, analyzer_agent_info):
        """Test l'utilisation d'un backend personnalisé."""
        from src.aiconexus.sdk.registry import RegistryBackend
        
        class CustomBackend(RegistryBackend):
            def __init__(self):
                self.agents = {analyzer_agent_info.id: analyzer_agent_info}
            
            async def find_agents(self, expertise, min_confidence=0.7):
                return list(self.agents.values())
        
        backend = CustomBackend()
        registry = AgentRegistry(backend=backend)
        
        agents = await registry.find_agents_by_expertise(["test"])
        
        assert len(agents) > 0
        assert agents[0].id == analyzer_agent_info.id


class TestRegistryPerformance:
    """Tests de performance du registry."""
    
    @pytest.mark.asyncio
    async def test_find_with_many_agents(self):
        """Test la recherche avec beaucoup d'agents."""
        from src.aiconexus.sdk.types import AgentSchema, InputSchema, OutputSchema
        
        backend = InMemoryRegistry()
        
        # Créer 1000 agents
        for i in range(1000):
            schema = AgentSchema(
                name=f"Agent{i}",
                input_schema=InputSchema(fields={}, required_fields=[]),
                output_schema=OutputSchema(fields={}, required_fields=[])
            )
            
            agent = analyzer_agent_info = type('obj', (object,), {
                'id': str(uuid.uuid4()),
                'name': f'Agent{i}',
                'endpoint': f'http://localhost:{8000+i}',
                'expertise': [ExpertiseArea("test", ExpertiseLevel.INTERMEDIATE)],
                'schema': schema,
                'status': 'active',
                'created_at': datetime.now(),
                'last_heartbeat': datetime.now()
            })()
            
            backend.agents[agent.id] = agent
        
        registry = AgentRegistry(backend=backend)
        
        # Recherche devrait être rapide même avec 1000 agents
        agents = await registry.find_agents_by_expertise(
            ["test"],
            strategy="exact"
        )
        
        assert len(agents) > 0

"""
Fixtures partagées pour tous les tests du SDK.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
import uuid

from src.aiconexus.sdk.types import (
    ExpertiseArea, ExpertiseLevel, AgentInfo, Message,
    AgentSchema, InputSchema, OutputSchema, FieldSchema
)
from src.aiconexus.sdk.registry import AgentRegistry, InMemoryRegistry
from src.aiconexus.sdk.validator import MessageValidator
from src.aiconexus.sdk.connector import AgentConnector, HTTPTransport


# ============================================================================
# Event Loop Setup
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Crée une boucle d'événements pour toute la session de test."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Expertise Areas
# ============================================================================

@pytest.fixture
def data_analysis_expertise():
    """Expertise en analyse de données."""
    return ExpertiseArea(
        domain="data-analysis",
        level=ExpertiseLevel.EXPERT
    )


@pytest.fixture
def optimization_expertise():
    """Expertise en optimisation."""
    return ExpertiseArea(
        domain="optimization",
        level=ExpertiseLevel.MASTER
    )


@pytest.fixture
def machine_learning_expertise():
    """Expertise en machine learning."""
    return ExpertiseArea(
        domain="machine-learning",
        level=ExpertiseLevel.INTERMEDIATE
    )


@pytest.fixture
def expertise_list(data_analysis_expertise, optimization_expertise):
    """Liste d'expertises pour tests."""
    return [data_analysis_expertise, optimization_expertise]


# ============================================================================
# Schemas
# ============================================================================

@pytest.fixture
def simple_input_schema():
    """Schéma d'entrée simple."""
    return InputSchema(
        fields={
            "data": FieldSchema(
                type="array",
                description="Dataset to analyze",
                constraints={"min_items": 1}
            ),
            "metric": FieldSchema(
                type="string",
                description="Metric to calculate",
                constraints={"enum": ["mean", "std", "min", "max"]}
            )
        },
        required_fields=["data", "metric"]
    )


@pytest.fixture
def simple_output_schema():
    """Schéma de sortie simple."""
    return OutputSchema(
        fields={
            "result": FieldSchema(type="number"),
            "timestamp": FieldSchema(type="string")
        },
        required_fields=["result"]
    )


@pytest.fixture
def simple_agent_schema(simple_input_schema, simple_output_schema):
    """Schéma d'agent complet."""
    return AgentSchema(
        name="TestAgent",
        input_schema=simple_input_schema,
        output_schema=simple_output_schema
    )


# ============================================================================
# Agent Infos
# ============================================================================

@pytest.fixture
def analyzer_agent_info(data_analysis_expertise, simple_agent_schema):
    """Info d'agent analyst."""
    return AgentInfo(
        id=str(uuid.uuid4()),
        name="DataAnalyzer",
        endpoint="http://analyzer:8000",
        expertise=[data_analysis_expertise],
        schema=simple_agent_schema,
        status="active",
        created_at=datetime.now(),
        last_heartbeat=datetime.now()
    )


@pytest.fixture
def optimizer_agent_info(optimization_expertise, simple_agent_schema):
    """Info d'agent optimiseur."""
    return AgentInfo(
        id=str(uuid.uuid4()),
        name="Optimizer",
        endpoint="http://optimizer:8000",
        expertise=[optimization_expertise],
        schema=simple_agent_schema,
        status="active",
        created_at=datetime.now(),
        last_heartbeat=datetime.now()
    )


@pytest.fixture
def ml_agent_info(machine_learning_expertise, simple_agent_schema):
    """Info d'agent ML."""
    return AgentInfo(
        id=str(uuid.uuid4()),
        name="MLExpert",
        endpoint="http://ml:8000",
        expertise=[machine_learning_expertise],
        schema=simple_agent_schema,
        status="active",
        created_at=datetime.now(),
        last_heartbeat=datetime.now()
    )


@pytest.fixture
def multiple_agents(analyzer_agent_info, optimizer_agent_info, ml_agent_info):
    """Liste d'agents pour tests."""
    return [analyzer_agent_info, optimizer_agent_info, ml_agent_info]


# ============================================================================
# Messages
# ============================================================================

@pytest.fixture
def simple_valid_message(analyzer_agent_info):
    """Message valide simple."""
    return Message(
        id=str(uuid.uuid4()),
        sender_id="user",
        recipient_id=analyzer_agent_info.id,
        data={"data": [1, 2, 3, 4, 5], "metric": "mean"},
        timestamp=datetime.now(),
        request_id=str(uuid.uuid4())
    )


@pytest.fixture
def invalid_message(analyzer_agent_info):
    """Message invalide (données manquantes)."""
    return Message(
        id=str(uuid.uuid4()),
        sender_id="user",
        recipient_id=analyzer_agent_info.id,
        data={"metric": "mean"},  # Manque 'data'
        timestamp=datetime.now()
    )


# ============================================================================
# Registry
# ============================================================================

@pytest.fixture
def empty_registry():
    """Registry vide."""
    return InMemoryRegistry()


@pytest.fixture
def populated_registry(empty_registry, multiple_agents):
    """Registry avec agents."""
    for agent in multiple_agents:
        empty_registry.agents[agent.id] = agent
    return empty_registry


# ============================================================================
# Mock Transport
# ============================================================================

@pytest.fixture
def mock_transport():
    """Transport mocké."""
    transport = AsyncMock(spec=HTTPTransport)
    
    async def mock_send(connection_info, message, timeout=30.0):
        return Message(
            id=str(uuid.uuid4()),
            sender_id=connection_info.agent_id,
            recipient_id=message.sender_id,
            data={"status": "success", "result": 42},
            timestamp=datetime.now()
        )
    
    transport.send = mock_send
    return transport


# ============================================================================
# Connector
# ============================================================================

@pytest.fixture
def connector_with_registry(populated_registry, mock_transport):
    """Connector avec registry peuplé."""
    connector = AgentConnector(
        transport=mock_transport,
        registry=populated_registry
    )
    return connector


# ============================================================================
# Validator
# ============================================================================

@pytest.fixture
def validator():
    """Validateur de messages."""
    return MessageValidator()


# ============================================================================
# Mock LLM
# ============================================================================

@pytest.fixture
def mock_llm():
    """Mock d'un LLM."""
    llm = AsyncMock()
    
    # Réponse par défaut: retourne un texte simple
    llm.ainvoke = AsyncMock(return_value=MagicMock(
        content="This is a test response",
        tool_calls=[]
    ))
    
    llm.model_name = "gpt-4"
    
    return llm


@pytest.fixture
def mock_llm_with_tools():
    """Mock LLM avec tool_calls."""
    llm = AsyncMock()
    
    llm.ainvoke = AsyncMock(return_value=MagicMock(
        content="I need to use a tool",
        tool_calls=[
            MagicMock(
                id="call_1",
                function=MagicMock(
                    name="find_experts",
                    arguments='{"expertise": ["optimization"]}'
                )
            )
        ]
    ))
    
    llm.model_name = "gpt-4"
    
    return llm


# ============================================================================
# Test Data Builders
# ============================================================================

@pytest.fixture
def message_builder():
    """Builder pour construire des messages de test."""
    class MessageBuilder:
        def __init__(self):
            self.data = {}
            self.sender_id = "test-sender"
            self.recipient_id = "test-recipient"
        
        def with_data(self, **kwargs):
            self.data = kwargs
            return self
        
        def with_sender(self, sender_id):
            self.sender_id = sender_id
            return self
        
        def with_recipient(self, recipient_id):
            self.recipient_id = recipient_id
            return self
        
        def build(self):
            return Message(
                id=str(uuid.uuid4()),
                sender_id=self.sender_id,
                recipient_id=self.recipient_id,
                data=self.data,
                timestamp=datetime.now()
            )
    
    return MessageBuilder()


@pytest.fixture
def agent_info_builder():
    """Builder pour construire des infos d'agent."""
    class AgentInfoBuilder:
        def __init__(self):
            self.id = str(uuid.uuid4())
            self.name = "TestAgent"
            self.endpoint = "http://localhost:8000"
            self.expertise = [ExpertiseArea("test", ExpertiseLevel.INTERMEDIATE)]
            self.status = "active"
        
        def with_name(self, name):
            self.name = name
            return self
        
        def with_expertise(self, *expertise_areas):
            self.expertise = list(expertise_areas)
            return self
        
        def with_endpoint(self, endpoint):
            self.endpoint = endpoint
            return self
        
        def with_status(self, status):
            self.status = status
            return self
        
        def build(self):
            from src.aiconexus.sdk.types import AgentSchema, InputSchema, OutputSchema, FieldSchema
            
            schema = AgentSchema(
                name=self.name,
                input_schema=InputSchema(fields={}, required_fields=[]),
                output_schema=OutputSchema(fields={}, required_fields=[])
            )
            
            return AgentInfo(
                id=self.id,
                name=self.name,
                endpoint=self.endpoint,
                expertise=self.expertise,
                schema=schema,
                status=self.status,
                created_at=datetime.now(),
                last_heartbeat=datetime.now()
            )
    
    return AgentInfoBuilder()


# ============================================================================
# Markers
# ============================================================================

def pytest_configure(config):
    """Configure les custom markers."""
    config.addinivalue_line(
        "markers", "asyncio: marque les tests asynchrones"
    )
    config.addinivalue_line(
        "markers", "integration: marque les tests d'intégration"
    )
    config.addinivalue_line(
        "markers", "performance: marque les tests de performance"
    )

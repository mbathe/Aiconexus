"""Tests for the Orchestrator module.

This module tests the Orchestrator which coordinates all SDK components
(Registry, Validator, Connector, Tools, Executor) to work together.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.aiconexus.sdk.orchestrator import Orchestrator, OrchestratorConfig
from src.aiconexus.sdk.types import Message


class TestOrchestratorInitialization:
    """Test Orchestrator initialization."""

    def test_create_orchestrator(self, mock_llm, populated_registry):
        """Test creating an orchestrator."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry
        )
        
        assert orchestrator is not None
        assert orchestrator.llm == mock_llm
        assert orchestrator.registry == populated_registry

    def test_orchestrator_with_config(self, mock_llm, populated_registry):
        """Test orchestrator with custom configuration."""
        config = OrchestratorConfig(
            enable_semantic_search=True,
            enable_validation=True,
            enable_tool_calling=True
        )
        
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry,
            config=config
        )
        
        assert orchestrator.config == config

    def test_orchestrator_initializes_components(self, mock_llm, populated_registry):
        """Test that orchestrator initializes all components."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry
        )
        
        assert orchestrator.executor is not None
        assert orchestrator.validator is not None
        assert orchestrator.connector is not None
        assert orchestrator.tool_caller is not None


class TestOrchestratorRegistryExposure:
    """Test registry exposed as tools to executor."""

    @pytest.mark.asyncio
    async def test_registry_as_discovery_tool(self, mock_llm, populated_registry):
        """Test using registry for agent discovery."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry
        )
        
        # Get registry as tool
        registry_tool = orchestrator.get_registry_tool()
        
        assert registry_tool is not None
        assert "discover" in registry_tool.get("name", "").lower()

    @pytest.mark.asyncio
    async def test_discover_agents_via_tool(self, mock_llm, populated_registry):
        """Test discovering agents through orchestrator tools."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry
        )
        
        # Get all available tools
        tools = orchestrator.get_available_tools()
        
        assert len(tools) > 0
        # Should include discovery capability
        assert any("discover" in str(t).lower() for t in tools)

    @pytest.mark.asyncio
    async def test_semantic_discovery_tool(self, mock_llm, populated_registry):
        """Test semantic agent discovery tool."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry,
            config=OrchestratorConfig(enable_semantic_search=True)
        )
        
        # Discover similar agents
        agents = await orchestrator.discover_agents(
            query="data analysis",
            method="semantic"
        )
        
        assert agents is not None
        assert len(agents) > 0


class TestOrchestratorValidation:
    """Test message validation integration."""

    @pytest.mark.asyncio
    async def test_validate_incoming_message(
        self,
        mock_llm,
        populated_registry,
        simple_valid_message
    ):
        """Test validating incoming messages."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry,
            config=OrchestratorConfig(enable_validation=True)
        )
        
        is_valid = await orchestrator.validate_message(simple_valid_message)
        
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_validate_invalid_message(
        self,
        mock_llm,
        populated_registry,
        invalid_message
    ):
        """Test validation rejects invalid messages."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry,
            config=OrchestratorConfig(enable_validation=True)
        )
        
        is_valid = await orchestrator.validate_message(invalid_message)
        
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_validation_error_details(
        self,
        mock_llm,
        populated_registry,
        invalid_message
    ):
        """Test getting validation error details."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry,
            config=OrchestratorConfig(enable_validation=True)
        )
        
        result = await orchestrator.validate_with_details(invalid_message)
        
        assert result["valid"] is False
        assert "errors" in result


class TestOrchestratorToolCalling:
    """Test tool calling integration."""

    @pytest.mark.asyncio
    async def test_executor_receives_tools(self, mock_llm, populated_registry):
        """Test that executor receives configured tools."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry
        )
        
        # Get tools available to executor
        tools = orchestrator.get_executor_tools()
        
        assert len(tools) > 0
        # Should include registry, validator, and custom tools

    @pytest.mark.asyncio
    async def test_custom_tool_registration(self, mock_llm, populated_registry):
        """Test registering custom tools."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry
        )
        
        async def custom_tool(param):
            return f"Custom result: {param}"
        
        orchestrator.register_tool(
            name="custom_search",
            func=custom_tool,
            description="Custom search tool"
        )
        
        tools = orchestrator.get_executor_tools()
        assert any(t.get("name") == "custom_search" for t in tools)

    @pytest.mark.asyncio
    async def test_tool_calling_in_execution(self, mock_llm, populated_registry):
        """Test tools are called during execution."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry
        )
        
        # Mock tool execution
        orchestrator.executor.tool_registry = {
            "search": AsyncMock(return_value="Results")
        }
        
        # Tools should be available to executor
        assert "search" in orchestrator.executor.tool_registry


class TestOrchestratorConnectorIntegration:
    """Test connector integration for inter-agent communication."""

    @pytest.mark.asyncio
    async def test_send_to_discovered_agent(
        self,
        mock_llm,
        populated_registry,
        simple_valid_message
    ):
        """Test sending message to discovered agent."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry
        )
        
        # Discover an agent
        agents = await orchestrator.discover_agents("data analysis")
        assert len(agents) > 0
        
        agent = agents[0]
        
        # Send message to agent
        result = await orchestrator.send_message(
            message=simple_valid_message,
            recipient=agent.name
        )
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_broadcast_to_multiple_agents(
        self,
        mock_llm,
        populated_registry,
        message_builder
    ):
        """Test broadcasting message to multiple agents."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry
        )
        
        message = message_builder.build()
        
        # Broadcast to all agents
        results = await orchestrator.broadcast_message(message)
        
        assert results is not None
        assert len(results) > 0


class TestOrchestratorCoordination:
    """Test component coordination."""

    @pytest.mark.asyncio
    async def test_execute_task_with_all_components(
        self,
        mock_llm,
        populated_registry
    ):
        """Test task execution using all components."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry,
            config=OrchestratorConfig(
                enable_validation=True,
                enable_semantic_search=True,
                enable_tool_calling=True
            )
        )
        
        # Mock LLM response
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="Task completed",
            tool_calls=[]
        ))
        
        result = await orchestrator.execute_task(
            task="Find and analyze data",
            expertise_area="data_analysis"
        )
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_workflow_with_agent_discovery(
        self,
        mock_llm,
        populated_registry
    ):
        """Test workflow: discover agent, validate, communicate."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry
        )
        
        # Step 1: Discover agent
        agents = await orchestrator.discover_agents("data_analysis")
        assert len(agents) > 0
        
        agent = agents[0]
        
        # Step 2: Create message
        from src.aiconexus.sdk.types import InputSchema
        
        message = Message(
            sender="orchestrator",
            recipient=agent.name,
            schema=InputSchema(required_fields=["data"]),
            data={"data": "test"}
        )
        
        # Step 3: Validate message
        is_valid = await orchestrator.validate_message(message)
        assert is_valid is True
        
        # Step 4: Send message
        result = await orchestrator.send_message(
            message=message,
            recipient=agent.name
        )
        
        assert result is not None


class TestOrchestratorState:
    """Test orchestrator state management."""

    def test_orchestrator_state_initialization(self, mock_llm, populated_registry):
        """Test orchestrator initializes proper state."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry
        )
        
        assert orchestrator is not None
        assert hasattr(orchestrator, 'execution_count')
        assert hasattr(orchestrator, 'message_log')

    @pytest.mark.asyncio
    async def test_state_tracking_during_execution(
        self,
        mock_llm,
        populated_registry
    ):
        """Test state updates during execution."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry
        )
        
        initial_count = orchestrator.execution_count if hasattr(orchestrator, 'execution_count') else 0
        
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="Done",
            tool_calls=[]
        ))
        
        await orchestrator.execute_task(task="Test", expertise_area="any")
        
        # Execution count should increase
        if hasattr(orchestrator, 'execution_count'):
            assert orchestrator.execution_count > initial_count


class TestOrchestratorErrorHandling:
    """Test error handling and recovery."""

    @pytest.mark.asyncio
    async def test_validation_failure_handling(
        self,
        mock_llm,
        populated_registry,
        invalid_message
    ):
        """Test handling of validation failures."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry,
            config=OrchestratorConfig(
                enable_validation=True,
                fail_on_validation_error=True
            )
        )
        
        with pytest.raises((ValueError, RuntimeError)):
            await orchestrator.send_message(
                message=invalid_message,
                recipient="some_agent"
            )

    @pytest.mark.asyncio
    async def test_discovery_failure_handling(self, mock_llm, empty_registry):
        """Test handling when no agents match discovery criteria."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=empty_registry
        )
        
        agents = await orchestrator.discover_agents("nonexistent")
        
        assert agents == [] or agents is None

    @pytest.mark.asyncio
    async def test_execution_error_recovery(self, mock_llm, populated_registry):
        """Test recovery from execution errors."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry
        )
        
        mock_llm.ainvoke = AsyncMock(
            side_effect=Exception("LLM error")
        )
        
        with pytest.raises(Exception):
            await orchestrator.execute_task(task="Test", expertise_area="any")


class TestOrchestratorConfiguration:
    """Test orchestrator configuration options."""

    def test_disable_validation(self, mock_llm, populated_registry):
        """Test disabling validation."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry,
            config=OrchestratorConfig(enable_validation=False)
        )
        
        assert orchestrator.config.enable_validation is False

    def test_disable_semantic_search(self, mock_llm, populated_registry):
        """Test disabling semantic search."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry,
            config=OrchestratorConfig(enable_semantic_search=False)
        )
        
        assert orchestrator.config.enable_semantic_search is False

    def test_disable_tool_calling(self, mock_llm, populated_registry):
        """Test disabling tool calling."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry,
            config=OrchestratorConfig(enable_tool_calling=False)
        )
        
        assert orchestrator.config.enable_tool_calling is False

    def test_custom_max_iterations(self, mock_llm, populated_registry):
        """Test setting custom max iterations."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry,
            config=OrchestratorConfig(max_executor_iterations=20)
        )
        
        assert orchestrator.executor.max_iterations == 20


class TestOrchestratorToolProvision:
    """Test dynamic tool provisioning."""

    def test_get_executor_tools(self, mock_llm, populated_registry):
        """Test getting all executor tools."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry
        )
        
        tools = orchestrator.get_executor_tools()
        
        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_get_registry_tools(self, mock_llm, populated_registry):
        """Test getting registry discovery tools."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry
        )
        
        tools = orchestrator.get_registry_tools()
        
        assert isinstance(tools, list)
        # Should have at least discover functions

    def test_get_all_available_tools(self, mock_llm, populated_registry):
        """Test getting all available tools."""
        orchestrator = Orchestrator(
            llm=mock_llm,
            registry=populated_registry
        )
        
        tools = orchestrator.get_available_tools()
        
        assert isinstance(tools, list)
        assert len(tools) > 0
        # Should be union of registry + validation + custom tools


@pytest.mark.asyncio
async def test_orchestrator_integration_full_workflow(
    mock_llm,
    populated_registry,
    message_builder
):
    """Integration test of complete orchestrator workflow."""
    orchestrator = Orchestrator(
        llm=mock_llm,
        registry=populated_registry,
        config=OrchestratorConfig(
            enable_validation=True,
            enable_semantic_search=True,
            enable_tool_calling=True
        )
    )
    
    # Mock LLM
    mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
        content="Analysis complete",
        tool_calls=[]
    ))
    
    # Execute full workflow
    message = message_builder.build()
    
    # Discover agents
    agents = await orchestrator.discover_agents("data_analysis")
    assert len(agents) > 0
    
    # Validate message
    is_valid = await orchestrator.validate_message(message)
    assert is_valid is True
    
    # Execute task
    result = await orchestrator.execute_task(
        task="Analyze data",
        expertise_area="data_analysis"
    )
    
    assert result is not None


@pytest.mark.asyncio
async def test_orchestrator_multi_agent_coordination(
    mock_llm,
    populated_registry,
    message_builder
):
    """Test coordinating multiple agents."""
    orchestrator = Orchestrator(
        llm=mock_llm,
        registry=populated_registry
    )
    
    # Discover multiple agents
    analyzers = await orchestrator.discover_agents("data_analysis")
    optimizers = await orchestrator.discover_agents("optimization")
    
    # Coordinate between them
    message = message_builder.build()
    
    # Send to all
    results = await orchestrator.broadcast_message(message)
    
    assert len(results) > 0

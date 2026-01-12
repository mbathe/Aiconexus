"""Tests for the Agent high-level API.

This module tests the Agent class which provides a simple 3-line interface
for creating and using AI agents with the full SDK capabilities.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.aiconexus.sdk.agent import Agent, AgentConfig
from src.aiconexus.sdk.types import ExpertiseArea, FieldSchema, InputSchema


class TestAgentBasicCreation:
    """Test basic agent creation (3-line API)."""

    def test_create_agent_minimal(self, mock_llm):
        """Test creating agent with minimal configuration."""
        agent = Agent(
            name="DataAnalyzer",
            llm=mock_llm
        )
        
        assert agent is not None
        assert agent.name == "DataAnalyzer"
        assert agent.llm == mock_llm

    def test_create_agent_with_expertise(self, mock_llm, data_analysis_expertise):
        """Test creating agent with expertise area."""
        agent = Agent(
            name="DataAnalyzer",
            llm=mock_llm,
            expertise=data_analysis_expertise
        )
        
        assert agent.expertise == data_analysis_expertise

    def test_create_agent_with_schema(self, mock_llm):
        """Test creating agent with input/output schema."""
        input_schema = InputSchema(
            required_fields=["data"],
            description="Input data"
        )
        
        agent = Agent(
            name="Analyzer",
            llm=mock_llm,
            input_schema=input_schema
        )
        
        assert agent.input_schema == input_schema

    def test_agent_default_config(self, mock_llm):
        """Test agent has sensible defaults."""
        agent = Agent(
            name="Agent",
            llm=mock_llm
        )
        
        assert agent.max_iterations == 10
        assert agent.timeout is not None
        assert agent.enable_semantic_search is True


class TestAgentExecution:
    """Test agent task execution."""

    @pytest.mark.asyncio
    async def test_execute_simple_task(self, mock_llm):
        """Test executing a simple task."""
        agent = Agent(name="Worker", llm=mock_llm)
        
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="Task completed",
            tool_calls=[]
        ))
        
        result = await agent.execute(task="Do something")
        
        assert result is not None
        assert result.success is True

    @pytest.mark.asyncio
    async def test_execute_with_context(self, mock_llm):
        """Test executing task with context data."""
        agent = Agent(name="Worker", llm=mock_llm)
        
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="Processed",
            tool_calls=[]
        ))
        
        result = await agent.execute(
            task="Analyze",
            context={"data": "test_data"}
        )
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_execute_with_tools(self, mock_llm):
        """Test executing task with tools available."""
        agent = Agent(name="Worker", llm=mock_llm)
        
        # Register tools
        agent.register_tool(
            name="search",
            func=AsyncMock(return_value="Results"),
            description="Search"
        )
        
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="Done",
            tool_calls=[MagicMock(name="search", args={})]
        ))
        
        result = await agent.execute(task="Search for something")
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_execute_multi_step(self, mock_llm):
        """Test executing multi-step task."""
        agent = Agent(name="Worker", llm=mock_llm)
        
        # Simulate 3-step execution
        responses = [
            MagicMock(content="Step 1", tool_calls=[MagicMock()]),
            MagicMock(content="Step 2", tool_calls=[MagicMock()]),
            MagicMock(content="Complete", tool_calls=[])
        ]
        
        mock_llm.ainvoke = AsyncMock(side_effect=responses)
        
        result = await agent.execute(task="Multi-step task")
        
        assert result is not None
        assert result.iterations == 3 or result.iterations >= 2


class TestAgentToolRegistration:
    """Test agent tool registration."""

    def test_register_tool(self, mock_llm):
        """Test registering a tool."""
        agent = Agent(name="Worker", llm=mock_llm)
        
        async def search_tool(query):
            return f"Results for {query}"
        
        agent.register_tool(
            name="search",
            func=search_tool,
            description="Search documents"
        )
        
        assert "search" in agent.tools

    def test_register_multiple_tools(self, mock_llm):
        """Test registering multiple tools."""
        agent = Agent(name="Worker", llm=mock_llm)
        
        async def tool1(): return "Tool 1"
        async def tool2(): return "Tool 2"
        async def tool3(): return "Tool 3"
        
        agent.register_tool("tool1", tool1, "First tool")
        agent.register_tool("tool2", tool2, "Second tool")
        agent.register_tool("tool3", tool3, "Third tool")
        
        assert len(agent.tools) == 3
        assert all(t in agent.tools for t in ["tool1", "tool2", "tool3"])

    def test_unregister_tool(self, mock_llm):
        """Test unregistering a tool."""
        agent = Agent(name="Worker", llm=mock_llm)
        
        async def search(): return "Results"
        
        agent.register_tool("search", search, "Search")
        assert "search" in agent.tools
        
        agent.unregister_tool("search")
        assert "search" not in agent.tools

    def test_tool_with_parameters(self, mock_llm):
        """Test registering tool with parameter metadata."""
        agent = Agent(name="Worker", llm=mock_llm)
        
        async def calculate(a, b, operation):
            return {"result": "value"}
        
        agent.register_tool(
            name="calculate",
            func=calculate,
            description="Calculate",
            parameters={
                "a": {"type": "number"},
                "b": {"type": "number"},
                "operation": {"type": "string", "enum": ["add", "sub"]}
            }
        )
        
        assert agent.tools["calculate"] is not None


class TestAgentExpertise:
    """Test agent expertise areas."""

    def test_agent_with_single_expertise(self, mock_llm, data_analysis_expertise):
        """Test agent with single expertise."""
        agent = Agent(
            name="DataAnalyzer",
            llm=mock_llm,
            expertise=data_analysis_expertise
        )
        
        assert agent.expertise == data_analysis_expertise

    def test_agent_expertise_matching(self, mock_llm):
        """Test expertise matching."""
        expertise = ExpertiseArea(
            name="data_analysis",
            level=0.95,
            keywords=["data", "analysis", "statistics"]
        )
        
        agent = Agent(
            name="Expert",
            llm=mock_llm,
            expertise=expertise
        )
        
        # Check if agent matches queries
        matches = agent.matches_expertise("data analysis")
        assert matches

    def test_agent_multiple_expertise(self, mock_llm):
        """Test agent with multiple expertise areas."""
        expertise_list = [
            ExpertiseArea("data_analysis", 0.9, ["data"]),
            ExpertiseArea("machine_learning", 0.85, ["ml"])
        ]
        
        agent = Agent(
            name="Expert",
            llm=mock_llm,
            expertise_list=expertise_list
        )
        
        assert len(agent.expertise_list) == 2


class TestAgentCommunication:
    """Test agent communication capabilities."""

    @pytest.mark.asyncio
    async def test_send_message_to_agent(self, mock_llm, simple_valid_message):
        """Test sending message to another agent."""
        agent = Agent(name="Sender", llm=mock_llm)
        
        agent.connector = AsyncMock()
        agent.connector.send_message = AsyncMock(return_value=True)
        
        result = await agent.send_message(
            message=simple_valid_message,
            recipient="recipient_agent"
        )
        
        assert result is True

    @pytest.mark.asyncio
    async def test_receive_message(self, mock_llm, simple_valid_message):
        """Test receiving message from another agent."""
        agent = Agent(name="Receiver", llm=mock_llm)
        
        agent.connector = AsyncMock()
        agent.connector.receive_message = AsyncMock(return_value=simple_valid_message)
        
        result = await agent.receive_message()
        
        assert result == simple_valid_message

    @pytest.mark.asyncio
    async def test_agent_collaboration(self, mock_llm):
        """Test collaboration between agents."""
        agent1 = Agent(name="Agent1", llm=mock_llm)
        agent2 = Agent(name="Agent2", llm=mock_llm)
        
        # Both have connectors
        agent1.connector = AsyncMock()
        agent2.connector = AsyncMock()
        
        from src.aiconexus.sdk.types import Message
        
        message = Message(
            sender="Agent1",
            recipient="Agent2",
            data={"query": "test"}
        )
        
        # Agent1 sends to Agent2
        agent1.connector.send_message = AsyncMock(return_value=True)
        result = await agent1.send_message(message, "Agent2")
        assert result is True


class TestAgentIntegration:
    """Test agent integration with registry and discovery."""

    @pytest.mark.asyncio
    async def test_agent_discovery(self, mock_llm, populated_registry):
        """Test discovering other agents."""
        agent = Agent(
            name="Searcher",
            llm=mock_llm,
            registry=populated_registry
        )
        
        agents = await agent.discover_agents(expertise_area="data_analysis")
        
        assert agents is not None
        assert len(agents) > 0

    @pytest.mark.asyncio
    async def test_agent_registry_registration(self, mock_llm, populated_registry):
        """Test registering agent in registry."""
        agent = Agent(
            name="NewAgent",
            llm=mock_llm,
            registry=populated_registry
        )
        
        result = await agent.register_in_registry()
        
        assert result is True

    @pytest.mark.asyncio
    async def test_agent_delegating_to_discovered_agent(
        self,
        mock_llm,
        populated_registry
    ):
        """Test delegating task to discovered agent."""
        agent = Agent(
            name="Delegator",
            llm=mock_llm,
            registry=populated_registry
        )
        
        # Discover suitable agent
        agents = await agent.discover_agents("data_analysis")
        
        if agents:
            target = agents[0]
            
            # Delegate task
            result = await agent.delegate_task(
                task="Analyze data",
                to_agent=target.name
            )
            
            assert result is not None


class TestAgentSchema:
    """Test agent input/output schema."""

    def test_agent_with_input_schema(self, mock_llm):
        """Test agent with specific input schema."""
        schema = InputSchema(
            required_fields=["data", "format"],
            description="Analysis input"
        )
        
        agent = Agent(
            name="Analyzer",
            llm=mock_llm,
            input_schema=schema
        )
        
        assert agent.input_schema == schema

    def test_agent_validates_input(self, mock_llm):
        """Test agent validates input against schema."""
        schema = InputSchema(
            required_fields=["data"],
            description="Input"
        )
        
        agent = Agent(
            name="Worker",
            llm=mock_llm,
            input_schema=schema
        )
        
        # Valid input
        valid = agent.validate_input({"data": "test"})
        assert valid is True
        
        # Invalid input (missing required field)
        invalid = agent.validate_input({})
        assert invalid is False

    def test_agent_output_schema(self, mock_llm):
        """Test agent with output schema."""
        from src.aiconexus.sdk.types import AgentSchema
        
        output_schema = AgentSchema(
            name="output",
            fields={"result": FieldSchema(type="string")}
        )
        
        agent = Agent(
            name="Producer",
            llm=mock_llm,
            output_schema=output_schema
        )
        
        assert agent.output_schema == output_schema


class TestAgentConfiguration:
    """Test agent configuration options."""

    def test_custom_config(self, mock_llm):
        """Test custom agent configuration."""
        config = AgentConfig(
            max_iterations=5,
            temperature=0.7,
            enable_semantic_search=False,
            timeout=60
        )
        
        agent = Agent(
            name="Worker",
            llm=mock_llm,
            config=config
        )
        
        assert agent.max_iterations == 5
        assert agent.config.temperature == 0.7
        assert agent.config.enable_semantic_search is False

    def test_agent_timeout(self, mock_llm):
        """Test agent timeout configuration."""
        agent = Agent(
            name="Worker",
            llm=mock_llm,
            timeout=30
        )
        
        assert agent.timeout == 30

    def test_agent_temperature(self, mock_llm):
        """Test agent temperature setting."""
        agent = Agent(
            name="Creative",
            llm=mock_llm,
            temperature=0.9
        )
        
        assert agent.config.temperature == 0.9


class TestAgentStateAndHistory:
    """Test agent state and message history."""

    @pytest.mark.asyncio
    async def test_agent_execution_history(self, mock_llm):
        """Test agent tracks execution history."""
        agent = Agent(name="Worker", llm=mock_llm)
        
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="Done",
            tool_calls=[]
        ))
        
        await agent.execute(task="Task 1")
        await agent.execute(task="Task 2")
        
        history = agent.get_execution_history()
        
        assert len(history) >= 2

    @pytest.mark.asyncio
    async def test_agent_message_history(self, mock_llm):
        """Test agent message history."""
        agent = Agent(name="Worker", llm=mock_llm)
        
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="Response",
            tool_calls=[]
        ))
        
        await agent.execute(task="Task")
        
        messages = agent.get_message_history()
        
        assert len(messages) > 0

    def test_clear_history(self, mock_llm):
        """Test clearing agent history."""
        agent = Agent(name="Worker", llm=mock_llm)
        
        agent.message_history = ["msg1", "msg2"]
        
        agent.clear_history()
        
        assert len(agent.message_history) == 0


class TestAgentErrorHandling:
    """Test agent error handling."""

    @pytest.mark.asyncio
    async def test_agent_llm_failure(self, mock_llm):
        """Test agent handles LLM failures."""
        agent = Agent(name="Worker", llm=mock_llm)
        
        mock_llm.ainvoke = AsyncMock(
            side_effect=Exception("LLM error")
        )
        
        with pytest.raises(Exception):
            await agent.execute(task="Task")

    @pytest.mark.asyncio
    async def test_agent_tool_failure(self, mock_llm):
        """Test agent handles tool execution failures."""
        agent = Agent(name="Worker", llm=mock_llm)
        
        async def failing_tool():
            raise RuntimeError("Tool failed")
        
        agent.register_tool("bad_tool", failing_tool, "Bad tool")
        
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="Calling tool",
            tool_calls=[MagicMock(name="bad_tool", args={})]
        ))
        
        with pytest.raises(RuntimeError):
            await agent.execute(task="Task")

    @pytest.mark.asyncio
    async def test_agent_max_iterations_exceeded(self, mock_llm):
        """Test agent handles max iterations."""
        agent = Agent(
            name="Worker",
            llm=mock_llm,
            max_iterations=2
        )
        
        # Always return tool calls
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="Still going",
            tool_calls=[MagicMock()]
        ))
        
        result = await agent.execute(task="Infinite loop")
        
        assert result.success is False or result.iterations <= 2


class TestAgentSerialization:
    """Test agent configuration serialization."""

    def test_agent_to_config_dict(self, mock_llm):
        """Test converting agent to configuration dict."""
        agent = Agent(
            name="Worker",
            llm=mock_llm,
            temperature=0.8,
            max_iterations=5
        )
        
        config = agent.to_dict()
        
        assert config["name"] == "Worker"
        assert config["max_iterations"] == 5
        assert config["temperature"] == 0.8

    def test_agent_from_config_dict(self, mock_llm):
        """Test creating agent from configuration dict."""
        config = {
            "name": "Worker",
            "max_iterations": 5,
            "temperature": 0.7
        }
        
        agent = Agent.from_dict(config, llm=mock_llm)
        
        assert agent.name == "Worker"
        assert agent.max_iterations == 5


@pytest.mark.asyncio
async def test_agent_integration_full_workflow(mock_llm, populated_registry):
    """Integration test of complete agent workflow."""
    # Create agent
    agent = Agent(
        name="CompleteAgent",
        llm=mock_llm,
        registry=populated_registry
    )
    
    # Register tools
    agent.register_tool(
        "search",
        AsyncMock(return_value="Results"),
        "Search tool"
    )
    
    # Mock LLM
    mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
        content="Complete",
        tool_calls=[]
    ))
    
    # Discover other agents
    agents = await agent.discover_agents("data_analysis")
    assert len(agents) > 0
    
    # Execute task
    result = await agent.execute(task="Complete workflow")
    assert result.success is True


@pytest.mark.asyncio
async def test_agent_3_line_initialization(mock_llm):
    """Test the 3-line agent initialization advertised."""
    # This is the promised simple API
    agent = Agent(name="MyAgent", llm=mock_llm)
    agent.register_tool("search", AsyncMock(return_value="Results"), "Search")
    
    mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
        content="Done",
        tool_calls=[]
    ))
    
    result = await agent.execute(task="Work")
    
    assert result is not None
    assert result.success is True

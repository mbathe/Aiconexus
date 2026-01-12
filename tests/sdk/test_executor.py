"""Tests for the Executor module.

This module tests the Executor which implements the ReAct (Reasoning + Acting)
loop - iterating between thinking and acting until a task is completed.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.aiconexus.sdk.executor import (
    Executor,
    ExecutorConfig,
    ExecutionResult,
    ExecutionState
)
from src.aiconexus.sdk.types import Message, ToolCall, ReasoningStep


class TestExecutorInitialization:
    """Test Executor initialization."""

    def test_create_executor(self, mock_llm):
        """Test creating an executor with default config."""
        executor = Executor(llm=mock_llm)
        
        assert executor is not None
        assert executor.llm == mock_llm
        assert executor.max_iterations == 10

    def test_executor_with_custom_config(self, mock_llm):
        """Test executor with custom configuration."""
        config = ExecutorConfig(
            max_iterations=5,
            temperature=0.7,
            timeout_per_iteration=30
        )
        
        executor = Executor(llm=mock_llm, config=config)
        
        assert executor.config == config
        assert executor.max_iterations == 5

    def test_executor_config_validation(self, mock_llm):
        """Test executor config validation."""
        with pytest.raises((ValueError, AssertionError)):
            config = ExecutorConfig(max_iterations=0)  # Invalid
            executor = Executor(llm=mock_llm, config=config)

    def test_executor_state_initialization(self, mock_llm):
        """Test executor initializes with proper state."""
        executor = Executor(llm=mock_llm)
        
        assert executor.state == ExecutionState.IDLE
        assert executor.iteration_count == 0
        assert executor.message_history == []


class TestExecutorReActLoop:
    """Test the ReAct (Reasoning + Acting) loop."""

    @pytest.mark.asyncio
    async def test_single_iteration_loop(self, mock_llm, simple_valid_message):
        """Test a single iteration of the ReAct loop."""
        executor = Executor(llm=mock_llm)
        
        # Mock LLM response with reasoning and tool call
        reasoning_step = ReasoningStep(
            thought="I need to search for this information",
            action="search",
            observation="Found relevant information"
        )
        
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="Searching...",
            reasoning=[reasoning_step]
        ))
        
        result = await executor.execute(
            task="Find information about AI",
            tools=[{"name": "search"}]
        )
        
        assert result is not None
        assert executor.iteration_count >= 1

    @pytest.mark.asyncio
    async def test_multiple_iterations_loop(self, mock_llm):
        """Test multiple iterations until completion."""
        executor = Executor(llm=mock_llm, config=ExecutorConfig(max_iterations=3))
        
        # Mock multiple iterations
        responses = [
            MagicMock(content="Iteration 1", tool_calls=[
                MagicMock(name="search", args={"query": "test"})
            ]),
            MagicMock(content="Iteration 2", tool_calls=[
                MagicMock(name="analyze", args={"data": "results"})
            ]),
            MagicMock(content="Done", tool_calls=[])
        ]
        
        mock_llm.ainvoke = AsyncMock(side_effect=responses)
        
        result = await executor.execute(
            task="Complex task",
            tools=[{"name": "search"}, {"name": "analyze"}]
        )
        
        assert result is not None
        assert executor.iteration_count <= 3

    @pytest.mark.asyncio
    async def test_early_termination(self, mock_llm):
        """Test early termination when task is complete."""
        executor = Executor(llm=mock_llm, config=ExecutorConfig(max_iterations=10))
        
        # Complete on second iteration
        responses = [
            MagicMock(content="Iteration 1", tool_calls=[MagicMock()]),
            MagicMock(content="Task complete", tool_calls=[])
        ]
        
        mock_llm.ainvoke = AsyncMock(side_effect=responses)
        
        result = await executor.execute(
            task="Quick task",
            tools=[{"name": "search"}]
        )
        
        # Should stop before max iterations
        assert executor.iteration_count == 2

    @pytest.mark.asyncio
    async def test_max_iterations_reached(self, mock_llm):
        """Test handling of max iterations limit."""
        executor = Executor(llm=mock_llm, config=ExecutorConfig(max_iterations=2))
        
        # Always return tool calls (never complete)
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="Still processing",
            tool_calls=[MagicMock(name="search")]
        ))
        
        result = await executor.execute(
            task="Never-ending task",
            tools=[{"name": "search"}]
        )
        
        # Should stop at max iterations
        assert executor.iteration_count == 2
        assert result is not None
        assert not result.success


class TestExecutorToolExecution:
    """Test tool execution within the executor."""

    @pytest.mark.asyncio
    async def test_execute_tool_call(self, mock_llm):
        """Test executing a tool call."""
        executor = Executor(llm=mock_llm)
        
        tool_call = ToolCall(
            id="call_123",
            name="search",
            args={"query": "test"}
        )
        
        # Mock tool execution
        executor.tool_registry = {
            "search": AsyncMock(return_value="Search results")
        }
        
        result = await executor._execute_tool(tool_call)
        
        assert result is not None
        assert result == "Search results"

    @pytest.mark.asyncio
    async def test_tool_not_found(self, mock_llm):
        """Test handling of non-existent tool."""
        executor = Executor(llm=mock_llm)
        executor.tool_registry = {}
        
        tool_call = ToolCall(
            id="call_123",
            name="nonexistent",
            args={}
        )
        
        with pytest.raises((KeyError, ValueError)):
            await executor._execute_tool(tool_call)

    @pytest.mark.asyncio
    async def test_tool_execution_error(self, mock_llm):
        """Test handling of tool execution errors."""
        executor = Executor(llm=mock_llm)
        
        async def failing_tool(*args, **kwargs):
            raise RuntimeError("Tool failed")
        
        executor.tool_registry = {"search": failing_tool}
        
        tool_call = ToolCall(
            id="call_123",
            name="search",
            args={}
        )
        
        with pytest.raises(RuntimeError):
            await executor._execute_tool(tool_call)

    @pytest.mark.asyncio
    async def test_parallel_tool_execution(self, mock_llm):
        """Test executing multiple tools in parallel."""
        executor = Executor(llm=mock_llm)
        
        tool_calls = [
            ToolCall(id="call_1", name="search", args={"q": "a"}),
            ToolCall(id="call_2", name="analyze", args={"data": "x"}),
            ToolCall(id="call_3", name="summarize", args={"text": "y"})
        ]
        
        executor.tool_registry = {
            "search": AsyncMock(return_value="results_a"),
            "analyze": AsyncMock(return_value="results_x"),
            "summarize": AsyncMock(return_value="results_y")
        }
        
        results = await executor._execute_tools_parallel(tool_calls)
        
        assert len(results) == 3
        assert all(r is not None for r in results)


class TestExecutorMessageHistory:
    """Test message history management."""

    @pytest.mark.asyncio
    async def test_message_history_tracking(self, mock_llm):
        """Test that message history is properly tracked."""
        executor = Executor(llm=mock_llm)
        
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="Response",
            tool_calls=[]
        ))
        
        result = await executor.execute(
            task="Simple task",
            tools=[]
        )
        
        assert len(executor.message_history) > 0
        
        # History should contain the task and response
        messages = executor.message_history
        assert any(m.sender == "user" for m in messages if hasattr(m, 'sender'))

    @pytest.mark.asyncio
    async def test_history_context_in_iterations(self, mock_llm):
        """Test that history is passed to LLM in each iteration."""
        executor = Executor(llm=mock_llm)
        
        responses = [
            MagicMock(content="Step 1", tool_calls=[MagicMock()]),
            MagicMock(content="Step 2", tool_calls=[])
        ]
        
        mock_llm.ainvoke = AsyncMock(side_effect=responses)
        
        result = await executor.execute(
            task="Multi-step task",
            tools=[{"name": "search"}]
        )
        
        # Each call should include accumulated history
        call_args_list = mock_llm.ainvoke.call_args_list
        assert len(call_args_list) >= 2

    @pytest.mark.asyncio
    async def test_clear_history(self, mock_llm):
        """Test clearing message history."""
        executor = Executor(llm=mock_llm)
        
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="Response",
            tool_calls=[]
        ))
        
        await executor.execute(task="Task", tools=[])
        
        assert len(executor.message_history) > 0
        
        executor.clear_history()
        
        assert len(executor.message_history) == 0


class TestExecutorReasoningSteps:
    """Test reasoning step tracking."""

    @pytest.mark.asyncio
    async def test_reasoning_step_capture(self, mock_llm):
        """Test capturing reasoning steps."""
        executor = Executor(llm=mock_llm)
        
        reasoning = ReasoningStep(
            thought="I need to search",
            action="search",
            observation="Found data"
        )
        
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="Searching",
            reasoning=[reasoning],
            tool_calls=[]
        ))
        
        result = await executor.execute(task="Task", tools=[])
        
        assert result is not None
        if hasattr(result, 'reasoning_steps'):
            assert len(result.reasoning_steps) > 0

    @pytest.mark.asyncio
    async def test_reasoning_without_tool_calls(self, mock_llm):
        """Test reasoning when no tool call is made."""
        executor = Executor(llm=mock_llm)
        
        reasoning = ReasoningStep(
            thought="The answer is 42",
            action="conclude",
            observation="No tool needed"
        )
        
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="The answer is 42",
            reasoning=[reasoning],
            tool_calls=[]
        ))
        
        result = await executor.execute(task="What's the answer?", tools=[])
        
        assert result is not None


class TestExecutorState:
    """Test executor state management."""

    @pytest.mark.asyncio
    async def test_state_transitions(self, mock_llm):
        """Test proper state transitions during execution."""
        executor = Executor(llm=mock_llm)
        
        assert executor.state == ExecutionState.IDLE
        
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="Done",
            tool_calls=[]
        ))
        
        # Start execution
        task = executor.execute(task="Test", tools=[])
        
        # State should change to RUNNING (or similar)
        # Note: Implementation may vary
        
        result = await task
        
        # Execution completed
        assert executor.state in [ExecutionState.IDLE, ExecutionState.COMPLETED]

    @pytest.mark.asyncio
    async def test_state_on_error(self, mock_llm):
        """Test state on execution error."""
        executor = Executor(llm=mock_llm)
        
        mock_llm.ainvoke = AsyncMock(
            side_effect=RuntimeError("LLM error")
        )
        
        with pytest.raises(RuntimeError):
            await executor.execute(task="Test", tools=[])
        
        # State should reflect error
        assert executor.state != ExecutionState.COMPLETED


class TestExecutorTimeout:
    """Test timeout handling."""

    @pytest.mark.asyncio
    async def test_iteration_timeout(self, mock_llm):
        """Test timeout on individual iteration."""
        import asyncio
        
        executor = Executor(
            llm=mock_llm,
            config=ExecutorConfig(timeout_per_iteration=0.1)
        )
        
        # Simulate slow LLM
        async def slow_response(*args, **kwargs):
            await asyncio.sleep(1)
            return MagicMock(content="Late response", tool_calls=[])
        
        mock_llm.ainvoke = slow_response
        
        with pytest.raises((asyncio.TimeoutError, RuntimeError)):
            await executor.execute(task="Test", tools=[])

    @pytest.mark.asyncio
    async def test_total_timeout(self, mock_llm):
        """Test total execution timeout."""
        import asyncio
        
        executor = Executor(
            llm=mock_llm,
            config=ExecutorConfig(
                max_iterations=100,
                timeout_per_iteration=0.1
            )
        )
        
        call_count = [0]
        
        async def slow_response(*args, **kwargs):
            call_count[0] += 1
            await asyncio.sleep(0.05)
            return MagicMock(
                content="Still going",
                tool_calls=[MagicMock()] if call_count[0] < 100 else []
            )
        
        mock_llm.ainvoke = slow_response
        
        # Should eventually complete or timeout
        result = await executor.execute(task="Test", tools=[])
        assert result is not None


class TestExecutorWithInterAgentCommunication:
    """Test executor with inter-agent communication."""

    @pytest.mark.asyncio
    async def test_send_message_to_agent(self, mock_llm, simple_valid_message):
        """Test sending message to another agent."""
        executor = Executor(llm=mock_llm)
        
        # Mock connector for agent communication
        executor.connector = AsyncMock()
        executor.connector.send_message = AsyncMock(return_value=True)
        
        message_to_send = simple_valid_message
        
        result = await executor.send_to_agent(
            message=message_to_send,
            agent_endpoint="http://agent:8000"
        )
        
        assert result is True
        executor.connector.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_receive_from_agent(self, mock_llm, simple_valid_message):
        """Test receiving message from another agent."""
        executor = Executor(llm=mock_llm)
        
        executor.connector = AsyncMock()
        executor.connector.receive_message = AsyncMock(
            return_value=simple_valid_message
        )
        
        result = await executor.receive_from_agent()
        
        assert result == simple_valid_message


class TestExecutorResult:
    """Test execution result."""

    def test_execution_result_success(self):
        """Test successful execution result."""
        result = ExecutionResult(
            success=True,
            output="Task completed successfully",
            iterations=3,
            reasoning_steps=[],
            final_message="Done"
        )
        
        assert result.success is True
        assert result.output == "Task completed successfully"
        assert result.iterations == 3

    def test_execution_result_failure(self):
        """Test failed execution result."""
        result = ExecutionResult(
            success=False,
            output=None,
            error="Max iterations reached",
            iterations=10
        )
        
        assert result.success is False
        assert result.error == "Max iterations reached"
        assert result.iterations == 10


@pytest.mark.asyncio
async def test_executor_integration_full_loop(mock_llm_with_tools):
    """Integration test of complete executor loop."""
    executor = Executor(
        llm=mock_llm_with_tools,
        config=ExecutorConfig(max_iterations=5)
    )
    
    tools = [
        {
            "name": "search",
            "description": "Search",
            "parameters": {}
        },
        {
            "name": "analyze",
            "description": "Analyze",
            "parameters": {}
        }
    ]
    
    result = await executor.execute(
        task="Find and analyze information",
        tools=tools
    )
    
    assert result is not None
    assert result.success is not None
    assert executor.iteration_count > 0


@pytest.mark.asyncio
async def test_executor_complex_workflow(mock_llm):
    """Test complex multi-step workflow."""
    executor = Executor(llm=mock_llm, config=ExecutorConfig(max_iterations=5))
    
    # Simulate 3-step workflow
    responses = [
        MagicMock(
            content="Step 1: Searching",
            tool_calls=[MagicMock(name="search", args={"q": "data"})]
        ),
        MagicMock(
            content="Step 2: Analyzing",
            tool_calls=[MagicMock(name="analyze", args={"data": "x"})]
        ),
        MagicMock(
            content="Complete",
            tool_calls=[]
        )
    ]
    
    mock_llm.ainvoke = AsyncMock(side_effect=responses)
    
    result = await executor.execute(
        task="Multi-step workflow",
        tools=[{"name": "search"}, {"name": "analyze"}]
    )
    
    assert result is not None
    assert executor.iteration_count == 3

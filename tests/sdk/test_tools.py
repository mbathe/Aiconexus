"""Tests for the Tool Calling abstraction module.

This module tests the ToolCall abstraction which provides a unified interface
for calling tools across different LLM models (native calling vs synthetic).
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from src.aiconexus.sdk.tools import (
    ToolCall,
    ToolCallResult,
    ToolCallAbstraction,
    NativeToolCaller,
    SyntheticToolCaller,
    detect_tool_calling_capability
)


class TestToolCallBasics:
    """Test basic ToolCall functionality."""

    def test_create_tool_call(self):
        """Test creating a basic tool call."""
        call = ToolCall(
            id="call_123",
            name="search",
            args={"query": "test"}
        )
        
        assert call.id == "call_123"
        assert call.name == "search"
        assert call.args == {"query": "test"}

    def test_tool_call_with_complex_args(self):
        """Test tool call with complex nested arguments."""
        args = {
            "filters": {
                "date": "2025-01-15",
                "status": ["active", "pending"]
            },
            "limit": 10
        }
        
        call = ToolCall(
            id="call_456",
            name="query_database",
            args=args
        )
        
        assert call.args == args
        assert call.args["filters"]["date"] == "2025-01-15"

    def test_tool_call_result(self):
        """Test ToolCallResult creation."""
        result = ToolCallResult(
            call_id="call_123",
            success=True,
            output="Found 5 results",
            error=None
        )
        
        assert result.call_id == "call_123"
        assert result.success is True
        assert result.output == "Found 5 results"
        assert result.error is None

    def test_tool_call_result_with_error(self):
        """Test ToolCallResult with error."""
        result = ToolCallResult(
            call_id="call_123",
            success=False,
            output=None,
            error="Database connection failed"
        )
        
        assert result.success is False
        assert result.error == "Database connection failed"
        assert result.output is None


class TestNativeToolCalling:
    """Test native tool calling for models that support it."""

    @pytest.mark.asyncio
    async def test_native_tool_calling_gpt4(self):
        """Test native tool calling with GPT-4."""
        mock_llm = AsyncMock()
        mock_llm.model_name = "gpt-4"
        
        # Mock GPT-4 response with tool_calls
        tool_call_obj = MagicMock()
        tool_call_obj.id = "call_123"
        tool_call_obj.function.name = "search"
        tool_call_obj.function.arguments = '{"query": "AI"}'
        
        response = MagicMock()
        response.content = "Searching..."
        response.tool_calls = [tool_call_obj]
        
        mock_llm.ainvoke = AsyncMock(return_value=response)
        
        caller = NativeToolCaller(llm=mock_llm)
        
        tools = [
            {"name": "search", "description": "Search", "parameters": {}}
        ]
        
        result = await caller.call_tools(
            message="Search for AI",
            tools=tools
        )
        
        assert result is not None
        mock_llm.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_native_tool_calling_claude(self):
        """Test native tool calling with Claude."""
        mock_llm = AsyncMock()
        mock_llm.model_name = "claude-3-5-sonnet-20241022"
        
        tool_use_obj = MagicMock()
        tool_use_obj.id = "call_456"
        tool_use_obj.type = "tool_use"
        tool_use_obj.name = "calculate"
        tool_use_obj.input = {"operation": "sum", "values": [1, 2, 3]}
        
        response = MagicMock()
        response.content = [tool_use_obj]
        
        mock_llm.ainvoke = AsyncMock(return_value=response)
        
        caller = NativeToolCaller(llm=mock_llm)
        
        tools = [
            {"name": "calculate", "description": "Calculate", "parameters": {}}
        ]
        
        result = await caller.call_tools(
            message="Sum 1, 2, 3",
            tools=tools
        )
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_native_tool_calling_multiple_tools(self):
        """Test native calling with multiple tool invocations."""
        mock_llm = AsyncMock()
        mock_llm.model_name = "gpt-4"
        
        tool_call1 = MagicMock()
        tool_call1.id = "call_1"
        tool_call1.function.name = "search"
        tool_call1.function.arguments = '{"query": "python"}'
        
        tool_call2 = MagicMock()
        tool_call2.id = "call_2"
        tool_call2.function.name = "analyze"
        tool_call2.function.arguments = '{"text": "python docs"}'
        
        response = MagicMock()
        response.tool_calls = [tool_call1, tool_call2]
        
        mock_llm.ainvoke = AsyncMock(return_value=response)
        
        caller = NativeToolCaller(llm=mock_llm)
        
        tools = [
            {"name": "search", "description": "Search"},
            {"name": "analyze", "description": "Analyze"}
        ]
        
        result = await caller.call_tools(
            message="Find and analyze python docs",
            tools=tools
        )
        
        assert result is not None


class TestSyntheticToolCalling:
    """Test synthetic tool calling for models without native support."""

    @pytest.mark.asyncio
    async def test_synthetic_tool_calling_with_json(self):
        """Test synthetic tool calling with JSON output."""
        mock_llm = AsyncMock()
        
        response = MagicMock()
        response.content = '''
        {
            "tools": [
                {
                    "name": "search",
                    "args": {"query": "AI"}
                }
            ]
        }
        '''
        
        mock_llm.ainvoke = AsyncMock(return_value=response)
        
        caller = SyntheticToolCaller(
            llm=mock_llm,
            output_format="json"
        )
        
        tools = [{"name": "search", "description": "Search"}]
        
        result = await caller.call_tools(
            message="Search for AI",
            tools=tools
        )
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_synthetic_tool_calling_with_xml(self):
        """Test synthetic tool calling with XML output."""
        mock_llm = AsyncMock()
        
        response = MagicMock()
        response.content = '''
        <tools>
            <tool>
                <name>calculate</name>
                <args>
                    <operation>sum</operation>
                    <values>1,2,3</values>
                </args>
            </tool>
        </tools>
        '''
        
        mock_llm.ainvoke = AsyncMock(return_value=response)
        
        caller = SyntheticToolCaller(
            llm=mock_llm,
            output_format="xml"
        )
        
        tools = [{"name": "calculate", "description": "Calculate"}]
        
        result = await caller.call_tools(
            message="Sum these numbers",
            tools=tools
        )
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_synthetic_tool_calling_with_markdown(self):
        """Test synthetic tool calling with markdown output."""
        mock_llm = AsyncMock()
        
        response = MagicMock()
        response.content = '''
        I will call the search tool.
        
        **Tool:** search
        **Arguments:**
        - query: test
        '''
        
        mock_llm.ainvoke = AsyncMock(return_value=response)
        
        caller = SyntheticToolCaller(
            llm=mock_llm,
            output_format="markdown"
        )
        
        tools = [{"name": "search", "description": "Search"}]
        
        # Note: markdown parsing may be custom
        result = await caller.call_tools(
            message="Search for test",
            tools=tools
        )
        
        assert result is not None


class TestDetectToolCallingCapability:
    """Test detection of tool calling capability."""

    @pytest.mark.parametrize("model_name,expected_native", [
        ("gpt-4", True),
        ("gpt-4-turbo", True),
        ("gpt-3.5-turbo", True),
        ("claude-3-5-sonnet-20241022", True),
        ("claude-3-opus", True),
        ("claude-3-haiku", True),
        ("llama-2-70b", False),
        ("mistral-7b", False),
        ("phi-2", False),
    ])
    def test_detect_capability(self, model_name, expected_native):
        """Test detection of native tool calling capability."""
        capability = detect_tool_calling_capability(model_name)
        
        assert capability["supports_native"] == expected_native
        assert "output_format" in capability
        if expected_native:
            assert capability["output_format"] in ["openai", "anthropic"]

    def test_detect_capability_unknown_model(self):
        """Test detection for unknown model."""
        capability = detect_tool_calling_capability("unknown-model-xyz")
        
        assert capability["supports_native"] is False
        assert capability["output_format"] == "synthetic"


class TestToolCallAbstraction:
    """Test the ToolCallAbstraction wrapper."""

    @pytest.mark.asyncio
    async def test_abstraction_with_native_model(self):
        """Test abstraction automatically uses native calling."""
        mock_llm = AsyncMock()
        mock_llm.model_name = "gpt-4"
        
        tool_call_obj = MagicMock()
        tool_call_obj.id = "call_123"
        tool_call_obj.function.name = "search"
        tool_call_obj.function.arguments = '{"query": "test"}'
        
        response = MagicMock()
        response.tool_calls = [tool_call_obj]
        
        mock_llm.ainvoke = AsyncMock(return_value=response)
        
        abstraction = ToolCallAbstraction(llm=mock_llm)
        
        tools = [{"name": "search", "description": "Search"}]
        
        result = await abstraction.call_tools(
            message="Search for test",
            tools=tools
        )
        
        assert result is not None
        assert abstraction._caller.__class__.__name__ == "NativeToolCaller"

    @pytest.mark.asyncio
    async def test_abstraction_with_synthetic_model(self):
        """Test abstraction uses synthetic calling for unsupported models."""
        mock_llm = AsyncMock()
        mock_llm.model_name = "llama-2-70b"
        
        response = MagicMock()
        response.content = '{"tools": [{"name": "search", "args": {"query": "test"}}]}'
        
        mock_llm.ainvoke = AsyncMock(return_value=response)
        
        abstraction = ToolCallAbstraction(llm=mock_llm)
        
        tools = [{"name": "search", "description": "Search"}]
        
        result = await abstraction.call_tools(
            message="Search for test",
            tools=tools
        )
        
        assert result is not None
        assert abstraction._caller.__class__.__name__ == "SyntheticToolCaller"

    @pytest.mark.asyncio
    async def test_abstraction_with_custom_output_format(self):
        """Test specifying custom output format for synthetic calling."""
        mock_llm = AsyncMock()
        mock_llm.model_name = "llama-2-70b"
        
        response = MagicMock()
        response.content = '<tools><tool name="search"/></tools>'
        
        mock_llm.ainvoke = AsyncMock(return_value=response)
        
        abstraction = ToolCallAbstraction(
            llm=mock_llm,
            force_synthetic=True,
            output_format="xml"
        )
        
        tools = [{"name": "search", "description": "Search"}]
        
        result = await abstraction.call_tools(
            message="Search",
            tools=tools
        )
        
        assert result is not None


class TestToolCallErrorHandling:
    """Test error handling in tool calling."""

    @pytest.mark.asyncio
    async def test_parse_error_in_native_calling(self):
        """Test handling of JSON parse errors."""
        mock_llm = AsyncMock()
        mock_llm.model_name = "gpt-4"
        
        tool_call_obj = MagicMock()
        tool_call_obj.id = "call_123"
        tool_call_obj.function.name = "search"
        tool_call_obj.function.arguments = "invalid json {{"
        
        response = MagicMock()
        response.tool_calls = [tool_call_obj]
        
        mock_llm.ainvoke = AsyncMock(return_value=response)
        
        caller = NativeToolCaller(llm=mock_llm)
        
        with pytest.raises((json.JSONDecodeError, ValueError)):
            await caller.call_tools(
                message="Search",
                tools=[{"name": "search"}]
            )

    @pytest.mark.asyncio
    async def test_invalid_tool_name(self):
        """Test calling tool that doesn't exist."""
        mock_llm = AsyncMock()
        mock_llm.model_name = "gpt-4"
        
        tool_call_obj = MagicMock()
        tool_call_obj.id = "call_123"
        tool_call_obj.function.name = "nonexistent_tool"
        tool_call_obj.function.arguments = '{}'
        
        response = MagicMock()
        response.tool_calls = [tool_call_obj]
        
        mock_llm.ainvoke = AsyncMock(return_value=response)
        
        caller = NativeToolCaller(llm=mock_llm)
        
        with pytest.raises((ValueError, KeyError)):
            await caller.call_tools(
                message="Call invalid tool",
                tools=[{"name": "search"}]
            )

    @pytest.mark.asyncio
    async def test_llm_failure_handling(self):
        """Test handling of LLM failures."""
        mock_llm = AsyncMock()
        mock_llm.model_name = "gpt-4"
        mock_llm.ainvoke = AsyncMock(
            side_effect=Exception("API rate limited")
        )
        
        caller = NativeToolCaller(llm=mock_llm)
        
        with pytest.raises(Exception):
            await caller.call_tools(
                message="Search",
                tools=[{"name": "search"}]
            )


class TestMixedToolScenarios:
    """Test scenarios with mixed tool types."""

    @pytest.mark.asyncio
    async def test_no_tools_called(self):
        """Test when model decides no tools are needed."""
        mock_llm = AsyncMock()
        mock_llm.model_name = "gpt-4"
        
        response = MagicMock()
        response.content = "I can answer this without tools."
        response.tool_calls = []
        
        mock_llm.ainvoke = AsyncMock(return_value=response)
        
        caller = NativeToolCaller(llm=mock_llm)
        
        result = await caller.call_tools(
            message="What's 2+2?",
            tools=[{"name": "calculate"}]
        )
        
        # Should handle gracefully
        assert result is not None

    @pytest.mark.asyncio
    async def test_partial_tool_execution(self):
        """Test partial success in tool execution."""
        mock_llm = AsyncMock()
        mock_llm.model_name = "gpt-4"
        
        tool_call1 = MagicMock()
        tool_call1.id = "call_1"
        tool_call1.function.name = "search"
        tool_call1.function.arguments = '{"query": "valid"}'
        
        tool_call2 = MagicMock()
        tool_call2.id = "call_2"
        tool_call2.function.name = "search"
        tool_call2.function.arguments = "invalid json"
        
        response = MagicMock()
        response.tool_calls = [tool_call1, tool_call2]
        
        mock_llm.ainvoke = AsyncMock(return_value=response)
        
        caller = NativeToolCaller(llm=mock_llm)
        
        # Should attempt to handle both, but one will fail
        with pytest.raises((json.JSONDecodeError, ValueError)):
            await caller.call_tools(
                message="Multiple searches",
                tools=[{"name": "search"}]
            )


class TestToolCallContext:
    """Test tool calls in execution context."""

    @pytest.mark.asyncio
    async def test_tool_call_with_history(self):
        """Test tool calls preserving message history."""
        mock_llm = AsyncMock()
        mock_llm.model_name = "gpt-4"
        
        tool_call_obj = MagicMock()
        tool_call_obj.id = "call_123"
        tool_call_obj.function.name = "search"
        tool_call_obj.function.arguments = '{"query": "previous"}'
        
        response = MagicMock()
        response.tool_calls = [tool_call_obj]
        
        mock_llm.ainvoke = AsyncMock(return_value=response)
        
        caller = NativeToolCaller(llm=mock_llm)
        
        messages = [
            {"role": "user", "content": "Search for previous"},
            {"role": "assistant", "content": "I'll search"}
        ]
        
        result = await caller.call_tools(
            message="Search for previous",
            tools=[{"name": "search"}],
            context_messages=messages
        )
        
        assert result is not None


@pytest.mark.asyncio
async def test_tool_calling_integration(mock_llm_with_tools):
    """Integration test of complete tool calling flow."""
    tools = [
        {
            "name": "search",
            "description": "Search the knowledge base",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        }
    ]
    
    abstraction = ToolCallAbstraction(llm=mock_llm_with_tools)
    
    result = await abstraction.call_tools(
        message="Search for information about AI",
        tools=tools
    )
    
    assert result is not None

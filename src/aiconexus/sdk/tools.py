"""
Tool Calling Manager
Handles both native and synthetic tool calling for LLMs
This is the key component that makes all models work with tools
"""

from typing import List, Dict, Any, Optional, Tuple
import json
import re
import logging
from abc import ABC, abstractmethod

from .types import Tool

logger = logging.getLogger(__name__)


class ToolCallingExecutor(ABC):
    """Abstract executor for tool calling"""
    
    @abstractmethod
    async def call_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """Execute a tool"""
        pass
    
    @abstractmethod
    async def get_llm_tools_format(self) -> Any:
        """Get tools in LLM-compatible format"""
        pass


class NativeToolCallingExecutor(ToolCallingExecutor):
    """
    Executor for models with native tool calling support
    (GPT-4, Claude 3, etc)
    """
    
    def __init__(self, llm: Any):
        self.llm = llm
        self.tools = []
        self.tools_dict = {}
    
    def set_tools(self, tools: List[Tool]):
        """Register tools"""
        self.tools = tools
        self.tools_dict = {tool.name: tool for tool in tools}
    
    async def call_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """Call a tool"""
        tool = self.tools_dict.get(tool_name)
        if not tool:
            return json.dumps({"error": f"Tool not found: {tool_name}"})
        
        try:
            if tool.async_func:
                result = await tool.func(**tool_args)
            else:
                result = tool.func(**tool_args)
            
            # Convert result to string/JSON
            if isinstance(result, (dict, list)):
                return json.dumps(result)
            return str(result)
        
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def get_llm_tools_format(self) -> List[Dict[str, Any]]:
        """Convert tools to LangChain format"""
        from langchain.tools import Tool as LCTool
        
        lc_tools = []
        for tool in self.tools:
            lc_tool = LCTool.from_function(
                func=tool.func,
                name=tool.name,
                description=tool.description
            )
            lc_tools.append(lc_tool)
        
        return lc_tools


class SyntheticToolCallingExecutor(ToolCallingExecutor):
    """
    Executor for models WITHOUT native tool calling support
    Uses XML-based prompting to simulate tool calling
    Works with any model: Llama, Mistral, local models, etc
    """
    
    def __init__(self, llm: Any):
        self.llm = llm
        self.tools = []
        self.tools_dict = {}
    
    def set_tools(self, tools: List[Tool]):
        """Register tools"""
        self.tools = tools
        self.tools_dict = {tool.name: tool for tool in tools}
    
    async def call_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """Call a tool"""
        tool = self.tools_dict.get(tool_name)
        if not tool:
            return json.dumps({"error": f"Tool not found: {tool_name}"})
        
        try:
            if tool.async_func:
                result = await tool.func(**tool_args)
            else:
                result = tool.func(**tool_args)
            
            if isinstance(result, (dict, list)):
                return json.dumps(result)
            return str(result)
        
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def get_tools_schema(self) -> str:
        """Generate XML schema for tools"""
        schema = ""
        
        for tool in self.tools:
            schema += f"""
<tool>
  <name>{tool.name}</name>
  <description>{tool.description}</description>
  <usage>
    <tool name="{tool.name}">
      <arg name="param1">value1</arg>
      <arg name="param2">value2</arg>
    </tool>
  </usage>
</tool>
"""
        
        return schema
    
    async def get_llm_tools_format(self) -> str:
        """Return tools in XML format for synthetic calling"""
        return self.get_tools_schema()


class ToolCallingManager:
    """
    Main manager for tool calling
    Automatically chooses between native and synthetic
    """
    
    def __init__(
        self,
        llm: Any,
        model_name: Optional[str] = None,
        force_synthetic: bool = False
    ):
        self.llm = llm
        self.model_name = model_name or str(llm)
        self.tools = []
        
        # Determine if model supports native tools
        self.supports_native_tools = self._check_native_tool_support()
        
        if force_synthetic:
            self.supports_native_tools = False
        
        # Create appropriate executor
        if self.supports_native_tools:
            logger.info(f"Using NATIVE tool calling for {self.model_name}")
            self.executor = NativeToolCallingExecutor(llm)
        else:
            logger.info(f"Using SYNTHETIC tool calling for {self.model_name}")
            self.executor = SyntheticToolCallingExecutor(llm)
    
    def _check_native_tool_support(self) -> bool:
        """Check if model supports native tool calling"""
        model_str = self.model_name.lower()
        
        # Models with native support
        native_models = [
            "gpt-4", "gpt-3.5", "gpt4", "gpt35",
            "claude-3", "claude3",
            "command-r", "cohere",
            "mistral-large",
            "gemini"
        ]
        
        for model in native_models:
            if model in model_str:
                return True
        
        return False
    
    def register_tools(self, tools: List[Tool]):
        """Register tools"""
        self.tools = tools
        self.executor.set_tools(tools)
        logger.info(f"Registered {len(tools)} tools")
    
    async def call_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """Call a tool"""
        logger.debug(f"Calling tool: {tool_name}({tool_args})")
        return await self.executor.call_tool(tool_name, tool_args)
    
    async def get_tools_for_llm(self) -> Any:
        """Get tools in format for LLM"""
        return await self.executor.get_llm_tools_format()
    
    def get_system_prompt_tools_section(self) -> str:
        """
        Get the tools section for system prompt
        Different for native vs synthetic
        """
        
        if self.supports_native_tools:
            return self._get_native_tools_section()
        else:
            return self._get_synthetic_tools_section()
    
    def _get_native_tools_section(self) -> str:
        """System prompt section for native tools"""
        tools_list = ", ".join([f"'{t.name}'" for t in self.tools])
        return f"""
You have access to the following tools: {tools_list}

Use them when you need to perform actions or gather information.
Call tools using the native tool calling interface.
"""
    
    def _get_synthetic_tools_section(self) -> str:
        """System prompt section for synthetic tools"""
        tools_desc = ""
        
        for tool in self.tools:
            tools_desc += f"""
<tool>
  <name>{tool.name}</name>
  <description>{tool.description}</description>
</tool>
"""
        
        return f"""
You have access to the following tools:

{tools_desc}

To use a tool, write:
<tool name="tool_name">
  <arg name="param1">value1</arg>
  <arg name="param2">value2</arg>
</tool>

The tool result will be provided in the next message.
"""
    
    def parse_tool_call_from_response(self, response: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Parse tool call from LLM response
        Returns: (tool_name, tool_args) or None
        """
        
        if self.supports_native_tools:
            return self._parse_native_tool_call(response)
        else:
            return self._parse_synthetic_tool_call(response)
    
    def _parse_native_tool_call(self, response: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Parse native tool calls (JSON)"""
        try:
            # Try to find JSON block
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                # Try to find JSON object directly
                json_str = response[response.find("{"):response.rfind("}")+1]
            
            data = json.loads(json_str)
            
            if "tool_name" in data and "tool_args" in data:
                return (data["tool_name"], data["tool_args"])
            elif "name" in data and "arguments" in data:
                return (data["name"], data["arguments"])
        
        except (json.JSONDecodeError, ValueError):
            pass
        
        return None
    
    def _parse_synthetic_tool_call(self, response: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Parse synthetic tool calls (XML)"""
        # Match: <tool name="tool_name"><arg name="param">value</arg></tool>
        match = re.search(
            r'<tool name="(\w+)">(.+?)</tool>',
            response,
            re.DOTALL
        )
        
        if not match:
            return None
        
        tool_name = match.group(1)
        args_section = match.group(2)
        
        # Parse arguments
        tool_args = {}
        for arg_match in re.finditer(
            r'<arg name="(\w+)">(.+?)</arg>',
            args_section,
            re.DOTALL
        ):
            arg_name = arg_match.group(1)
            arg_value = arg_match.group(2).strip()
            
            # Try to parse as JSON
            try:
                tool_args[arg_name] = json.loads(arg_value)
            except:
                tool_args[arg_name] = arg_value
        
        return (tool_name, tool_args) if tool_args else (tool_name, {})

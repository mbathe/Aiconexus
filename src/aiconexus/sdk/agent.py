"""
SDKAgent - The main high-level API for developers

This is THE API that developers use - everything else is hidden inside.
It provides a simple, powerful interface for creating agents.
"""

from typing import List, Dict, Any, Optional
import logging
import asyncio
from datetime import datetime

from .types import (
    ExpertiseArea,
    AgentResult,
    ReasoningStep,
    Tool,
    ConnectionInfo,
    InputSchema,
    OutputSchema,
    FieldSchema
)
from .orchestrator import SDKOrchestrator
from .tools import ToolCallingManager
from .executor import ReActExecutor

logger = logging.getLogger(__name__)


class SDKAgent:
    """
    Main API for creating intelligent agents
    
    Usage:
        agent = SDKAgent(
            name="planner",
            expertise=[ExpertiseArea("planning", 0.95)],
            llm_model="gpt-4"
        )
        result = await agent.execute("Your task here")
    """
    
    def __init__(
        self,
        name: str,
        expertise: List[ExpertiseArea],
        llm: Optional[Any] = None,
        llm_model: str = "gpt-4",
        temperature: float = 0.7,
        gateway_url: str = "http://localhost:8000",
        system_prompt: Optional[str] = None,
        custom_tools: Optional[List[Tool]] = None,
        max_iterations: int = 10,
        input_schema: Optional[InputSchema] = None,
        output_schema: Optional[OutputSchema] = None,
        delegation_rules: Optional[Dict[str, str]] = None,
        auto_delegation: bool = True,
        force_synthetic_tools: bool = False,
        verbose: bool = True
    ):
        """
        Create a new SDK Agent
        
        Args:
            name: Agent name
            expertise: List of expertise areas
            llm: LLM instance (if None, creates one)
            llm_model: Model name (ignored if llm provided)
            temperature: LLM temperature
            gateway_url: Gateway URL for agent discovery
            system_prompt: Custom system prompt
            custom_tools: Additional tools for the agent
            max_iterations: Max ReAct iterations
            input_schema: Custom input schema
            output_schema: Custom output schema
            delegation_rules: Rules for forcing delegation (pattern -> agent_id)
            auto_delegation: Whether to auto-delegate to other agents
            force_synthetic_tools: Force synthetic tool calling (for testing)
            verbose: Enable verbose logging
        """
        
        self.name = name
        self.expertise = expertise
        self.llm_model = llm_model
        self.temperature = temperature
        self.gateway_url = gateway_url
        self.max_iterations = max_iterations
        self.delegation_rules = delegation_rules or {}
        self.auto_delegation = auto_delegation
        self.force_synthetic_tools = force_synthetic_tools
        self.verbose = verbose
        
        logger.info(f"Initializing SDKAgent: {name}")
        logger.info(f"  Expertise: {[e.domain for e in expertise]}")
        logger.info(f"  LLM Model: {llm_model}")
        
        # ===== LAYER 1: LLM Setup =====
        self.llm = llm or self._create_llm(llm_model, temperature)
        
        # ===== LAYER 2: SDK Orchestrator =====
        self.sdk = SDKOrchestrator(
            gateway_url=gateway_url,
            agent_id=name
        )
        
        # ===== LAYER 3: Schemas =====
        self.input_schema = input_schema or self._default_input_schema()
        self.output_schema = output_schema or self._default_output_schema()
        
        # ===== LAYER 4: Tools =====
        self.custom_tools = custom_tools or []
        self.tools = self._build_tools()
        
        # ===== LAYER 5: System Prompt =====
        self.system_prompt = system_prompt or self._generate_system_prompt()
        
        # ===== LAYER 6: ReAct Executor =====
        self.executor: Optional[ReActExecutor] = None
        
        logger.info(f"✅ SDKAgent '{name}' initialized successfully")
    
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """
        Execute a task with the agent
        
        This is the main entry point. Everything happens inside.
        
        Args:
            task: The task description
            context: Optional context information
        
        Returns:
            AgentResult with answer, reasoning steps, tool calls, etc
        """
        
        logger.info(f"\n{'='*70}")
        logger.info(f"🚀 Executing task with agent '{self.name}'")
        logger.info(f"{'='*70}")
        logger.info(f"Task: {task}")
        if context:
            logger.info(f"Context: {context}")
        
        try:
            # Create executor if not exists
            if self.executor is None:
                self.executor = await self.sdk.create_react_executor(
                    llm=self.llm,
                    system_prompt=self.system_prompt,
                    tools=self.tools,
                    max_iterations=self.max_iterations
                )
            
            # Run ReAct loop
            start_time = datetime.utcnow()
            
            result = await self.executor.run(
                task=task,
                context=context or {},
                source_agent_id=self.name
            )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Convert to AgentResult
            agent_result = AgentResult(
                answer=result.get("answer", ""),
                reasoning_steps=result.get("reasoning_steps", []),
                tool_calls=result.get("tool_calls", []),
                interactions=result.get("interactions", []),
                success=result.get("success", False),
                error=result.get("error"),
                execution_time_ms=execution_time
            )
            
            logger.info(f"\n✅ Task completed successfully")
            logger.info(f"⏱️  Total time: {execution_time:.0f}ms")
            logger.info(f"{'='*70}\n")
            
            return agent_result
        
        except Exception as e:
            logger.error(f"❌ Error executing task: {str(e)}")
            
            return AgentResult(
                answer=None,
                success=False,
                error=str(e),
                execution_time_ms=0
            )
    
    # ========== PRIVATE METHODS ==========
    
    def _create_llm(self, model_name: str, temperature: float) -> Any:
        """Create an LLM instance"""
        try:
            from langchain_openai import ChatOpenAI
            
            logger.info(f"Creating ChatOpenAI LLM: {model_name}")
            return ChatOpenAI(
                model_name=model_name,
                temperature=temperature
            )
        except ImportError:
            logger.warning("langchain_openai not installed, using mock LLM")
            return self._create_mock_llm()
    
    def _create_mock_llm(self) -> Any:
        """Create a mock LLM for testing"""
        class MockLLM:
            async def agenerate_prompt(self, messages):
                class Response:
                    class Generation:
                        text = "This is a mock response"
                    generations = [[Generation()]]
                return Response()
        
        return MockLLM()
    
    def _build_tools(self) -> List[Tool]:
        """Build the list of tools for the agent"""
        
        tools = []
        
        # Add SDK tools for inter-agent communication
        if self.auto_delegation:
            tools.extend([
                Tool(
                    name="find_experts",
                    description="Find expert agents with specific expertise",
                    func=self.sdk.find_experts,
                    async_func=True
                ),
                Tool(
                    name="validate_message",
                    description="Validate a message before sending to another agent",
                    func=self.sdk.validate_message,
                    async_func=True
                ),
                Tool(
                    name="send_message",
                    description="Send a message to another agent",
                    func=self.sdk.send_message,
                    async_func=True
                ),
                Tool(
                    name="send_messages_parallel",
                    description="Send messages to multiple agents in parallel",
                    func=self.sdk.send_messages_parallel,
                    async_func=True
                ),
            ])
        
        # Add custom tools
        if self.custom_tools:
            tools.extend(self.custom_tools)
        
        return tools
    
    def _default_input_schema(self) -> InputSchema:
        """Default input schema"""
        return InputSchema(
            fields={
                "task": FieldSchema(
                    name="task",
                    type="string",
                    required=True,
                    description="The task to execute"
                ),
                "context": FieldSchema(
                    name="context",
                    type="object",
                    required=False,
                    description="Optional context information"
                )
            },
            required_fields=["task"],
            strict_mode=False
        )
    
    def _default_output_schema(self) -> OutputSchema:
        """Default output schema"""
        return OutputSchema(
            fields={
                "answer": FieldSchema(
                    name="answer",
                    type="string",
                    required=True,
                    description="The answer to the task"
                ),
                "confidence": FieldSchema(
                    name="confidence",
                    type="number",
                    required=False,
                    description="Confidence in the answer (0-1)"
                )
            },
            required_fields=["answer"]
        )
    
    def _generate_system_prompt(self) -> str:
        """Generate system prompt"""
        expertise_str = "\n".join([
            f"  - {e.domain} (confidence: {e.confidence:.1%})"
            for e in self.expertise
        ])
        
        delegation_info = ""
        if self.auto_delegation:
            delegation_info = """
You have tools to collaborate with other agents:
- find_experts: Search for agents with specific expertise
- validate_message: Verify message format
- send_message: Contact one agent
- send_messages_parallel: Contact multiple agents simultaneously

When you need expertise outside your domain:
1. Use find_experts() to find relevant specialists
2. Formulate a clear request
3. Use send_message() or send_messages_parallel() to contact them
4. Integrate their responses into your solution
"""
        
        return f"""You are an expert agent named '{self.name}'.

Your Areas of Expertise:
{expertise_str}

You are autonomous and should leverage your skills to solve problems.
Be honest about limitations and delegate to specialists when needed.{delegation_info}

Approach:
1. Analyze the task carefully
2. Identify required subtasks
3. Use available tools (including agent collaboration)
4. Synthesize a comprehensive solution
5. Provide clear reasoning
"""
    
    # ========== PUBLIC UTILITY METHODS ==========
    
    def get_expertise_summary(self) -> Dict[str, Any]:
        """Get a summary of the agent's expertise"""
        return {
            "agent_name": self.name,
            "expertise": [e.to_dict() for e in self.expertise],
            "tools_count": len(self.tools),
            "auto_delegation": self.auto_delegation,
            "delegation_rules": self.delegation_rules
        }
    
    def get_tools_summary(self) -> List[Dict[str, str]]:
        """Get summary of available tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in self.tools
        ]

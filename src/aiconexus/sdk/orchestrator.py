"""
SDK Orchestrator
Coordinates all SDK components
"""

from typing import List, Dict, Any, Optional
import logging

from .registry import AgentRegistry
from .validator import MessageValidator
from .connector import AgentConnector
from .tools import ToolCallingManager
from .executor import ReActExecutor
from .types import ExpertiseArea, Tool, AgentSchema, InputSchema, OutputSchema, FieldSchema

logger = logging.getLogger(__name__)


class SDKOrchestrator:
    """
    Main orchestrator for the SDK
    Combines all components and provides a unified interface
    """
    
    def __init__(
        self,
        gateway_url: str = "http://localhost:8000",
        agent_id: str = "default-agent",
        enable_semantic_matching: bool = True
    ):
        self.gateway_url = gateway_url
        self.agent_id = agent_id
        
        # Initialize components
        self.registry = AgentRegistry(
            enable_semantic_matching=enable_semantic_matching
        )
        self.validator = MessageValidator()
        self.connector = AgentConnector(self.registry)
        
        logger.info(f"SDKOrchestrator initialized for agent: {agent_id}")
    
    async def create_react_executor(
        self,
        llm: Any,
        system_prompt: str,
        tools: List[Tool],
        max_iterations: int = 10
    ) -> ReActExecutor:
        """
        Create a ReAct executor for an agent
        """
        
        # Create tool manager
        tool_manager = ToolCallingManager(
            llm=llm,
            model_name=str(llm)
        )
        
        # Register tools
        tool_manager.register_tools(tools)
        
        # Create executor
        executor = ReActExecutor(
            llm=llm,
            tool_manager=tool_manager,
            connector=self.connector,
            validator=self.validator,
            system_prompt=system_prompt,
            max_iterations=max_iterations
        )
        
        return executor
    
    # ========== SDK TOOLS FOR AGENTS ==========
    
    async def find_experts(
        self,
        expertise: List[str],
        min_confidence: float = 0.7,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Tool: Find agents with specific expertise
        """
        agents = await self.registry.find_agents_by_expertise(
            expertise=expertise,
            min_confidence=min_confidence,
            limit=limit
        )
        
        return [agent.to_dict() for agent in agents]
    
    async def validate_message(
        self,
        message: Dict[str, Any],
        agent_id: str
    ) -> Dict[str, Any]:
        """
        Tool: Validate a message before sending
        """
        schema = await self.registry.get_agent_schema(agent_id)
        
        if not schema:
            return {
                "valid": False,
                "errors": [f"No schema found for agent: {agent_id}"]
            }
        
        validation = await self.validator.validate_request(
            message,
            agent_id,
            schema
        )
        
        return {
            "valid": validation.valid,
            "errors": validation.errors,
            "warnings": validation.warnings
        }
    
    async def send_message(
        self,
        message: Dict[str, Any],
        to_agent_id: str,
        timeout_ms: int = 30000,
        auto_validate: bool = True
    ) -> Dict[str, Any]:
        """
        Tool: Send a message to an agent
        """
        
        # Auto-validate if requested
        if auto_validate:
            validation = await self.validate_message(message, to_agent_id)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": f"Message validation failed: {validation['errors']}",
                    "agent_id": to_agent_id
                }
        
        # Send message
        response = await self.connector.send_message(
            to_agent_id=to_agent_id,
            message=message,
            source_agent_id=self.agent_id,
            timeout_ms=timeout_ms
        )
        
        return {
            "success": response.status == "success",
            "response": response.response,
            "agent_id": response.agent_id,
            "status": response.status,
            "error": response.error,
            "execution_time_ms": response.execution_time_ms
        }
    
    async def send_messages_parallel(
        self,
        messages: List[Dict[str, Any]],
        agent_ids: List[str],
        timeout_ms: int = 30000,
        auto_validate: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Tool: Send messages to multiple agents in parallel
        """
        
        if len(messages) != len(agent_ids):
            return [{
                "success": False,
                "error": "messages and agent_ids must have same length"
            }]
        
        # Auto-validate all messages
        if auto_validate:
            for message, agent_id in zip(messages, agent_ids):
                validation = await self.validate_message(message, agent_id)
                if not validation["valid"]:
                    return [{
                        "success": False,
                        "error": f"Message validation failed for {agent_id}: {validation['errors']}",
                        "agent_id": agent_id
                    }]
        
        # Send all messages
        responses = await self.connector.send_messages_parallel(
            messages=messages,
            agent_ids=agent_ids,
            source_agent_id=self.agent_id,
            timeout_ms=timeout_ms
        )
        
        return [
            {
                "success": r.status == "success",
                "response": r.response,
                "agent_id": r.agent_id,
                "status": r.status,
                "error": r.error,
                "execution_time_ms": r.execution_time_ms
            }
            for r in responses
        ]
    
    # ========== AGENT REGISTRATION ==========
    
    async def register_agent(
        self,
        agent_id: str,
        name: str,
        expertise: List[ExpertiseArea],
        connection_info: Any,  # ConnectionInfo
        input_schema: Optional[InputSchema] = None,
        output_schema: Optional[OutputSchema] = None
    ) -> None:
        """
        Register an agent with the registry
        """
        
        # Create schema if not provided
        if input_schema is None:
            input_schema = InputSchema(
                fields={
                    "task": FieldSchema("task", "string", required=True),
                    "context": FieldSchema("context", "object", required=False)
                },
                required_fields=["task"]
            )
        
        if output_schema is None:
            output_schema = OutputSchema(
                fields={
                    "answer": FieldSchema("answer", "string", required=True),
                    "confidence": FieldSchema("confidence", "number", required=False)
                },
                required_fields=["answer"]
            )
        
        # Create schema object
        schema = AgentSchema(
            agent_id=agent_id,
            input_schema=input_schema,
            output_schema=output_schema
        )
        
        # Register
        await self.registry.register_agent(
            agent_id=agent_id,
            name=name,
            expertise=expertise,
            connection_info=connection_info,
            schema=schema
        )
        
        logger.info(f"Registered agent: {agent_id}")

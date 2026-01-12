"""
ReAct Executor
Implements the Reasoning + Acting loop for agents
Works with all LLM models through the tool manager
"""

from typing import List, Dict, Any, Optional
import asyncio
import logging
from datetime import datetime

from .types import ReasoningStep, ToolCall, Message, Tool
from .tools import ToolCallingManager
from .validator import MessageValidator
from .connector import AgentConnector

logger = logging.getLogger(__name__)


class ReActExecutor:
    """
    Executes the Reasoning + Acting loop
    - Handles the conversation with LLM
    - Parses and executes tool calls
    - Manages the iteration loop
    """
    
    def __init__(
        self,
        llm: Any,
        tool_manager: ToolCallingManager,
        connector: AgentConnector,
        validator: MessageValidator,
        system_prompt: str,
        max_iterations: int = 10,
        verbose: bool = True
    ):
        self.llm = llm
        self.tool_manager = tool_manager
        self.connector = connector
        self.validator = validator
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
        self.verbose = verbose
    
    async def run(
        self,
        task: str,
        context: Dict[str, Any],
        source_agent_id: str
    ) -> Dict[str, Any]:
        """
        Run the ReAct loop
        
        Returns:
            {
                "answer": "final answer",
                "reasoning_steps": [...],
                "tool_calls": [...],
                "success": True/False,
                "error": optional error message
            }
        """
        
        start_time = datetime.utcnow()
        reasoning_steps: List[ReasoningStep] = []
        tool_calls: List[ToolCall] = []
        interactions: List[Dict[str, Any]] = []
        
        # Initialize conversation
        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            },
            {
                "role": "user",
                "content": self._format_task(task, context)
            }
        ]
        
        try:
            for iteration in range(self.max_iterations):
                # ====== STEP 1: REASONING ======
                # Ask LLM to think
                
                self._log(f"\n{'='*60}")
                self._log(f"Iteration {iteration + 1}/{self.max_iterations}")
                self._log(f"{'='*60}")
                
                response = await self._call_llm(messages)
                
                self._log(f"LLM Response:\n{response}")
                
                reasoning_steps.append(
                    ReasoningStep(
                        iteration=iteration,
                        thought=response
                    )
                )
                
                # ====== STEP 2: PARSE ACTION ======
                # Check if there's a tool call in the response
                
                tool_call_info = self.tool_manager.parse_tool_call_from_response(response)
                
                if tool_call_info is None:
                    # No tool call → this is the final answer
                    self._log(f"\n✅ Final answer generated (no tool call)")
                    
                    elapsed_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                    
                    return {
                        "answer": response,
                        "reasoning_steps": reasoning_steps,
                        "tool_calls": tool_calls,
                        "interactions": interactions,
                        "success": True,
                        "error": None,
                        "execution_time_ms": elapsed_ms
                    }
                
                tool_name, tool_args = tool_call_info
                
                self._log(f"\n🔧 Tool call detected: {tool_name}")
                self._log(f"   Args: {tool_args}")
                
                # ====== STEP 3: EXECUTE TOOL ======
                
                tool_start = datetime.utcnow()
                
                # Special handling for inter-agent communication tools
                if tool_name in ["send_message", "send_messages_parallel"]:
                    tool_result = await self._execute_communication_tool(
                        tool_name,
                        tool_args,
                        source_agent_id,
                        interactions
                    )
                else:
                    # Regular tool execution
                    tool_result = await self.tool_manager.call_tool(tool_name, tool_args)
                
                tool_elapsed = (datetime.utcnow() - tool_start).total_seconds() * 1000
                
                self._log(f"   Result: {tool_result}")
                
                tool_calls.append(
                    ToolCall(
                        iteration=iteration,
                        tool_name=tool_name,
                        tool_args=tool_args,
                        result=tool_result,
                        execution_time_ms=tool_elapsed
                    )
                )
                
                # ====== STEP 4: UPDATE CONVERSATION ======
                # Add action and result to messages
                
                messages.append({
                    "role": "assistant",
                    "content": response  # The full response with tool call
                })
                
                messages.append({
                    "role": "user",
                    "content": f"Tool '{tool_name}' result:\n{tool_result}"
                })
                
                self._log(f"\n⏳ Iteration {iteration + 1} complete, continuing...\n")
            
            # Max iterations reached
            self._log(f"\n⚠️  Max iterations ({self.max_iterations}) reached")
            
            elapsed_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return {
                "answer": "Max iterations reached",
                "reasoning_steps": reasoning_steps,
                "tool_calls": tool_calls,
                "interactions": interactions,
                "success": False,
                "error": "Max iterations exceeded",
                "execution_time_ms": elapsed_ms
            }
        
        except Exception as e:
            self._log(f"\n❌ Error in ReAct loop: {str(e)}")
            
            elapsed_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return {
                "answer": None,
                "reasoning_steps": reasoning_steps,
                "tool_calls": tool_calls,
                "interactions": interactions,
                "success": False,
                "error": str(e),
                "execution_time_ms": elapsed_ms
            }
    
    async def _execute_communication_tool(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        source_agent_id: str,
        interactions: List[Dict[str, Any]]
    ) -> str:
        """
        Execute inter-agent communication tools
        """
        
        if tool_name == "send_message":
            # Single message to one agent
            agent_id = tool_args.get("to_agent_id") or tool_args.get("agent_id")
            message = tool_args.get("message", {})
            
            self._log(f"   → Contacting agent: {agent_id}")
            
            response = await self.connector.send_message(
                to_agent_id=agent_id,
                message=message,
                source_agent_id=source_agent_id,
                timeout_ms=tool_args.get("timeout_ms", 30000)
            )
            
            interactions.append({
                "type": "single_message",
                "to_agent": agent_id,
                "request_id": response.request_id,
                "status": response.status,
                "execution_time_ms": response.execution_time_ms
            })
            
            if response.status == "success":
                return self._format_agent_response(response.response)
            else:
                return f"Error contacting {agent_id}: {response.error}"
        
        elif tool_name == "send_messages_parallel":
            # Multiple messages to multiple agents
            agent_ids = tool_args.get("agent_ids", [])
            messages = tool_args.get("messages", [])
            
            self._log(f"   → Contacting {len(agent_ids)} agents in parallel")
            
            responses = await self.connector.send_messages_parallel(
                messages=messages,
                agent_ids=agent_ids,
                source_agent_id=source_agent_id,
                timeout_ms=tool_args.get("timeout_ms", 30000)
            )
            
            # Record interactions
            for response in responses:
                interactions.append({
                    "type": "parallel_message",
                    "to_agent": response.agent_id,
                    "request_id": response.request_id,
                    "status": response.status,
                    "execution_time_ms": response.execution_time_ms
                })
            
            # Format results
            results = []
            for response in responses:
                if response.status == "success":
                    results.append(f"From {response.agent_id}: {self._format_agent_response(response.response)}")
                else:
                    results.append(f"Error from {response.agent_id}: {response.error}")
            
            return "\n".join(results)
        
        else:
            return f"Unknown communication tool: {tool_name}"
    
    async def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        """Call the LLM"""
        try:
            # Different based on LLM provider
            if hasattr(self.llm, 'agenerate'):
                # LangChain async
                from langchain.schema import HumanMessage, SystemMessage
                
                lc_messages = []
                for msg in messages:
                    if msg["role"] == "system":
                        lc_messages.append(SystemMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        lc_messages.append({"role": "assistant", "content": msg["content"]})
                    else:
                        lc_messages.append({"role": "user", "content": msg["content"]})
                
                response = await self.llm.agenerate_prompt([lc_messages])
                return response.generations[0][0].text
            
            elif hasattr(self.llm, 'ainvoke'):
                # LangChain LCEL
                response = await self.llm.ainvoke({"messages": messages})
                if hasattr(response, 'content'):
                    return response.content
                return str(response)
            
            else:
                # Generic async call
                response = await self.llm.acall(messages)
                return response
        
        except Exception as e:
            logger.error(f"Error calling LLM: {str(e)}")
            raise
    
    def _format_task(self, task: str, context: Dict[str, Any]) -> str:
        """Format the task for the LLM"""
        context_str = ""
        if context:
            context_str = "Context:\n" + "\n".join([
                f"- {k}: {v}"
                for k, v in context.items()
            ])
        
        return f"""Task: {task}

{context_str}

Please solve this task. If you need additional information or help from other agents, use the available tools to contact them."""
    
    def _format_agent_response(self, response: Dict[str, Any]) -> str:
        """Format agent response for LLM"""
        import json
        return json.dumps(response, indent=2)
    
    def _log(self, message: str):
        """Log message if verbose"""
        if self.verbose:
            logger.info(message)
            print(message)

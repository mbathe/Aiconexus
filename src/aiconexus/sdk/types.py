"""
Core types and schemas for the AIConexus SDK
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import json
from datetime import datetime
import uuid


class ExpertiseLevel(str, Enum):
    """Confidence level in a domain"""
    NOVICE = "novice"  # 0.0-0.3
    INTERMEDIATE = "intermediate"  # 0.3-0.7
    EXPERT = "expert"  # 0.7-0.95
    MASTER = "master"  # 0.95-1.0


@dataclass
class ExpertiseArea:
    """
    Defines an area of expertise for an agent
    """
    domain: str
    confidence: float = 0.8
    description: Optional[str] = None
    sub_domains: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
        
        if not self.description:
            self.description = f"Expert in {self.domain}"
    
    @property
    def level(self) -> ExpertiseLevel:
        """Get the expertise level"""
        if self.confidence >= 0.95:
            return ExpertiseLevel.MASTER
        elif self.confidence >= 0.7:
            return ExpertiseLevel.EXPERT
        elif self.confidence >= 0.3:
            return ExpertiseLevel.INTERMEDIATE
        else:
            return ExpertiseLevel.NOVICE
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "confidence": self.confidence,
            "description": self.description,
            "sub_domains": self.sub_domains,
            "level": self.level.value
        }


@dataclass
class FieldSchema:
    """Schema for a single field"""
    name: str
    type: str  # "string", "number", "boolean", "object", "array"
    required: bool = True
    description: Optional[str] = None
    enum: Optional[List[Any]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    pattern: Optional[str] = None  # Regex pattern


@dataclass
class InputSchema:
    """Schema for agent input"""
    fields: Dict[str, FieldSchema]
    required_fields: List[str] = field(default_factory=list)
    strict_mode: bool = True  # No unknown fields allowed
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "fields": {k: v.__dict__ for k, v in self.fields.items()},
            "required_fields": self.required_fields,
            "strict_mode": self.strict_mode
        }


@dataclass
class OutputSchema:
    """Schema for agent output"""
    fields: Dict[str, FieldSchema]
    required_fields: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "fields": {k: v.__dict__ for k, v in self.fields.items()},
            "required_fields": self.required_fields
        }


@dataclass
class AgentSchema:
    """Complete schema for an agent's input/output"""
    agent_id: str
    input_schema: InputSchema
    output_schema: OutputSchema
    version: str = "1.0"


@dataclass
class ConnectionInfo:
    """Connection information for an agent"""
    protocol: str  # "http", "grpc", "websocket"
    host: str
    port: int
    auth_token: Optional[str] = None
    
    @property
    def url(self) -> str:
        return f"{self.protocol}://{self.host}:{self.port}"


@dataclass
class AgentInfo:
    """Information about an available agent"""
    agent_id: str
    name: str
    expertise: List[ExpertiseArea]
    connection_info: ConnectionInfo
    schema: Optional[AgentSchema] = None
    match_score: float = 0.0
    availability: str = "online"  # "online", "offline", "busy"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "expertise": [e.to_dict() for e in self.expertise],
            "connection_info": self.connection_info.__dict__,
            "match_score": self.match_score,
            "availability": self.availability,
            "metadata": self.metadata
        }


@dataclass
class Message:
    """Message between agents"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_agent: str = ""
    target_agent: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    timeout_ms: int = 30000
    
    def to_json(self) -> str:
        return json.dumps({
            "request_id": self.request_id,
            "source_agent": self.source_agent,
            "target_agent": self.target_agent,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "timeout_ms": self.timeout_ms
        })
    
    @staticmethod
    def from_json(json_str: str) -> "Message":
        data = json.loads(json_str)
        return Message(
            request_id=data["request_id"],
            source_agent=data["source_agent"],
            target_agent=data["target_agent"],
            payload=data["payload"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            timeout_ms=data.get("timeout_ms", 30000)
        )


@dataclass
class ValidationResult:
    """Result of message validation"""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validated_payload: Optional[Dict[str, Any]] = None


@dataclass
class MessageResponse:
    """Response to a message"""
    agent_id: str
    request_id: str
    response: Optional[Dict[str, Any]] = None
    status: str = "success"  # "success", "error", "timeout"
    error: Optional[str] = None
    execution_time_ms: float = 0.0


@dataclass
class ToolCall:
    """A tool call made by the agent"""
    iteration: int
    tool_name: str
    tool_args: Dict[str, Any]
    result: str
    execution_time_ms: float = 0.0


@dataclass
class ReasoningStep:
    """A step in the reasoning process"""
    iteration: int
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None


@dataclass
class AgentResult:
    """Final result from an agent execution"""
    answer: str
    reasoning_steps: List[ReasoningStep] = field(default_factory=list)
    tool_calls: List[ToolCall] = field(default_factory=list)
    interactions: List[Dict[str, Any]] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "answer": self.answer,
            "reasoning_steps": [
                {
                    "iteration": step.iteration,
                    "thought": step.thought,
                    "action": step.action,
                    "action_input": step.action_input
                }
                for step in self.reasoning_steps
            ],
            "tool_calls": [
                {
                    "iteration": call.iteration,
                    "tool_name": call.tool_name,
                    "tool_args": call.tool_args,
                    "result": call.result,
                    "execution_time_ms": call.execution_time_ms
                }
                for call in self.tool_calls
            ],
            "interactions": self.interactions,
            "success": self.success,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms
        }


@dataclass
class Tool:
    """Tool available to agents"""
    name: str
    description: str
    func: Callable
    input_schema: Optional[InputSchema] = None
    async_func: bool = False

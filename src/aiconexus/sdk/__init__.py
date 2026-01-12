"""
AIConexus SDK - Next-generation framework for autonomous agent collaboration

The SDK provides:
- Unified agent API (SDKAgent)
- Intelligent agent discovery and matching
- P2P inter-agent communication
- Automatic tool calling for all LLM models
- ReAct loop orchestration
- Contract validation and error handling
"""

from .agent import SDKAgent
from .types import (
    ExpertiseArea,
    AgentInfo,
    AgentSchema,
    Message,
    AgentResult,
)
from .registry import AgentRegistry
from .validator import MessageValidator
from .connector import AgentConnector
from .tools import ToolCallingManager, SyntheticToolCallingExecutor, NativeToolCallingExecutor
from .executor import ReActExecutor
from .orchestrator import SDKOrchestrator

__version__ = "0.1.0"

__all__ = [
    "SDKAgent",
    "ExpertiseArea",
    "AgentInfo",
    "AgentSchema",
    "Message",
    "AgentResult",
    "AgentRegistry",
    "MessageValidator",
    "AgentConnector",
    "ToolCallingManager",
    "SyntheticToolCallingExecutor",
    "NativeToolCallingExecutor",
    "ReActExecutor",
    "SDKOrchestrator",
]

"""Exception classes for AIConexus"""


class AIConexusError(Exception):
    """Base exception for all AIConexus errors"""

    pass


class AgentError(AIConexusError):
    """Agent-related errors"""

    pass


class ProtocolError(AIConexusError):
    """Protocol communication errors"""

    pass


class RegistryError(AIConexusError):
    """Registry/discovery errors"""

    pass


class NegotiationError(AIConexusError):
    """Negotiation and contract errors"""

    pass


class ExecutionError(AIConexusError):
    """Execution and task errors"""

    pass


class SecurityError(AIConexusError):
    """Security and authentication errors"""

    pass


class BudgetError(AIConexusError):
    """Budget and economic errors"""

    pass


class TimeoutError(AIConexusError):
    """Operation timeout errors"""

    pass


class ValidationError(AIConexusError):
    """Input validation errors"""

    pass

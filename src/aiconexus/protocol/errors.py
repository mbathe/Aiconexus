"""
Protocol-specific exceptions.
"""


class ProtocolError(Exception):
    """Base exception for protocol-related errors."""
    pass


class SignatureError(ProtocolError):
    """Raised when message signature verification fails."""
    pass


class InvalidMessageError(ProtocolError):
    """Raised when message structure is invalid."""
    pass


class AgentNotFoundError(ProtocolError):
    """Raised when target agent is not found in registry."""
    pass


class ConnectionError(ProtocolError):
    """Raised when connection establishment fails."""
    pass


class TimeoutError(ProtocolError):
    """Raised when operation exceeds timeout."""
    pass


class VersionMismatchError(ProtocolError):
    """Raised when protocol version is not supported."""
    pass

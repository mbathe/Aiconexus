"""Protocol module - WebRTC-based communication protocol implementation"""

from .models import (
    Message,
    MessageType,
    ErrorCode,
    IntentPayload,
    ExecRequestPayload,
    ExecResponsePayload,
)
from .security import DIDKey, MessageSigner, SecurityError
from .serialization import MessageSerializer, CanonicalJSON, SerializationError
from .errors import (
    ProtocolError,
    SignatureError,
    InvalidMessageError,
    AgentNotFoundError,
    ConnectionError,
    TimeoutError,
    VersionMismatchError,
)

__all__ = [
    "Message",
    "MessageType",
    "ErrorCode",
    "IntentPayload",
    "ExecRequestPayload",
    "ExecResponsePayload",
    "DIDKey",
    "MessageSigner",
    "SecurityError",
    "MessageSerializer",
    "CanonicalJSON",
    "SerializationError",
    "ProtocolError",
    "SignatureError",
    "InvalidMessageError",
    "AgentNotFoundError",
    "ConnectionError",
    "TimeoutError",
    "VersionMismatchError",
]


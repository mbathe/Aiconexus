"""
Pydantic models for IoAP Protocol messages.

Defines the structure of all message types exchanged between agents
and the gateway over WebSocket (signaling) and DataChannel (P2P).
"""

from enum import Enum
from typing import Optional, Any, Dict, Union
from datetime import datetime
from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Message types in the IoAP protocol."""
    REGISTER = "REGISTER"
    UNREGISTER = "UNREGISTER"
    OFFER = "OFFER"
    ANSWER = "ANSWER"
    ICE_CANDIDATE = "ICE_CANDIDATE"
    INTENT = "INTENT"
    EXEC_REQUEST = "EXEC_REQUEST"
    EXEC_RESPONSE = "EXEC_RESPONSE"
    ERROR = "ERROR"
    PING = "PING"
    PONG = "PONG"


class ErrorCode(str, Enum):
    """Error codes for ERROR message type."""
    INVALID_SIGNATURE = "INVALID_SIGNATURE"
    UNKNOWN_AGENT = "UNKNOWN_AGENT"
    CONNECTION_REFUSED = "CONNECTION_REFUSED"
    TIMEOUT = "TIMEOUT"
    MALFORMED_MESSAGE = "MALFORMED_MESSAGE"
    UNSUPPORTED_VERSION = "UNSUPPORTED_VERSION"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class BasePayload(BaseModel):
    """Base class for all message payloads."""
    class Config:
        extra = "forbid"


class RegisterPayload(BasePayload):
    """Payload for REGISTER message."""
    public_key: str = Field(..., description="Base58-encoded Ed25519 public key")


class UnregisterPayload(BasePayload):
    """Payload for UNREGISTER message."""
    reason: Optional[str] = Field(None, description="Reason for disconnection")


class OfferPayload(BasePayload):
    """Payload for OFFER message (WebRTC SDP)."""
    sdp: str = Field(..., description="WebRTC Session Description Protocol offer")


class AnswerPayload(BasePayload):
    """Payload for ANSWER message (WebRTC SDP)."""
    sdp: str = Field(..., description="WebRTC Session Description Protocol answer")


class ICECandidatePayload(BasePayload):
    """Payload for ICE_CANDIDATE message."""
    candidate: str = Field(..., description="ICE candidate string")
    sdp_mid: Optional[str] = Field(None, description="Media stream ID")
    sdp_mline_index: Optional[int] = Field(None, description="Media line index")


class IntentPayload(BasePayload):
    """Payload for INTENT message (flexible - natural language or structured)."""
    # Natural language mode
    query: Optional[str] = Field(None, description="Natural language query")
    context: Optional[str] = Field(None, description="Additional context for query")
    
    # Structured mode
    task: Optional[str] = Field(None, description="Task name (machine-friendly)")
    params: Optional[Dict[str, Any]] = Field(None, description="Task parameters")
    
    # Response fields
    status: Optional[str] = Field(None, description="Status (e.g., 'understood', 'executing')")
    required_input: Optional[str] = Field(None, description="Input required from client")
    cost: Optional[str] = Field(None, description="Cost estimation (e.g., '0.50 EUR')")


class ExecRequestPayload(BasePayload):
    """Payload for EXEC_REQUEST message."""
    args: Dict[str, Any] = Field(default_factory=dict, description="Execution arguments")
    timeout_ms: Optional[int] = Field(None, description="Execution timeout in milliseconds")
    stream: Optional[bool] = Field(False, description="Enable streaming response")


class ExecResponsePayload(BasePayload):
    """Payload for EXEC_RESPONSE message."""
    result: Optional[Any] = Field(None, description="Execution result (any type)")
    error: Optional[str] = Field(None, description="Error message if execution failed")
    status: str = Field("success", description="Status: 'success' or 'error'")
    execution_time_ms: Optional[float] = Field(None, description="Time taken in milliseconds")
    stream_url: Optional[str] = Field(None, description="URL for streaming large responses")


class ErrorPayload(BasePayload):
    """Payload for ERROR message."""
    code: ErrorCode = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")


class PingPayload(BasePayload):
    """Payload for PING message."""
    sequence: Optional[int] = Field(None, description="Sequence number for tracking")


class PongPayload(BasePayload):
    """Payload for PONG message."""
    sequence: Optional[int] = Field(None, description="Echo of PING sequence number")


class Message(BaseModel):
    """
    Standard message format for IoAP Protocol.
    
    Used on both WebSocket (signaling) and DataChannel (P2P).
    """
    id: str = Field(..., description="UUID v4 unique message ID")
    correlation_id: Optional[str] = Field(None, description="ID of message being replied to")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="ISO 8601 UTC")
    from_did: str = Field(..., alias="from", description="Sender DID (did:key format)")
    to_did: str = Field(..., alias="to", description="Recipient DID (did:key format)")
    type: MessageType = Field(..., description="Message type")
    payload: Union[
        RegisterPayload,
        UnregisterPayload,
        OfferPayload,
        AnswerPayload,
        ICECandidatePayload,
        IntentPayload,
        ExecRequestPayload,
        ExecResponsePayload,
        ErrorPayload,
        PingPayload,
        PongPayload,
    ] = Field(..., description="Message payload (type-specific)")
    version: str = Field("1.0", description="Protocol version")
    signature: str = Field(..., description="Base64-encoded Ed25519 signature")

    class Config:
        populate_by_name = True
        use_enum_values = False
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "correlation_id": None,
                "timestamp": "2026-01-12T10:00:00Z",
                "from": "did:key:z6MkClient",
                "to": "did:key:z6MkExpert",
                "type": "INTENT",
                "payload": {
                    "query": "Extract non-compete clauses from this PDF"
                },
                "version": "1.0",
                "signature": "base64_encoded_signature"
            }
        }

    @property
    def dict_for_signature(self) -> Dict[str, Any]:
        """
        Return message as dict without signature field.
        Used for signature computation and verification.
        """
        data = self.model_dump(by_alias=True, exclude_none=False)
        data.pop("signature", None)
        return data

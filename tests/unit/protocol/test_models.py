"""
Unit tests for protocol models.
"""

import pytest
from datetime import datetime
from aiconexus.protocol.models import (
    Message,
    MessageType,
    ErrorCode,
    RegisterPayload,
    IntentPayload,
    ExecRequestPayload,
    ExecResponsePayload,
    ErrorPayload,
)


class TestMessageType:
    """Test MessageType enum."""
    
    def test_message_types_defined(self):
        """Verify all required message types exist."""
        assert MessageType.REGISTER.value == "REGISTER"
        assert MessageType.OFFER.value == "OFFER"
        assert MessageType.INTENT.value == "INTENT"
        assert MessageType.EXEC_REQUEST.value == "EXEC_REQUEST"
        assert MessageType.EXEC_RESPONSE.value == "EXEC_RESPONSE"
        assert MessageType.ERROR.value == "ERROR"


class TestPayloads:
    """Test payload models."""
    
    def test_register_payload(self):
        """Test REGISTER payload validation."""
        payload = RegisterPayload(public_key="z6MkKey123")
        assert payload.public_key == "z6MkKey123"
    
    def test_intent_payload_natural_language(self):
        """Test INTENT with natural language."""
        payload = IntentPayload(
            query="Extract clauses from PDF",
            context="Legal document"
        )
        assert payload.query == "Extract clauses from PDF"
        assert payload.context == "Legal document"
    
    def test_intent_payload_structured(self):
        """Test INTENT with structured task."""
        payload = IntentPayload(
            task="extract_clauses",
            params={"file_id": "doc_123", "types": ["non_compete"]}
        )
        assert payload.task == "extract_clauses"
        assert payload.params["file_id"] == "doc_123"
    
    def test_exec_request_payload(self):
        """Test EXEC_REQUEST payload."""
        payload = ExecRequestPayload(
            args={"file": "test.pdf"},
            timeout_ms=5000,
            stream=True
        )
        assert payload.args["file"] == "test.pdf"
        assert payload.timeout_ms == 5000
        assert payload.stream is True
    
    def test_exec_response_payload_success(self):
        """Test successful EXEC_RESPONSE."""
        payload = ExecResponsePayload(
            result={"clauses": ["clause1", "clause2"]},
            status="success",
            execution_time_ms=1234.5
        )
        assert payload.status == "success"
        assert len(payload.result["clauses"]) == 2
        assert payload.execution_time_ms == 1234.5
    
    def test_exec_response_payload_error(self):
        """Test error EXEC_RESPONSE."""
        payload = ExecResponsePayload(
            error="File too large",
            status="error"
        )
        assert payload.status == "error"
        assert payload.error == "File too large"
        assert payload.result is None


class TestMessage:
    """Test Message model."""
    
    def test_message_creation(self):
        """Test creating a valid message."""
        msg = Message(
            id="msg_123",
            timestamp=datetime.utcnow(),
            from_did="did:key:z6MkA",
            to_did="did:key:z6MkB",
            type=MessageType.INTENT,
            payload=IntentPayload(query="test"),
            signature="sig_123"
        )
        assert msg.id == "msg_123"
        assert msg.from_did == "did:key:z6MkA"
        assert msg.to_did == "did:key:z6MkB"
        assert msg.type == MessageType.INTENT
    
    def test_message_with_correlation_id(self):
        """Test message with correlation_id for request/response linking."""
        msg = Message(
            id="msg_456",
            correlation_id="msg_123",
            timestamp=datetime.utcnow(),
            from_did="did:key:z6MkB",
            to_did="did:key:z6MkA",
            type=MessageType.EXEC_RESPONSE,
            payload=ExecResponsePayload(result={"ok": True}),
            signature="sig_456"
        )
        assert msg.correlation_id == "msg_123"
    
    def test_message_dict_for_signature(self):
        """Test dict_for_signature excludes signature field."""
        msg = Message(
            id="msg_789",
            timestamp=datetime.utcnow(),
            from_did="did:key:z6MkA",
            to_did="did:key:z6MkB",
            type=MessageType.PING,
            payload={},
            signature="sig_789"
        )
        sig_dict = msg.dict_for_signature
        assert "signature" not in sig_dict
        assert sig_dict["id"] == "msg_789"
    
    def test_message_version_default(self):
        """Test default protocol version."""
        msg = Message(
            id="msg_000",
            timestamp=datetime.utcnow(),
            from_did="did:key:z6MkA",
            to_did="did:key:z6MkB",
            type=MessageType.PONG,
            payload={},
            signature="sig_000"
        )
        assert msg.version == "1.0"
    
    def test_message_timestamp_default(self):
        """Test timestamp defaults to current UTC time."""
        before = datetime.utcnow()
        msg = Message(
            id="msg_zzz",
            from_did="did:key:z6MkA",
            to_did="did:key:z6MkB",
            type=MessageType.ERROR,
            payload=ErrorPayload(code=ErrorCode.TIMEOUT, message="Timed out"),
            signature="sig_zzz"
        )
        after = datetime.utcnow()
        assert before <= msg.timestamp <= after


class TestErrorCode:
    """Test ErrorCode enum."""
    
    def test_error_codes_defined(self):
        """Verify all error codes exist."""
        assert ErrorCode.INVALID_SIGNATURE.value == "INVALID_SIGNATURE"
        assert ErrorCode.UNKNOWN_AGENT.value == "UNKNOWN_AGENT"
        assert ErrorCode.TIMEOUT.value == "TIMEOUT"
        assert ErrorCode.INTERNAL_ERROR.value == "INTERNAL_ERROR"

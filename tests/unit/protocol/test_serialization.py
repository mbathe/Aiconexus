"""
Unit tests for protocol serialization.
"""

import json
import pytest
from datetime import datetime
from aiconexus.protocol.serialization import (
    MessageSerializer,
    CanonicalJSON,
    SerializationError,
)


class TestCanonicalJSON:
    """Test canonical JSON utilities."""
    
    def test_canonical_dumps(self):
        """Test canonical JSON serialization."""
        data = {"z": 3, "a": 1, "m": 2}
        result = CanonicalJSON.dumps(data)
        
        assert result == '{"a":1,"m":2,"z":3}'
        assert " " not in result
    
    def test_canonical_loads(self):
        """Test JSON deserialization."""
        json_str = '{"a":1,"m":2,"z":3}'
        result = CanonicalJSON.loads(json_str)
        
        assert result == {"a": 1, "m": 2, "z": 3}
    
    def test_canonical_nested(self):
        """Test canonical JSON with nested objects."""
        data = {
            "z": {"nested": 2},
            "a": [1, 2, 3],
            "m": "value"
        }
        result = CanonicalJSON.dumps(data)
        
        assert "a" in result
        assert "m" in result
        assert "z" in result
        assert result.index("a") < result.index("m") < result.index("z")


class TestMessageSerializer:
    """Test message serialization utilities."""
    
    def test_to_json(self):
        """Test serializing message to JSON."""
        message = {
            "id": "msg_123",
            "type": "INTENT",
            "timestamp": datetime(2026, 1, 12, 10, 0, 0)
        }
        
        json_str = MessageSerializer.to_json(message)
        assert isinstance(json_str, str)
        assert "msg_123" in json_str
        assert "INTENT" in json_str
    
    def test_from_json(self):
        """Test deserializing message from JSON."""
        json_str = '{"id":"msg_123","type":"INTENT"}'
        message = MessageSerializer.from_json(json_str)
        
        assert message["id"] == "msg_123"
        assert message["type"] == "INTENT"
    
    def test_from_json_invalid(self):
        """Test that invalid JSON raises SerializationError."""
        invalid_json = "{not valid json}"
        
        with pytest.raises(SerializationError):
            MessageSerializer.from_json(invalid_json)
    
    def test_datetime_serialization(self):
        """Test that datetime objects are converted to ISO format."""
        dt = datetime(2026, 1, 12, 10, 30, 45)
        message = {
            "timestamp": dt,
            "nested": {"time": dt}
        }
        
        json_str = MessageSerializer.to_json(message)
        assert "2026-01-12T10:30:45Z" in json_str
    
    def test_roundtrip(self):
        """Test serialization roundtrip."""
        original = {
            "id": "msg_456",
            "data": [1, 2, 3],
            "nested": {"key": "value"}
        }
        
        json_str = MessageSerializer.to_json(original)
        deserialized = MessageSerializer.from_json(json_str)
        
        assert deserialized["id"] == original["id"]
        assert deserialized["data"] == original["data"]
        assert deserialized["nested"] == original["nested"]

"""
Serialization utilities for IoAP Protocol.

Handles JSON parsing and canonical representation for messages.
"""

import json
from typing import Dict, Any
from datetime import datetime


class SerializationError(Exception):
    """Raised when serialization/deserialization fails."""
    pass


class CanonicalJSON:
    """
    Utilities for canonical JSON representation.
    
    Ensures deterministic output regardless of input order.
    """
    
    @staticmethod
    def dumps(obj: Dict[str, Any], **kwargs) -> str:
        """
        Serialize to canonical JSON.
        
        Args:
            obj: Object to serialize
            **kwargs: Additional json.dumps arguments (ignored)
            
        Returns:
            Canonical JSON string (sorted keys, minimal spacing)
        """
        return json.dumps(obj, separators=(",", ":"), sort_keys=True)
    
    @staticmethod
    def loads(s: str) -> Dict[str, Any]:
        """
        Deserialize from JSON.
        
        Args:
            s: JSON string
            
        Returns:
            Deserialized dict
        """
        return json.loads(s)


class MessageSerializer:
    """
    Serialization utilities for Protocol messages.
    """
    
    @staticmethod
    def to_json(message_dict: Dict[str, Any]) -> str:
        """
        Serialize message to JSON.
        
        Args:
            message_dict: Message dictionary
            
        Returns:
            JSON string
        """
        # Convert datetime objects to ISO format strings
        data = MessageSerializer._serialize_datetime(message_dict)
        return json.dumps(data, default=str)
    
    @staticmethod
    def from_json(json_str: str) -> Dict[str, Any]:
        """
        Deserialize message from JSON.
        
        Args:
            json_str: JSON string
            
        Returns:
            Message dictionary
        """
        try:
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError as e:
            raise SerializationError(f"Invalid JSON: {e}")
    
    @staticmethod
    def _serialize_datetime(obj: Any) -> Any:
        """
        Recursively convert datetime objects to ISO format strings.
        """
        if isinstance(obj, dict):
            return {k: MessageSerializer._serialize_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [MessageSerializer._serialize_datetime(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat() + "Z"
        else:
            return obj

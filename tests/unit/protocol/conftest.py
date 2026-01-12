"""
Pytest fixtures for protocol tests.
"""

import pytest
from aiconexus.protocol.security import DIDKey


@pytest.fixture
def did_key_a():
    """Generate a test DID:key for Agent A."""
    return DIDKey.generate()


@pytest.fixture
def did_key_b():
    """Generate a test DID:key for Agent B."""
    return DIDKey.generate()


@pytest.fixture
def sample_message_dict(did_key_a, did_key_b):
    """Create a sample message dictionary."""
    return {
        "id": "msg_test_123",
        "from": did_key_a.did,
        "to": did_key_b.did,
        "type": "INTENT",
        "timestamp": "2026-01-12T10:00:00Z",
        "payload": {"query": "test query"},
        "version": "1.0"
    }

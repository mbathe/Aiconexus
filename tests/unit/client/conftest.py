"""
Pytest fixtures for client tests.
"""

import pytest
from aiconexus.protocol.security import DIDKey, MessageSigner


@pytest.fixture
def test_did_key() -> DIDKey:
    """Generate test DID key."""
    return DIDKey.generate()


@pytest.fixture
def test_signer(test_did_key: DIDKey) -> MessageSigner:
    """Create message signer from test DID key."""
    return MessageSigner(test_did_key)

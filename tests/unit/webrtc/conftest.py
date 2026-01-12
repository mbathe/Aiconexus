"""
Fixtures for WebRTC tests.
"""

import pytest
from aiconexus.protocol.security import DIDKey
from aiconexus.webrtc.models import DataChannelConfig


@pytest.fixture
def local_did_key():
    """Create a local DID key."""
    return DIDKey.generate()


@pytest.fixture
def remote_did_key():
    """Create a remote DID key."""
    return DIDKey.generate()


@pytest.fixture
def datachannel_config():
    """Create a basic DataChannel config."""
    return DataChannelConfig(
        label="test-channel",
        ordered=True,
        protocol="aiconexus-v1",
    )


@pytest.fixture
def message_channel_config():
    """Create a message DataChannel config."""
    return DataChannelConfig(
        label="messages",
        ordered=True,
        compressed=True,
    )


@pytest.fixture
def bulk_transfer_config():
    """Create a bulk transfer DataChannel config."""
    return DataChannelConfig(
        label="bulk",
        ordered=False,
        max_retransmits=3,
        compressed=True,
    )

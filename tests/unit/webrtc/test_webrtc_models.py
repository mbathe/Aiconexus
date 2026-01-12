"""
Unit tests for WebRTC models.
"""

import pytest
from aiconexus.webrtc.models import (
    ICECandidate,
    ICECandidateType,
    SDPOffer,
    SDPAnswer,
    DataChannelConfig,
    DataChannelMessage,
    ConnectionState,
    ICEConnectionState,
)


class TestICECandidate:
    """Test ICECandidate model."""
    
    def test_create_ice_candidate(self):
        """Test creating an ICE candidate."""
        candidate = ICECandidate(
            candidate="candidate:123 1 udp 1234 192.168.1.1 5000 typ host",
            sdp_mline_index=0,
            sdp_mid="0",
        )
        
        assert candidate.candidate == "candidate:123 1 udp 1234 192.168.1.1 5000 typ host"
        assert candidate.sdp_mline_index == 0
        assert candidate.sdp_mid == "0"
    
    def test_ice_candidate_with_optional_fields(self):
        """Test ICE candidate with optional fields."""
        candidate = ICECandidate(
            candidate="candidate:123 1 udp 1234 192.168.1.1 5000 typ srflx",
            sdp_mline_index=0,
            sdp_mid="0",
            candidate_type=ICECandidateType.SRFLX,
            priority=1234,
            foundation="abc123",
            address="192.168.1.1",
            port=5000,
        )
        
        assert candidate.priority == 1234
        assert candidate.foundation == "abc123"
        assert candidate.candidate_type == ICECandidateType.SRFLX
        assert candidate.address == "192.168.1.1"
        assert candidate.port == 5000


class TestSDPOffer:
    """Test SDPOffer model."""
    
    def test_create_sdp_offer(self):
        """Test creating an SDP offer."""
        sdp_string = "v=0\r\no=- 123 456 IN IP4 0.0.0.0\r\n"
        offer = SDPOffer(sdp=sdp_string)
        
        assert offer.sdp == sdp_string
        assert offer.ice_candidates == []
    
    def test_sdp_offer_with_candidates(self):
        """Test SDP offer with ICE candidates."""
        sdp_string = "v=0\r\no=- 123 456 IN IP4 0.0.0.0\r\n"
        candidate = ICECandidate(
            candidate="candidate:123 1 udp 1234 192.168.1.1 5000 typ host",
            sdp_mline_index=0,
            sdp_mid="0",
        )
        
        offer = SDPOffer(
            sdp=sdp_string,
            ice_candidates=[candidate],
            ice_ufrag="abc123def456",
            ice_pwd="pwd123456789012345678901234",
        )
        
        assert len(offer.ice_candidates) == 1
        assert offer.ice_ufrag == "abc123def456"
        assert offer.ice_pwd == "pwd123456789012345678901234"


class TestSDPAnswer:
    """Test SDPAnswer model."""
    
    def test_create_sdp_answer(self):
        """Test creating an SDP answer."""
        sdp_string = "v=0\r\no=- 789 012 IN IP4 0.0.0.0\r\n"
        answer = SDPAnswer(sdp=sdp_string)
        
        assert answer.sdp == sdp_string
        assert answer.ice_candidates == []
    
    def test_sdp_answer_with_candidates(self):
        """Test SDP answer with ICE candidates."""
        sdp_string = "v=0\r\no=- 789 012 IN IP4 0.0.0.0\r\n"
        candidate = ICECandidate(
            candidate="candidate:789 1 udp 5678 192.168.1.2 5001 typ host",
            sdp_mline_index=0,
            sdp_mid="0",
        )
        
        answer = SDPAnswer(
            sdp=sdp_string,
            ice_candidates=[candidate],
            ice_ufrag="xyz789abc123",
            ice_pwd="pwd987654321098765432109876",
        )
        
        assert len(answer.ice_candidates) == 1


class TestDataChannelConfig:
    """Test DataChannelConfig model."""
    
    def test_create_datachannel_config(self):
        """Test creating a DataChannel config."""
        config = DataChannelConfig(label="test")
        
        assert config.label == "test"
        assert config.ordered is True
        assert config.negotiated is False
        assert config.compressed is True
    
    def test_datachannel_config_with_options(self):
        """Test DataChannel config with custom options."""
        config = DataChannelConfig(
            label="bulk-transfer",
            ordered=False,
            max_retransmits=5,
            protocol="custom-v1",
            negotiated=True,
            id=1,
            compressed=False,
        )
        
        assert config.label == "bulk-transfer"
        assert config.ordered is False
        assert config.max_retransmits == 5
        assert config.protocol == "custom-v1"
        assert config.negotiated is True
        assert config.id == 1
        assert config.compressed is False


class TestDataChannelMessage:
    """Test DataChannelMessage model."""
    
    def test_create_message(self):
        """Test creating a DataChannel message."""
        message = DataChannelMessage(
            channel_label="test",
            data={"type": "hello", "content": "world"},
            timestamp=1234567890.0,
        )
        
        assert message.channel_label == "test"
        assert message.data == {"type": "hello", "content": "world"}
        assert message.timestamp == 1234567890.0
    
    def test_message_with_sequence(self):
        """Test message with sequence number."""
        message = DataChannelMessage(
            channel_label="ordered",
            data="sequential data",
            timestamp=1234567890.0,
            sequence=42,
        )
        
        assert message.sequence == 42


class TestConnectionState:
    """Test ConnectionState enum."""
    
    def test_connection_states(self):
        """Test all connection states."""
        assert ConnectionState.NEW == "new"
        assert ConnectionState.CONNECTING == "connecting"
        assert ConnectionState.CONNECTED == "connected"
        assert ConnectionState.DISCONNECTED == "disconnected"
        assert ConnectionState.FAILED == "failed"
        assert ConnectionState.CLOSED == "closed"


class TestICEConnectionState:
    """Test ICEConnectionState enum."""
    
    def test_ice_connection_states(self):
        """Test all ICE connection states."""
        assert ICEConnectionState.NEW == "new"
        assert ICEConnectionState.CHECKING == "checking"
        assert ICEConnectionState.CONNECTED == "connected"
        assert ICEConnectionState.COMPLETED == "completed"
        assert ICEConnectionState.FAILED == "failed"
        assert ICEConnectionState.DISCONNECTED == "disconnected"
        assert ICEConnectionState.CLOSED == "closed"

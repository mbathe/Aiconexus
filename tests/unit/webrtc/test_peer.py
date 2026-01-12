"""
Unit tests for PeerConnection.
"""

import pytest
from aiconexus.webrtc.peer import PeerConnection
from aiconexus.webrtc.models import (
    DataChannelConfig,
    ICECandidate,
    ConnectionState,
    ICEConnectionState,
)


class TestPeerConnectionCreation:
    """Test PeerConnection creation and initialization."""
    
    def test_create_peer_connection(self, local_did_key, remote_did_key):
        """Test creating a peer connection."""
        peer = PeerConnection(
            local_did=local_did_key.did,
            remote_did=remote_did_key.did,
        )
        
        assert peer.local_did == local_did_key.did
        assert peer.remote_did == remote_did_key.did
        assert peer.connection_state == ConnectionState.NEW
        assert peer.ice_connection_state == ICEConnectionState.NEW
    
    def test_peer_connection_with_custom_id(self, local_did_key, remote_did_key):
        """Test peer connection with custom ID."""
        peer = PeerConnection(
            local_did=local_did_key.did,
            remote_did=remote_did_key.did,
            peer_id="custom-id-123",
        )
        
        assert peer.peer_id == "custom-id-123"
    
    def test_peer_connection_auto_id(self, local_did_key, remote_did_key):
        """Test peer connection gets auto-generated ID."""
        peer = PeerConnection(
            local_did=local_did_key.did,
            remote_did=remote_did_key.did,
        )
        
        assert peer.peer_id is not None
        assert len(peer.peer_id) > 0


class TestOfferAnswerExchange:
    """Test SDP offer/answer exchange."""
    
    @pytest.mark.asyncio
    async def test_create_offer(self, local_did_key, remote_did_key):
        """Test creating an SDP offer."""
        peer = PeerConnection(
            local_did=local_did_key.did,
            remote_did=remote_did_key.did,
        )
        
        offer = await peer.create_offer()
        
        assert offer is not None
        assert offer.sdp is not None
        assert len(offer.sdp) > 0
        assert peer.connection_state == ConnectionState.CONNECTING
    
    @pytest.mark.asyncio
    async def test_cannot_create_offer_twice(self, local_did_key, remote_did_key):
        """Test that offer cannot be created twice."""
        peer = PeerConnection(
            local_did=local_did_key.did,
            remote_did=remote_did_key.did,
        )
        
        await peer.create_offer()
        
        with pytest.raises(RuntimeError):
            await peer.create_offer()
    
    @pytest.mark.asyncio
    async def test_set_remote_offer(self, local_did_key, remote_did_key):
        """Test setting remote offer."""
        peer = PeerConnection(
            local_did=local_did_key.did,
            remote_did=remote_did_key.did,
        )
        
        remote_peer = PeerConnection(
            local_did=remote_did_key.did,
            remote_did=local_did_key.did,
        )
        
        offer = await remote_peer.create_offer()
        await peer.set_remote_offer(offer)
        
        assert peer.get_remote_offer() == offer
        assert peer.ice_connection_state == ICEConnectionState.CHECKING
    
    @pytest.mark.asyncio
    async def test_create_answer(self, local_did_key, remote_did_key):
        """Test creating SDP answer."""
        peer = PeerConnection(
            local_did=local_did_key.did,
            remote_did=remote_did_key.did,
        )
        
        remote_peer = PeerConnection(
            local_did=remote_did_key.did,
            remote_did=local_did_key.did,
        )
        
        offer = await remote_peer.create_offer()
        await peer.set_remote_offer(offer)
        
        answer = await peer.create_answer()
        
        assert answer is not None
        assert answer.sdp is not None
        assert len(answer.sdp) > 0
    
    @pytest.mark.asyncio
    async def test_cannot_create_answer_without_offer(self, local_did_key, remote_did_key):
        """Test that answer cannot be created without remote offer."""
        peer = PeerConnection(
            local_did=local_did_key.did,
            remote_did=remote_did_key.did,
        )
        
        with pytest.raises(RuntimeError):
            await peer.create_answer()
    
    @pytest.mark.asyncio
    async def test_set_remote_answer(self, local_did_key, remote_did_key):
        """Test setting remote answer."""
        peer1 = PeerConnection(
            local_did=local_did_key.did,
            remote_did=remote_did_key.did,
        )
        
        peer2 = PeerConnection(
            local_did=remote_did_key.did,
            remote_did=local_did_key.did,
        )
        
        offer = await peer1.create_offer()
        await peer2.set_remote_offer(offer)
        answer = await peer2.create_answer()
        
        await peer1.set_remote_answer(answer)
        
        assert peer1.get_remote_answer() == answer
        assert peer1.connection_state == ConnectionState.CONNECTED
        assert peer1.ice_connection_state == ICEConnectionState.CONNECTED


class TestICECandidates:
    """Test ICE candidate handling."""
    
    @pytest.mark.asyncio
    async def test_add_ice_candidate(self, local_did_key, remote_did_key):
        """Test adding ICE candidate."""
        peer = PeerConnection(
            local_did=local_did_key.did,
            remote_did=remote_did_key.did,
        )
        
        candidate = ICECandidate(
            candidate="candidate:123 1 udp 1234 192.168.1.1 5000 typ host",
            sdp_mline_index=0,
            sdp_mid="0",
        )
        
        await peer.add_ice_candidate(candidate)
        
        candidates = peer.get_ice_candidates()
        assert len(candidates) == 1
        assert candidates[0] == candidate
    
    @pytest.mark.asyncio
    async def test_add_multiple_candidates(self, local_did_key, remote_did_key):
        """Test adding multiple ICE candidates."""
        peer = PeerConnection(
            local_did=local_did_key.did,
            remote_did=remote_did_key.did,
        )
        
        for i in range(3):
            candidate = ICECandidate(
                candidate=f"candidate:{i} 1 udp {1234+i} 192.168.1.{1+i} {5000+i} typ host",
                sdp_mline_index=0,
                sdp_mid="0",
            )
            await peer.add_ice_candidate(candidate)
        
        candidates = peer.get_ice_candidates()
        assert len(candidates) == 3
    
    @pytest.mark.asyncio
    async def test_add_local_ice_candidate(self, local_did_key, remote_did_key):
        """Test adding locally gathered ICE candidate."""
        peer = PeerConnection(
            local_did=local_did_key.did,
            remote_did=remote_did_key.did,
        )
        
        candidate = ICECandidate(
            candidate="candidate:456 1 udp 5678 192.168.1.100 6000 typ host",
            sdp_mline_index=0,
            sdp_mid="0",
        )
        
        await peer.add_local_ice_candidate(candidate)
        
        local_candidates = peer.get_local_ice_candidates()
        assert len(local_candidates) == 1
        assert local_candidates[0] == candidate


class TestDataChannelOperations:
    """Test data channel operations."""
    
    @pytest.mark.asyncio
    async def test_create_data_channel(self, local_did_key, remote_did_key, datachannel_config):
        """Test creating a data channel."""
        peer = PeerConnection(
            local_did=local_did_key.did,
            remote_did=remote_did_key.did,
        )
        
        # Establish connection first
        remote_peer = PeerConnection(
            local_did=remote_did_key.did,
            remote_did=local_did_key.did,
        )
        
        offer = await peer.create_offer()
        await remote_peer.set_remote_offer(offer)
        answer = await remote_peer.create_answer()
        await peer.set_remote_answer(answer)
        
        # Now create channel
        label = await peer.create_data_channel(datachannel_config)
        
        assert label == "test-channel"
        channels = peer.get_data_channels()
        assert "test-channel" in channels
    
    @pytest.mark.asyncio
    async def test_cannot_create_channel_without_connection(self, local_did_key, remote_did_key, datachannel_config):
        """Test that channel cannot be created without established connection."""
        peer = PeerConnection(
            local_did=local_did_key.did,
            remote_did=remote_did_key.did,
        )
        
        with pytest.raises(RuntimeError):
            await peer.create_data_channel(datachannel_config)
    
    @pytest.mark.asyncio
    async def test_multiple_data_channels(self, local_did_key, remote_did_key):
        """Test creating multiple data channels."""
        peer = PeerConnection(
            local_did=local_did_key.did,
            remote_did=remote_did_key.did,
        )
        
        remote_peer = PeerConnection(
            local_did=remote_did_key.did,
            remote_did=local_did_key.did,
        )
        
        offer = await peer.create_offer()
        await remote_peer.set_remote_offer(offer)
        answer = await remote_peer.create_answer()
        await peer.set_remote_answer(answer)
        
        # Create multiple channels
        for i in range(3):
            config = DataChannelConfig(label=f"channel-{i}")
            await peer.create_data_channel(config)
        
        channels = peer.get_data_channels()
        assert len(channels) == 3


class TestConnectionStateCallbacks:
    """Test state change callbacks."""
    
    @pytest.mark.asyncio
    async def test_state_change_callback(self, local_did_key, remote_did_key):
        """Test connection state change callback."""
        peer = PeerConnection(
            local_did=local_did_key.did,
            remote_did=remote_did_key.did,
        )
        
        states = []
        
        def on_state_change(state):
            states.append(state)
        
        peer.on_state_change(on_state_change)
        
        await peer.create_offer()
        
        assert ConnectionState.CONNECTING in states
    
    @pytest.mark.asyncio
    async def test_ice_state_callback(self, local_did_key, remote_did_key):
        """Test ICE state change callback."""
        peer = PeerConnection(
            local_did=local_did_key.did,
            remote_did=remote_did_key.did,
        )
        
        states = []
        
        def on_ice_state_change(state):
            states.append(state)
        
        peer.on_ice_state_change(on_ice_state_change)
        
        remote_peer = PeerConnection(
            local_did=remote_did_key.did,
            remote_did=local_did_key.did,
        )
        
        offer = await remote_peer.create_offer()
        await peer.set_remote_offer(offer)
        
        assert ICEConnectionState.CHECKING in states


class TestConnectionLifecycle:
    """Test connection lifecycle."""
    
    @pytest.mark.asyncio
    async def test_close_connection(self, local_did_key, remote_did_key):
        """Test closing a connection."""
        peer = PeerConnection(
            local_did=local_did_key.did,
            remote_did=remote_did_key.did,
        )
        
        await peer.close()
        
        assert peer.connection_state == ConnectionState.CLOSED
        assert peer.ice_connection_state == ICEConnectionState.CLOSED
    
    @pytest.mark.asyncio
    async def test_is_connected(self, local_did_key, remote_did_key):
        """Test is_connected method."""
        peer = PeerConnection(
            local_did=local_did_key.did,
            remote_did=remote_did_key.did,
        )
        
        assert not peer.is_connected()
        
        remote_peer = PeerConnection(
            local_did=remote_did_key.did,
            remote_did=local_did_key.did,
        )
        
        offer = await peer.create_offer()
        await remote_peer.set_remote_offer(offer)
        answer = await remote_peer.create_answer()
        await peer.set_remote_answer(answer)
        
        assert peer.is_connected()
    
    @pytest.mark.asyncio
    async def test_age_property(self, local_did_key, remote_did_key):
        """Test connection age property."""
        import time
        
        peer = PeerConnection(
            local_did=local_did_key.did,
            remote_did=remote_did_key.did,
        )
        
        time.sleep(0.1)
        age = peer.age_seconds
        
        assert age >= 0.1

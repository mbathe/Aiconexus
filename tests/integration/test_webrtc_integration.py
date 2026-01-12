"""
Integration tests for WebRTC P2P communication.
"""

import pytest
from aiconexus.protocol.security import DIDKey
from aiconexus.webrtc.peer import PeerConnection
from aiconexus.webrtc.datachannel import DataChannelManager
from aiconexus.webrtc.models import DataChannelConfig, ConnectionState, ICEConnectionState


@pytest.fixture
def initiator_did():
    """Create initiator DID."""
    return DIDKey.generate()


@pytest.fixture
def responder_did():
    """Create responder DID."""
    return DIDKey.generate()


class TestPeerToPeerConnection:
    """Test peer-to-peer connection establishment."""
    
    @pytest.mark.asyncio
    async def test_simple_connection_flow(self, initiator_did, responder_did):
        """Test simple P2P connection flow."""
        # Create two peers
        initiator = PeerConnection(
            local_did=initiator_did.did,
            remote_did=responder_did.did,
        )
        
        responder = PeerConnection(
            local_did=responder_did.did,
            remote_did=initiator_did.did,
        )
        
        # Initiator creates offer
        offer = await initiator.create_offer()
        assert offer is not None
        assert initiator.connection_state == ConnectionState.CONNECTING
        
        # Responder receives offer
        await responder.set_remote_offer(offer)
        assert responder.ice_connection_state == ICEConnectionState.CHECKING
        
        # Responder creates answer
        answer = await responder.create_answer()
        assert answer is not None
        
        # Initiator receives answer
        await initiator.set_remote_answer(answer)
        
        # Verify connection established on initiator
        assert initiator.is_connected()
    
    @pytest.mark.asyncio
    async def test_ice_candidate_exchange(self, initiator_did, responder_did):
        """Test ICE candidate exchange between peers."""
        from aiconexus.webrtc.models import ICECandidate
        
        initiator = PeerConnection(
            local_did=initiator_did.did,
            remote_did=responder_did.did,
        )
        
        responder = PeerConnection(
            local_did=responder_did.did,
            remote_did=initiator_did.did,
        )
        
        # Start connection
        offer = await initiator.create_offer()
        await responder.set_remote_offer(offer)
        answer = await responder.create_answer()
        await initiator.set_remote_answer(answer)
        
        # Exchange ICE candidates
        candidate1 = ICECandidate(
            candidate="candidate:1 1 udp 1234 192.168.1.1 5000 typ host",
            sdp_mline_index=0,
            sdp_mid="0",
        )
        
        candidate2 = ICECandidate(
            candidate="candidate:2 1 udp 5678 192.168.1.2 5001 typ host",
            sdp_mline_index=0,
            sdp_mid="0",
        )
        
        # Initiator adds candidate from responder
        await initiator.add_ice_candidate(candidate2)
        
        # Responder adds candidate from initiator
        await responder.add_ice_candidate(candidate1)
        
        # Verify candidates stored
        assert len(initiator.get_ice_candidates()) == 1
        assert len(responder.get_ice_candidates()) == 1


class TestDataChannelCommunication:
    """Test data channel creation and communication."""
    
    @pytest.mark.asyncio
    async def test_single_data_channel(self, initiator_did, responder_did):
        """Test creating and using a single data channel."""
        # Establish connection
        initiator = PeerConnection(
            local_did=initiator_did.did,
            remote_did=responder_did.did,
        )
        
        responder = PeerConnection(
            local_did=responder_did.did,
            remote_did=initiator_did.did,
        )
        
        offer = await initiator.create_offer()
        await responder.set_remote_offer(offer)
        answer = await responder.create_answer()
        await initiator.set_remote_answer(answer)
        
        # Create data channel
        config = DataChannelConfig(label="messages")
        channel_label = await initiator.create_data_channel(config)
        
        assert channel_label == "messages"
        assert len(initiator.get_data_channels()) == 1
    
    @pytest.mark.asyncio
    async def test_multiple_data_channels(self, initiator_did, responder_did):
        """Test creating multiple data channels."""
        # Establish connection
        initiator = PeerConnection(
            local_did=initiator_did.did,
            remote_did=responder_did.did,
        )
        
        responder = PeerConnection(
            local_did=responder_did.did,
            remote_did=initiator_did.did,
        )
        
        offer = await initiator.create_offer()
        await responder.set_remote_offer(offer)
        answer = await responder.create_answer()
        await initiator.set_remote_answer(answer)
        
        # Create multiple channels
        channels = ["messages", "events", "bulk"]
        for label in channels:
            config = DataChannelConfig(label=label)
            await initiator.create_data_channel(config)
        
        assert len(initiator.get_data_channels()) == 3
        for label in channels:
            assert label in initiator.get_data_channels()


class TestDataChannelManager:
    """Test DataChannelManager integration."""
    
    @pytest.mark.asyncio
    async def test_manager_with_peer_connection(self, initiator_did, responder_did):
        """Test DataChannelManager with peer connection."""
        peer = PeerConnection(
            local_did=initiator_did.did,
            remote_did=responder_did.did,
        )
        
        remote = PeerConnection(
            local_did=responder_did.did,
            remote_did=initiator_did.did,
        )
        
        # Establish connection
        offer = await peer.create_offer()
        await remote.set_remote_offer(offer)
        answer = await remote.create_answer()
        await peer.set_remote_answer(answer)
        
        # Create manager
        manager = DataChannelManager()
        
        config = DataChannelConfig(label="test")
        channel = await manager.create_channel(config)
        
        assert channel is not None
        assert manager.get_channel_count() == 1
    
    @pytest.mark.asyncio
    async def test_datachannel_message_flow(self, initiator_did, responder_did):
        """Test message flow through data channel."""
        manager = DataChannelManager()
        
        config = DataChannelConfig(label="messages")
        channel = await manager.create_channel(config)
        
        messages_received = []
        
        def on_message(msg):
            messages_received.append(msg)
        
        channel.on_message(on_message)
        
        # Send and receive message
        await channel.send({"type": "hello", "content": "world"})
        await manager.receive_on_channel("messages", {"type": "reply", "content": "received"})
        
        assert len(messages_received) == 1
        assert messages_received[0]["type"] == "reply"


class TestConnectionStateTransitions:
    """Test connection state transitions."""
    
    @pytest.mark.asyncio
    async def test_connection_state_progression(self, initiator_did, responder_did):
        """Test connection state changes through lifecycle."""
        peer = PeerConnection(
            local_did=initiator_did.did,
            remote_did=responder_did.did,
        )
        
        states = []
        
        def track_state(state):
            states.append(state)
        
        peer.on_state_change(track_state)
        
        # Initial state
        assert peer.connection_state == ConnectionState.NEW
        
        # Create offer
        await peer.create_offer()
        assert ConnectionState.CONNECTING in states
        
        # Close
        await peer.close()
        assert peer.connection_state == ConnectionState.CLOSED
    
    @pytest.mark.asyncio
    async def test_ice_connection_state_progression(self, initiator_did, responder_did):
        """Test ICE connection state changes."""
        peer = PeerConnection(
            local_did=initiator_did.did,
            remote_did=responder_did.did,
        )
        
        remote = PeerConnection(
            local_did=responder_did.did,
            remote_did=initiator_did.did,
        )
        
        ice_states = []
        
        def track_ice_state(state):
            ice_states.append(state)
        
        peer.on_ice_state_change(track_ice_state)
        
        # Initial state
        assert peer.ice_connection_state == ICEConnectionState.NEW
        
        # Set remote offer
        offer = await remote.create_offer()
        await peer.set_remote_offer(offer)
        assert ICEConnectionState.CHECKING in ice_states
        
        # Complete connection
        answer = await peer.create_answer()
        await remote.set_remote_answer(answer)


class TestErrorHandling:
    """Test error handling in P2P scenarios."""
    
    @pytest.mark.asyncio
    async def test_answer_without_offer(self, initiator_did, responder_did):
        """Test that answer cannot be created without offer."""
        peer = PeerConnection(
            local_did=initiator_did.did,
            remote_did=responder_did.did,
        )
        
        with pytest.raises(RuntimeError):
            await peer.create_answer()
    
    @pytest.mark.asyncio
    async def test_close_on_new_connection(self, initiator_did, responder_did):
        """Test closing connection in NEW state."""
        peer = PeerConnection(
            local_did=initiator_did.did,
            remote_did=responder_did.did,
        )
        
        await peer.close()
        
        assert peer.connection_state == ConnectionState.CLOSED
    
    @pytest.mark.asyncio
    async def test_duplicate_channel_label(self, initiator_did, responder_did):
        """Test that duplicate channel labels are rejected."""
        peer = PeerConnection(
            local_did=initiator_did.did,
            remote_did=responder_did.did,
        )
        
        remote = PeerConnection(
            local_did=responder_did.did,
            remote_did=initiator_did.did,
        )
        
        # Establish connection
        offer = await peer.create_offer()
        await remote.set_remote_offer(offer)
        answer = await remote.create_answer()
        await peer.set_remote_answer(answer)
        
        # Create channel
        config1 = DataChannelConfig(label="test")
        await peer.create_data_channel(config1)
        
        # Try to create duplicate
        config2 = DataChannelConfig(label="test")
        with pytest.raises(ValueError):
            manager = DataChannelManager()
            await manager.create_channel(config1)
            await manager.create_channel(config2)


class TestConcurrentOperations:
    """Test concurrent peer operations."""
    
    @pytest.mark.asyncio
    async def test_concurrent_peer_connections(self, initiator_did, responder_did):
        """Test multiple concurrent peer connections."""
        import asyncio
        
        peers_created = []
        
        async def create_peer(i):
            peer = PeerConnection(
                local_did=f"did:key:{i}",
                remote_did=f"did:key:{i+1000}",
            )
            peers_created.append(peer)
            offer = await peer.create_offer()
            return peer
        
        # Create 5 peers concurrently
        peers = await asyncio.gather(*[create_peer(i) for i in range(5)])
        
        assert len(peers) == 5
        assert all(p.connection_state == ConnectionState.CONNECTING for p in peers)
    
    @pytest.mark.asyncio
    async def test_concurrent_datachannel_creation(self, initiator_did, responder_did):
        """Test concurrent data channel creation."""
        import asyncio
        
        manager = DataChannelManager()
        
        async def create_channels(count):
            for i in range(count):
                config = DataChannelConfig(label=f"channel-{asyncio.current_task().get_name()}-{i}")
                await manager.create_channel(config)
        
        # Create channels from multiple tasks
        await asyncio.gather(
            create_channels(3),
            create_channels(3),
        )
        
        assert manager.get_channel_count() == 6

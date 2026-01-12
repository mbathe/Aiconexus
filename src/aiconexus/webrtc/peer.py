"""
P2P Peer Connection manager for WebRTC.

Manages the lifecycle of peer connections between agents, including
connection establishment, media negotiation, and state management.
"""

import asyncio
import uuid
from typing import Optional, Callable, Dict, List, Any
from datetime import datetime

from aiconexus.webrtc.models import (
    SDPOffer,
    SDPAnswer,
    ICECandidate,
    DataChannelConfig,
    ConnectionState,
    ICEConnectionState,
)


class PeerConnection:
    """
    Manages a WebRTC peer connection between two agents.
    
    This class handles the complete lifecycle of a peer-to-peer connection:
    - Connection establishment
    - SDP offer/answer exchange
    - ICE candidate handling
    - DataChannel management
    - Connection state tracking
    
    Attributes:
        peer_id: Unique identifier for the peer
        local_did: Local agent's DID
        remote_did: Remote agent's DID
        connection_state: Current connection state
        ice_connection_state: Current ICE connection state
    """
    
    def __init__(
        self,
        local_did: str,
        remote_did: str,
        peer_id: Optional[str] = None,
    ):
        """
        Initialize a peer connection.
        
        Args:
            local_did: Local agent's DID
            remote_did: Remote agent's DID
            peer_id: Optional peer ID (generated if not provided)
        """
        self.peer_id = peer_id or str(uuid.uuid4())
        self.local_did = local_did
        self.remote_did = remote_did
        
        self.connection_state = ConnectionState.NEW
        self.ice_connection_state = ICEConnectionState.NEW
        
        self._local_offer: Optional[SDPOffer] = None
        self._remote_offer: Optional[SDPOffer] = None
        self._local_answer: Optional[SDPAnswer] = None
        self._remote_answer: Optional[SDPAnswer] = None
        
        self._ice_candidates: List[ICECandidate] = []
        self._local_ice_candidates: List[ICECandidate] = []
        
        self._data_channels: Dict[str, DataChannelConfig] = {}
        self._created_at = datetime.utcnow()
        
        self._on_state_change: Optional[Callable[[ConnectionState], None]] = None
        self._on_ice_state_change: Optional[Callable[[ICEConnectionState], None]] = None
        self._on_ice_candidate: Optional[Callable[[ICECandidate], None]] = None
        self._on_datachannel: Optional[Callable[[DataChannelConfig], None]] = None
    
    async def create_offer(self) -> SDPOffer:
        """
        Create SDP offer for connection negotiation.
        
        Returns:
            SDPOffer containing SDP string and ICE candidates
            
        Raises:
            RuntimeError: If connection not in NEW state
        """
        if self.connection_state != ConnectionState.NEW:
            raise RuntimeError(f"Cannot create offer in {self.connection_state} state")
        
        self.connection_state = ConnectionState.CONNECTING
        if self._on_state_change:
            self._on_state_change(self.connection_state)
        
        # Generate mock SDP offer
        sdp = self._generate_sdp_offer()
        
        self._local_offer = SDPOffer(
            sdp=sdp,
            ice_candidates=[],
            ice_ufrag=self._generate_ice_ufrag(),
            ice_pwd=self._generate_ice_pwd(),
        )
        
        return self._local_offer
    
    async def set_remote_offer(self, offer: SDPOffer) -> None:
        """
        Set remote SDP offer.
        
        Args:
            offer: Remote SDPOffer
            
        Raises:
            RuntimeError: If in invalid state
        """
        if self.connection_state not in (ConnectionState.NEW, ConnectionState.CONNECTING):
            raise RuntimeError(f"Cannot set offer in {self.connection_state} state")
        
        self._remote_offer = offer
        self.ice_connection_state = ICEConnectionState.CHECKING
        if self._on_ice_state_change:
            self._on_ice_state_change(self.ice_connection_state)
    
    async def create_answer(self) -> SDPAnswer:
        """
        Create SDP answer in response to offer.
        
        Returns:
            SDPAnswer containing SDP string and ICE candidates
            
        Raises:
            RuntimeError: If no remote offer set
        """
        if self._remote_offer is None:
            raise RuntimeError("Cannot create answer without remote offer")
        
        # Generate mock SDP answer
        sdp = self._generate_sdp_answer()
        
        self._local_answer = SDPAnswer(
            sdp=sdp,
            ice_candidates=[],
            ice_ufrag=self._generate_ice_ufrag(),
            ice_pwd=self._generate_ice_pwd(),
        )
        
        return self._local_answer
    
    async def set_remote_answer(self, answer: SDPAnswer) -> None:
        """
        Set remote SDP answer.
        
        Args:
            answer: Remote SDPAnswer
            
        Raises:
            RuntimeError: If in invalid state
        """
        if self._local_offer is None:
            raise RuntimeError("Cannot set answer without local offer")
        
        self._remote_answer = answer
        self.connection_state = ConnectionState.CONNECTED
        self.ice_connection_state = ICEConnectionState.CONNECTED
        
        if self._on_state_change:
            self._on_state_change(self.connection_state)
        if self._on_ice_state_change:
            self._on_ice_state_change(self.ice_connection_state)
    
    async def add_ice_candidate(self, candidate: ICECandidate) -> None:
        """
        Add ICE candidate from remote peer.
        
        Args:
            candidate: ICECandidate to add
        """
        self._ice_candidates.append(candidate)
        self.ice_connection_state = ICEConnectionState.CONNECTED
        if self._on_ice_state_change:
            self._on_ice_state_change(self.ice_connection_state)
    
    async def add_local_ice_candidate(self, candidate: ICECandidate) -> None:
        """
        Add locally gathered ICE candidate.
        
        Args:
            candidate: ICECandidate to add
        """
        self._local_ice_candidates.append(candidate)
        if self._on_ice_candidate:
            self._on_ice_candidate(candidate)
    
    async def create_data_channel(self, config: DataChannelConfig) -> str:
        """
        Create a new DataChannel.
        
        Args:
            config: DataChannelConfig for the channel
            
        Returns:
            Channel label
            
        Raises:
            RuntimeError: If connection not established
        """
        if self.connection_state != ConnectionState.CONNECTED:
            raise RuntimeError("Connection not established")
        
        self._data_channels[config.label] = config
        
        if self._on_datachannel:
            self._on_datachannel(config)
        
        return config.label
    
    async def close(self) -> None:
        """Close the peer connection."""
        self.connection_state = ConnectionState.CLOSED
        self.ice_connection_state = ICEConnectionState.CLOSED
        self._data_channels.clear()
        
        if self._on_state_change:
            self._on_state_change(self.connection_state)
        if self._on_ice_state_change:
            self._on_ice_state_change(self.ice_connection_state)
    
    def on_state_change(self, callback: Callable[[ConnectionState], None]) -> None:
        """Register connection state change callback."""
        self._on_state_change = callback
    
    def on_ice_state_change(self, callback: Callable[[ICEConnectionState], None]) -> None:
        """Register ICE state change callback."""
        self._on_ice_state_change = callback
    
    def on_ice_candidate(self, callback: Callable[[ICECandidate], None]) -> None:
        """Register ICE candidate callback."""
        self._on_ice_candidate = callback
    
    def on_datachannel(self, callback: Callable[[DataChannelConfig], None]) -> None:
        """Register DataChannel creation callback."""
        self._on_datachannel = callback
    
    def is_connected(self) -> bool:
        """Check if connection is established."""
        return self.connection_state == ConnectionState.CONNECTED
    
    def get_local_offer(self) -> Optional[SDPOffer]:
        """Get locally created offer."""
        return self._local_offer
    
    def get_remote_offer(self) -> Optional[SDPOffer]:
        """Get remote offer."""
        return self._remote_offer
    
    def get_local_answer(self) -> Optional[SDPAnswer]:
        """Get locally created answer."""
        return self._local_answer
    
    def get_remote_answer(self) -> Optional[SDPAnswer]:
        """Get remote answer."""
        return self._remote_answer
    
    def get_ice_candidates(self) -> List[ICECandidate]:
        """Get all remote ICE candidates."""
        return self._ice_candidates.copy()
    
    def get_local_ice_candidates(self) -> List[ICECandidate]:
        """Get all locally gathered ICE candidates."""
        return self._local_ice_candidates.copy()
    
    def get_data_channels(self) -> Dict[str, DataChannelConfig]:
        """Get all data channels."""
        return self._data_channels.copy()
    
    @property
    def age_seconds(self) -> float:
        """Get connection age in seconds."""
        return (datetime.utcnow() - self._created_at).total_seconds()
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"PeerConnection(peer_id={self.peer_id}, "
            f"local={self.local_did}, remote={self.remote_did}, "
            f"state={self.connection_state})"
        )
    
    # Private helper methods
    
    def _generate_sdp_offer(self) -> str:
        """Generate mock SDP offer string."""
        return (
            f"v=0\r\n"
            f"o=- {uuid.uuid4().int} 2 IN IP4 127.0.0.1\r\n"
            f"s=aiconexus-offer\r\n"
            f"t=0 0\r\n"
            f"a=group:BUNDLE 0\r\n"
            f"a=extmap-allow-mixed\r\n"
            f"m=application 9 UDP/TLS/RTP/SAVPF 120\r\n"
            f"c=IN IP4 0.0.0.0\r\n"
        )
    
    def _generate_sdp_answer(self) -> str:
        """Generate mock SDP answer string."""
        return (
            f"v=0\r\n"
            f"o=- {uuid.uuid4().int} 2 IN IP4 127.0.0.1\r\n"
            f"s=aiconexus-answer\r\n"
            f"t=0 0\r\n"
            f"a=group:BUNDLE 0\r\n"
            f"a=extmap-allow-mixed\r\n"
            f"m=application 9 UDP/TLS/RTP/SAVPF 120\r\n"
            f"c=IN IP4 0.0.0.0\r\n"
        )
    
    @staticmethod
    def _generate_ice_ufrag() -> str:
        """Generate random ICE username fragment."""
        import secrets
        return secrets.token_hex(8)
    
    @staticmethod
    def _generate_ice_pwd() -> str:
        """Generate random ICE password."""
        import secrets
        return secrets.token_hex(24)

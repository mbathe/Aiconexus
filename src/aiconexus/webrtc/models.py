"""
WebRTC data models for P2P communication.

This module defines Pydantic models for ICE candidates, SDP offers/answers,
and DataChannel configuration. These models are used to exchange connection
information between peers.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ICECandidateType(str, Enum):
    """ICE candidate type."""
    HOST = "host"
    SRFLX = "srflx"
    PRFLX = "prflx"
    RELAY = "relay"


class ICECandidate(BaseModel):
    """
    ICE (Interactive Connectivity Establishment) candidate for P2P connection.
    
    Attributes:
        candidate: The candidate string (SDP format)
        sdp_mline_index: Media line index
        sdp_mid: Media stream ID
        username_fragment: Username fragment for STUN
        priority: Candidate priority
        foundation: Candidate foundation
        component: Component (rtp or rtcp)
        candidate_type: Type of candidate (host, srflx, etc.)
        address: Candidate address
        port: Candidate port
        tcp_type: TCP type (active, passive, so)
        related_address: Related address for reflexive candidates
        related_port: Related port for reflexive candidates
    """
    
    candidate: str = Field(..., description="The candidate string")
    sdp_mline_index: int = Field(..., description="Media line index")
    sdp_mid: str = Field(..., description="Media stream ID")
    username_fragment: Optional[str] = Field(None, description="Username fragment")
    
    priority: Optional[int] = Field(None, description="Candidate priority")
    foundation: Optional[str] = Field(None, description="Candidate foundation")
    component: Optional[str] = Field("rtp", description="Component type")
    candidate_type: Optional[ICECandidateType] = Field(None, description="Candidate type")
    address: Optional[str] = Field(None, description="Candidate address")
    port: Optional[int] = Field(None, description="Candidate port")
    tcp_type: Optional[str] = Field(None, description="TCP type")
    related_address: Optional[str] = Field(None, description="Related address")
    related_port: Optional[int] = Field(None, description="Related port")


class SDPOffer(BaseModel):
    """
    SDP (Session Description Protocol) offer for initiating connection.
    
    The offer contains the local media capabilities and is sent first
    in the negotiation process.
    
    Attributes:
        sdp: The full SDP string
        ice_candidates: List of ICE candidates
        fingerprint: DTLS fingerprint
        ice_ufrag: ICE username fragment
        ice_pwd: ICE password
    """
    
    sdp: str = Field(..., description="The full SDP string")
    ice_candidates: List[ICECandidate] = Field(default_factory=list, description="ICE candidates")
    fingerprint: Optional[str] = Field(None, description="DTLS fingerprint")
    ice_ufrag: Optional[str] = Field(None, description="ICE username fragment")
    ice_pwd: Optional[str] = Field(None, description="ICE password")
    
    class Config:
        """Model configuration."""
        use_enum_values = True


class SDPAnswer(BaseModel):
    """
    SDP (Session Description Protocol) answer for responding to connection.
    
    The answer contains acknowledgment of media capabilities and is sent
    in response to an offer.
    
    Attributes:
        sdp: The full SDP string
        ice_candidates: List of ICE candidates
        fingerprint: DTLS fingerprint
        ice_ufrag: ICE username fragment
        ice_pwd: ICE password
    """
    
    sdp: str = Field(..., description="The full SDP string")
    ice_candidates: List[ICECandidate] = Field(default_factory=list, description="ICE candidates")
    fingerprint: Optional[str] = Field(None, description="DTLS fingerprint")
    ice_ufrag: Optional[str] = Field(None, description="ICE username fragment")
    ice_pwd: Optional[str] = Field(None, description="ICE password")
    
    class Config:
        """Model configuration."""
        use_enum_values = True


class DataChannelConfig(BaseModel):
    """
    Configuration for DataChannel creation.
    
    Attributes:
        label: Channel label (identifies channel purpose)
        ordered: Whether messages must arrive in order
        max_packet_lifetime: Max lifetime for unordered messages (ms)
        max_retransmits: Max retransmit attempts
        protocol: Optional protocol identifier
        negotiated: Whether channel is negotiated
        id: Channel ID (if negotiated)
        compressed: Whether messages should be compressed
    """
    
    label: str = Field(..., description="Channel label")
    ordered: bool = Field(True, description="Messages must arrive in order")
    max_packet_lifetime: Optional[int] = Field(None, description="Max packet lifetime (ms)")
    max_retransmits: Optional[int] = Field(None, description="Max retransmit attempts")
    protocol: Optional[str] = Field(None, description="Protocol identifier")
    negotiated: bool = Field(False, description="Channel is negotiated")
    id: Optional[int] = Field(None, description="Channel ID")
    compressed: bool = Field(True, description="Messages are compressed")
    
    class Config:
        """Model configuration."""
        use_enum_values = True


class DataChannelMessage(BaseModel):
    """
    Message sent over a DataChannel.
    
    Attributes:
        channel_label: Label of the channel
        data: Message data (bytes or string)
        timestamp: When message was sent
        sequence: Sequence number for ordering
    """
    
    channel_label: str = Field(..., description="Channel label")
    data: Any = Field(..., description="Message data")
    timestamp: float = Field(..., description="Message timestamp")
    sequence: Optional[int] = Field(None, description="Sequence number")


class ConnectionState(str, Enum):
    """WebRTC connection state."""
    NEW = "new"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    FAILED = "failed"
    CLOSED = "closed"


class ICEConnectionState(str, Enum):
    """ICE connection state."""
    NEW = "new"
    CHECKING = "checking"
    CONNECTED = "connected"
    COMPLETED = "completed"
    FAILED = "failed"
    DISCONNECTED = "disconnected"
    CLOSED = "closed"

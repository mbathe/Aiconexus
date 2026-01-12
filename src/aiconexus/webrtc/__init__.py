"""
WebRTC module for P2P communication in AIConexus.

Provides support for:
- ICE candidate exchange
- SDP offer/answer negotiation
- DataChannel management
- P2P peer connection handling
"""

from aiconexus.webrtc.models import (
    ICECandidate,
    SDPOffer,
    SDPAnswer,
    DataChannelConfig,
)
from aiconexus.webrtc.peer import PeerConnection
from aiconexus.webrtc.datachannel import DataChannelManager

__all__ = [
    "ICECandidate",
    "SDPOffer",
    "SDPAnswer",
    "DataChannelConfig",
    "PeerConnection",
    "DataChannelManager",
]

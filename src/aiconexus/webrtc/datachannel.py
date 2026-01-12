"""
DataChannel manager for P2P communication.

Manages the lifecycle of data channels, message routing, and
event handling for bidirectional communication between peers.
"""

import asyncio
import uuid
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime

from aiconexus.webrtc.models import DataChannelConfig, DataChannelMessage


class DataChannel:
    """
    Represents a single data channel in a peer connection.
    
    Attributes:
        label: Channel label
        id: Channel ID
        state: Channel state (connecting, open, closing, closed)
        buffered_amount: Bytes buffered for sending
    """
    
    def __init__(self, config: DataChannelConfig):
        """
        Initialize a data channel.
        
        Args:
            config: DataChannelConfig
        """
        self.config = config
        self.label = config.label
        self.id = config.id
        self.state = "connecting"
        self.buffered_amount = 0
        
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._on_open: Optional[Callable[[], None]] = None
        self._on_message: Optional[Callable[[Any], None]] = None
        self._on_close: Optional[Callable[[], None]] = None
        self._on_error: Optional[Callable[[str], None]] = None
        
        self._created_at = datetime.utcnow()
    
    async def send(self, data: Any) -> None:
        """
        Send data through the channel.
        
        Args:
            data: Data to send
            
        Raises:
            RuntimeError: If channel not open
        """
        if self.state != "open":
            raise RuntimeError(f"Cannot send on {self.state} channel")
        
        await self._message_queue.put(data)
        self.buffered_amount += len(str(data).encode())
    
    async def _receive_message(self, data: Any) -> None:
        """
        Internal method to receive message.
        
        Args:
            data: Received data
        """
        if self._on_message:
            self._on_message(data)
    
    async def open(self) -> None:
        """Open the channel."""
        self.state = "open"
        if self._on_open:
            self._on_open()
    
    async def close(self) -> None:
        """Close the channel."""
        self.state = "closed"
        if self._on_close:
            self._on_close()
    
    def on_open(self, callback: Callable[[], None]) -> None:
        """Register open callback."""
        self._on_open = callback
    
    def on_message(self, callback: Callable[[Any], None]) -> None:
        """Register message callback."""
        self._on_message = callback
    
    def on_close(self, callback: Callable[[], None]) -> None:
        """Register close callback."""
        self._on_close = callback
    
    def on_error(self, callback: Callable[[str], None]) -> None:
        """Register error callback."""
        self._on_error = callback
    
    @property
    def age_seconds(self) -> float:
        """Get channel age in seconds."""
        return (datetime.utcnow() - self._created_at).total_seconds()
    
    def __str__(self) -> str:
        """String representation."""
        return f"DataChannel(label={self.label}, state={self.state})"


class DataChannelManager:
    """
    Manages multiple data channels for a peer connection.
    
    Handles:
    - Channel lifecycle (creation, opening, closing)
    - Message routing between channels
    - Event delegation
    - Channel state tracking
    """
    
    def __init__(self):
        """Initialize the DataChannelManager."""
        self._channels: Dict[str, DataChannel] = {}
        self._channels_by_id: Dict[int, DataChannel] = {}
        self._message_handlers: Dict[str, Callable[[Any], None]] = {}
    
    async def create_channel(self, config: DataChannelConfig) -> DataChannel:
        """
        Create a new data channel.
        
        Args:
            config: DataChannelConfig
            
        Returns:
            Created DataChannel
            
        Raises:
            ValueError: If channel label already exists
        """
        if config.label in self._channels:
            raise ValueError(f"Channel '{config.label}' already exists")
        
        channel = DataChannel(config)
        self._channels[config.label] = channel
        
        if channel.id is not None:
            self._channels_by_id[channel.id] = channel
        
        # Automatically open channel
        await channel.open()
        
        return channel
    
    async def get_channel(self, label: str) -> Optional[DataChannel]:
        """
        Get a channel by label.
        
        Args:
            label: Channel label
            
        Returns:
            DataChannel or None if not found
        """
        return self._channels.get(label)
    
    async def get_channel_by_id(self, channel_id: int) -> Optional[DataChannel]:
        """
        Get a channel by ID.
        
        Args:
            channel_id: Channel ID
            
        Returns:
            DataChannel or None if not found
        """
        return self._channels_by_id.get(channel_id)
    
    async def send_on_channel(self, label: str, data: Any) -> None:
        """
        Send data on a specific channel.
        
        Args:
            label: Channel label
            data: Data to send
            
        Raises:
            ValueError: If channel not found
        """
        channel = self._channels.get(label)
        if not channel:
            raise ValueError(f"Channel '{label}' not found")
        
        await channel.send(data)
    
    async def receive_on_channel(self, label: str, data: Any) -> None:
        """
        Handle received data on a channel.
        
        Args:
            label: Channel label
            data: Received data
        """
        channel = self._channels.get(label)
        if channel:
            await channel._receive_message(data)
    
    async def close_channel(self, label: str) -> None:
        """
        Close a channel.
        
        Args:
            label: Channel label
            
        Raises:
            ValueError: If channel not found
        """
        channel = self._channels.get(label)
        if not channel:
            raise ValueError(f"Channel '{label}' not found")
        
        await channel.close()
        del self._channels[label]
        
        if channel.id is not None and channel.id in self._channels_by_id:
            del self._channels_by_id[channel.id]
    
    async def close_all(self) -> None:
        """Close all channels."""
        labels = list(self._channels.keys())
        for label in labels:
            await self.close_channel(label)
    
    def register_message_handler(self, label: str, handler: Callable[[Any], None]) -> None:
        """
        Register a message handler for a channel.
        
        Args:
            label: Channel label
            handler: Message handler function
        """
        self._message_handlers[label] = handler
    
    def get_all_channels(self) -> List[DataChannel]:
        """
        Get all channels.
        
        Returns:
            List of DataChannel objects
        """
        return list(self._channels.values())
    
    def get_channel_count(self) -> int:
        """Get number of open channels."""
        return len(self._channels)
    
    def get_open_channels(self) -> List[str]:
        """
        Get labels of all open channels.
        
        Returns:
            List of channel labels
        """
        return [label for label, ch in self._channels.items() if ch.state == "open"]
    
    async def __aenter__(self):
        """Context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close_all()
    
    def __str__(self) -> str:
        """String representation."""
        return f"DataChannelManager(channels={self.get_channel_count()})"

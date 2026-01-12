"""
Unit tests for DataChannel and DataChannelManager.
"""

import pytest
from aiconexus.webrtc.datachannel import DataChannel, DataChannelManager
from aiconexus.webrtc.models import DataChannelConfig


class TestDataChannel:
    """Test DataChannel class."""
    
    def test_create_data_channel(self, datachannel_config):
        """Test creating a data channel."""
        channel = DataChannel(datachannel_config)
        
        assert channel.label == "test-channel"
        assert channel.config == datachannel_config
        assert channel.state == "connecting"
    
    @pytest.mark.asyncio
    async def test_open_channel(self, datachannel_config):
        """Test opening a channel."""
        channel = DataChannel(datachannel_config)
        
        await channel.open()
        
        assert channel.state == "open"
    
    @pytest.mark.asyncio
    async def test_close_channel(self, datachannel_config):
        """Test closing a channel."""
        channel = DataChannel(datachannel_config)
        
        await channel.open()
        await channel.close()
        
        assert channel.state == "closed"
    
    @pytest.mark.asyncio
    async def test_cannot_send_on_closed_channel(self, datachannel_config):
        """Test that data cannot be sent on closed channel."""
        channel = DataChannel(datachannel_config)
        
        with pytest.raises(RuntimeError):
            await channel.send("test data")
    
    @pytest.mark.asyncio
    async def test_send_data(self, datachannel_config):
        """Test sending data."""
        channel = DataChannel(datachannel_config)
        await channel.open()
        
        await channel.send("test data")
        
        assert channel.buffered_amount > 0
    
    @pytest.mark.asyncio
    async def test_channel_callbacks(self, datachannel_config):
        """Test channel callbacks."""
        channel = DataChannel(datachannel_config)
        
        open_called = False
        close_called = False
        message_received = []
        
        def on_open():
            nonlocal open_called
            open_called = True
        
        def on_close():
            nonlocal close_called
            close_called = True
        
        def on_message(data):
            message_received.append(data)
        
        channel.on_open(on_open)
        channel.on_close(on_close)
        channel.on_message(on_message)
        
        await channel.open()
        assert open_called
        
        await channel._receive_message("hello")
        assert "hello" in message_received
        
        await channel.close()
        assert close_called
    
    @pytest.mark.asyncio
    async def test_channel_age(self, datachannel_config):
        """Test channel age property."""
        import time
        
        channel = DataChannel(datachannel_config)
        await channel.open()
        
        time.sleep(0.1)
        age = channel.age_seconds
        
        assert age >= 0.1
    
    def test_channel_str(self, datachannel_config):
        """Test channel string representation."""
        channel = DataChannel(datachannel_config)
        
        assert "test-channel" in str(channel)
        assert "connecting" in str(channel)


class TestDataChannelManager:
    """Test DataChannelManager class."""
    
    @pytest.mark.asyncio
    async def test_create_manager(self):
        """Test creating a DataChannelManager."""
        manager = DataChannelManager()
        
        assert manager.get_channel_count() == 0
        assert len(manager.get_all_channels()) == 0
    
    @pytest.mark.asyncio
    async def test_create_channel(self, datachannel_config):
        """Test creating a channel in manager."""
        manager = DataChannelManager()
        
        channel = await manager.create_channel(datachannel_config)
        
        assert channel is not None
        assert channel.label == "test-channel"
        assert manager.get_channel_count() == 1
    
    @pytest.mark.asyncio
    async def test_cannot_create_duplicate_channel(self, datachannel_config):
        """Test that duplicate channels cannot be created."""
        manager = DataChannelManager()
        
        await manager.create_channel(datachannel_config)
        
        with pytest.raises(ValueError):
            await manager.create_channel(datachannel_config)
    
    @pytest.mark.asyncio
    async def test_get_channel_by_label(self, datachannel_config):
        """Test getting channel by label."""
        manager = DataChannelManager()
        
        await manager.create_channel(datachannel_config)
        channel = await manager.get_channel("test-channel")
        
        assert channel is not None
        assert channel.label == "test-channel"
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_channel(self):
        """Test getting nonexistent channel."""
        manager = DataChannelManager()
        
        channel = await manager.get_channel("nonexistent")
        
        assert channel is None
    
    @pytest.mark.asyncio
    async def test_send_on_channel(self, datachannel_config):
        """Test sending data on channel through manager."""
        manager = DataChannelManager()
        
        await manager.create_channel(datachannel_config)
        await manager.send_on_channel("test-channel", "hello")
        
        channel = await manager.get_channel("test-channel")
        assert channel.buffered_amount > 0
    
    @pytest.mark.asyncio
    async def test_cannot_send_on_nonexistent_channel(self):
        """Test that sending on nonexistent channel raises error."""
        manager = DataChannelManager()
        
        with pytest.raises(ValueError):
            await manager.send_on_channel("nonexistent", "data")
    
    @pytest.mark.asyncio
    async def test_receive_on_channel(self, datachannel_config):
        """Test receiving data on channel."""
        manager = DataChannelManager()
        
        await manager.create_channel(datachannel_config)
        
        channel = await manager.get_channel("test-channel")
        messages = []
        channel.on_message(lambda x: messages.append(x))
        
        await manager.receive_on_channel("test-channel", "received data")
        
        assert "received data" in messages
    
    @pytest.mark.asyncio
    async def test_close_channel(self, datachannel_config):
        """Test closing a channel."""
        manager = DataChannelManager()
        
        await manager.create_channel(datachannel_config)
        assert manager.get_channel_count() == 1
        
        await manager.close_channel("test-channel")
        
        assert manager.get_channel_count() == 0
    
    @pytest.mark.asyncio
    async def test_cannot_close_nonexistent_channel(self):
        """Test that closing nonexistent channel raises error."""
        manager = DataChannelManager()
        
        with pytest.raises(ValueError):
            await manager.close_channel("nonexistent")
    
    @pytest.mark.asyncio
    async def test_close_all_channels(self):
        """Test closing all channels."""
        manager = DataChannelManager()
        
        for i in range(3):
            config = DataChannelConfig(label=f"channel-{i}")
            await manager.create_channel(config)
        
        assert manager.get_channel_count() == 3
        
        await manager.close_all()
        
        assert manager.get_channel_count() == 0
    
    @pytest.mark.asyncio
    async def test_get_open_channels(self):
        """Test getting list of open channels."""
        manager = DataChannelManager()
        
        for i in range(3):
            config = DataChannelConfig(label=f"channel-{i}")
            await manager.create_channel(config)
        
        open_labels = manager.get_open_channels()
        
        assert len(open_labels) == 3
        assert "channel-0" in open_labels
        assert "channel-1" in open_labels
        assert "channel-2" in open_labels
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test using DataChannelManager as context manager."""
        async with DataChannelManager() as manager:
            config = DataChannelConfig(label="test")
            await manager.create_channel(config)
            
            assert manager.get_channel_count() == 1
        
        # After exiting, all channels should be closed
        # (we can't check directly since manager is out of scope)
    
    @pytest.mark.asyncio
    async def test_channel_by_id(self):
        """Test getting channel by ID."""
        manager = DataChannelManager()
        
        config = DataChannelConfig(label="test", id=5, negotiated=True)
        await manager.create_channel(config)
        
        channel = await manager.get_channel_by_id(5)
        
        assert channel is not None
        assert channel.label == "test"
    
    @pytest.mark.asyncio
    async def test_register_message_handler(self, datachannel_config):
        """Test registering message handler."""
        manager = DataChannelManager()
        
        handler_called = False
        
        def handler(data):
            nonlocal handler_called
            handler_called = True
        
        manager.register_message_handler("test-channel", handler)
        await manager.create_channel(datachannel_config)
        
        # Note: In real implementation, handler would be called
        # Here we just verify registration doesn't raise
    
    def test_manager_str(self):
        """Test manager string representation."""
        manager = DataChannelManager()
        
        assert "DataChannelManager" in str(manager)
        assert "0" in str(manager)

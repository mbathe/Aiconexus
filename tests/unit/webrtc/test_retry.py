"""
Unit tests for connection retry logic.
"""

import pytest
import asyncio
from aiconexus.webrtc.retry import (
    RetryConfig,
    RetryState,
    RetryStrategy,
    ConnectionRetryManager,
)


class TestRetryConfig:
    """Test RetryConfig."""
    
    def test_default_config(self):
        """Test default retry configuration."""
        config = RetryConfig()
        
        assert config.max_retries == 10
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.backoff_multiplier == 2.0
        assert config.strategy == RetryStrategy.EXPONENTIAL
        assert config.jitter == 0.1
    
    def test_custom_config(self):
        """Test custom retry configuration."""
        config = RetryConfig(
            max_retries=5,
            initial_delay=0.5,
            max_delay=30.0,
            strategy=RetryStrategy.LINEAR,
        )
        
        assert config.max_retries == 5
        assert config.initial_delay == 0.5
        assert config.max_delay == 30.0
        assert config.strategy == RetryStrategy.LINEAR


class TestRetryState:
    """Test RetryState."""
    
    def test_initial_state(self):
        """Test initial retry state."""
        config = RetryConfig()
        state = RetryState(config)
        
        assert state.attempt_count == 0
        assert state.last_error is None
        assert state.should_retry() is True
        assert state.exhausted is False
    
    def test_record_attempt(self):
        """Test recording retry attempt."""
        config = RetryConfig(max_retries=3)
        state = RetryState(config)
        
        error = RuntimeError("Connection failed")
        state.record_attempt(error)
        
        assert state.attempt_count == 1
        assert state.last_error == error
        assert state.should_retry() is True
        assert state.next_retry_time is not None
    
    def test_exponential_backoff(self):
        """Test exponential backoff calculation."""
        config = RetryConfig(
            initial_delay=1.0,
            backoff_multiplier=2.0,
            jitter=0.0,  # No jitter for deterministic test
        )
        state = RetryState(config)
        
        delays = []
        for _ in range(4):
            state.record_attempt()
            delay = state.calculate_delay()
            delays.append(delay)
        
        # First delay is initial_delay * 2^1, then 2^2, etc.
        assert delays[0] == pytest.approx(2.0, rel=0.01)
        assert delays[1] == pytest.approx(4.0, rel=0.01)
        assert delays[2] == pytest.approx(8.0, rel=0.01)
    
    def test_linear_backoff(self):
        """Test linear backoff calculation."""
        config = RetryConfig(
            strategy=RetryStrategy.LINEAR,
            initial_delay=1.0,
            jitter=0.0,
        )
        state = RetryState(config)
        
        delays = []
        for _ in range(3):
            state.record_attempt()
            delay = state.calculate_delay()
            delays.append(delay)
        
        # Linear: 1.0 * 2, 1.0 * 3, 1.0 * 4 (because attempt_count is 1, 2, 3)
        assert delays[0] == pytest.approx(2.0, rel=0.01)
        assert delays[1] == pytest.approx(3.0, rel=0.01)
        assert delays[2] == pytest.approx(4.0, rel=0.01)
    
    def test_fixed_backoff(self):
        """Test fixed backoff calculation."""
        config = RetryConfig(
            strategy=RetryStrategy.FIXED,
            initial_delay=2.0,
            jitter=0.0,
        )
        state = RetryState(config)
        
        delays = []
        for _ in range(3):
            state.record_attempt()
            delay = state.calculate_delay()
            delays.append(delay)
        
        # All delays same
        assert delays[0] == pytest.approx(2.0, rel=0.01)
        assert delays[1] == pytest.approx(2.0, rel=0.01)
        assert delays[2] == pytest.approx(2.0, rel=0.01)
    
    def test_max_delay_cap(self):
        """Test that delays are capped at max_delay."""
        config = RetryConfig(
            initial_delay=1.0,
            max_delay=5.0,
            backoff_multiplier=10.0,  # Large multiplier
            jitter=0.0,
        )
        state = RetryState(config)
        
        state.record_attempt()
        state.record_attempt()
        state.record_attempt()
        
        delay = state.calculate_delay()
        assert delay <= config.max_delay
    
    def test_exhausted(self):
        """Test retry exhaustion."""
        config = RetryConfig(max_retries=2)
        state = RetryState(config)
        
        assert state.exhausted is False
        
        state.record_attempt()
        assert state.exhausted is False
        
        state.record_attempt()
        assert state.exhausted is True
    
    def test_reset(self):
        """Test state reset."""
        config = RetryConfig()
        state = RetryState(config)
        
        state.record_attempt(RuntimeError("test"))
        assert state.attempt_count == 1
        
        state.reset()
        assert state.attempt_count == 0
        assert state.last_error is None


class TestConnectionRetryManager:
    """Test ConnectionRetryManager."""
    
    @pytest.mark.asyncio
    async def test_successful_operation(self):
        """Test successful operation on first try."""
        manager = ConnectionRetryManager()
        
        call_count = 0
        
        async def operation():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await manager.execute_with_retry(operation)
        
        assert result == "success"
        assert call_count == 1
        assert manager.attempts_made == 0
    
    @pytest.mark.asyncio
    async def test_retry_until_success(self):
        """Test retrying until operation succeeds."""
        config = RetryConfig(
            max_retries=5,
            initial_delay=0.01,
            jitter=0.0,
        )
        manager = ConnectionRetryManager(config)
        
        call_count = 0
        
        async def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError("Temporary failure")
            return "success"
        
        result = await manager.execute_with_retry(operation)
        
        assert result == "success"
        assert call_count == 3
        assert manager.attempts_made == 0  # Reset after success
    
    @pytest.mark.asyncio
    async def test_exhausted_retries(self):
        """Test when retries are exhausted."""
        config = RetryConfig(
            max_retries=2,
            initial_delay=0.01,
            jitter=0.0,
        )
        manager = ConnectionRetryManager(config)
        
        call_count = 0
        
        async def operation():
            nonlocal call_count
            call_count += 1
            raise RuntimeError(f"Failure {call_count}")
        
        with pytest.raises(RuntimeError):
            await manager.execute_with_retry(operation)
        
        # Initial attempt + retries until max_retries is reached
        assert call_count == 2
        assert manager.attempts_made == 2
    
    @pytest.mark.asyncio
    async def test_on_retry_callback(self):
        """Test on_retry callback."""
        config = RetryConfig(
            max_retries=3,
            initial_delay=0.01,
            jitter=0.0,
        )
        manager = ConnectionRetryManager(config)
        
        retry_events = []
        
        def on_retry(attempt, delay):
            retry_events.append((attempt, delay))
        
        manager.on_retry(on_retry)
        
        attempt_count = 0
        
        async def operation():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise RuntimeError("Failure")
            return "success"
        
        await manager.execute_with_retry(operation)
        
        assert len(retry_events) == 2
        assert retry_events[0][0] == 1  # First retry
        assert retry_events[1][0] == 2  # Second retry
    
    @pytest.mark.asyncio
    async def test_on_exhausted_callback(self):
        """Test on_exhausted callback."""
        config = RetryConfig(max_retries=1, initial_delay=0.01)
        manager = ConnectionRetryManager(config)
        
        exhausted_called = False
        
        def on_exhausted():
            nonlocal exhausted_called
            exhausted_called = True
        
        manager.on_exhausted(on_exhausted)
        
        async def operation():
            raise RuntimeError("Failure")
        
        with pytest.raises(RuntimeError):
            await manager.execute_with_retry(operation)
        
        assert exhausted_called is True
    
    @pytest.mark.asyncio
    async def test_failure_callback(self):
        """Test failure callback."""
        config = RetryConfig(
            max_retries=2,
            initial_delay=0.01,
            jitter=0.0,
        )
        manager = ConnectionRetryManager(config)
        
        failures = []
        
        async def on_failure(error):
            failures.append(str(error))
        
        attempt_count = 0
        
        async def operation():
            nonlocal attempt_count
            attempt_count += 1
            raise RuntimeError(f"Error {attempt_count}")
        
        with pytest.raises(RuntimeError):
            await manager.execute_with_retry(operation, on_failure)
        
        # Called on each failure before retry
        assert len(failures) == 2
    
    def test_reset(self):
        """Test manager reset."""
        manager = ConnectionRetryManager()
        manager.retry_state.record_attempt(RuntimeError("test"))
        
        assert manager.attempts_made == 1
        
        manager.reset()
        assert manager.attempts_made == 0
    
    @pytest.mark.asyncio
    async def test_total_delay_tracking(self):
        """Test total delay tracking."""
        config = RetryConfig(
            max_retries=3,
            initial_delay=0.01,
            jitter=0.0,
        )
        manager = ConnectionRetryManager(config)
        
        attempt_count = 0
        
        async def operation():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise RuntimeError("Failure")
            return "success"
        
        await manager.execute_with_retry(operation)
        
        # After success, total_delay should be 0 (reset)
        assert manager.total_delay == 0.0

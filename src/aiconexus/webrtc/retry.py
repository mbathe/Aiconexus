"""
Connection retry logic for peer connections.

Implements exponential backoff retry strategy for handling
failed peer connection establishment and reconnection scenarios.
"""

import asyncio
import logging
from typing import Optional, Callable, Coroutine, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class RetryStrategy(str, Enum):
    """Retry strategy type."""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"


@dataclass
class RetryConfig:
    """Configuration for connection retry behavior.
    
    Attributes:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds (before first retry)
        max_delay: Maximum delay between retries in seconds
        backoff_multiplier: Multiplier for exponential backoff
        strategy: Retry strategy (exponential, linear, fixed)
        jitter: Add random jitter to delays (0.0 to 1.0)
    """
    
    max_retries: int = 10
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_multiplier: float = 2.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    jitter: float = 0.1


class RetryState:
    """Track retry state for a connection."""
    
    def __init__(self, config: RetryConfig):
        """Initialize retry state.
        
        Args:
            config: RetryConfig for this connection
        """
        self.config = config
        self.attempt_count = 0
        self.last_error: Optional[Exception] = None
        self.last_retry_time: Optional[datetime] = None
        self.next_retry_time: Optional[datetime] = None
        self.total_delays: float = 0.0
    
    def calculate_delay(self) -> float:
        """Calculate delay for next retry.
        
        Returns:
            Delay in seconds
        """
        if self.attempt_count == 0:
            delay = self.config.initial_delay
        elif self.config.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.config.initial_delay * (self.config.backoff_multiplier ** self.attempt_count)
        elif self.config.strategy == RetryStrategy.LINEAR:
            delay = self.config.initial_delay * (self.attempt_count + 1)
        else:  # FIXED
            delay = self.config.initial_delay
        
        # Cap at max_delay
        delay = min(delay, self.config.max_delay)
        
        # Add jitter
        import random
        if self.config.jitter > 0:
            jitter_amount = delay * self.config.jitter * random.random()
            delay += jitter_amount
        
        return delay
    
    def should_retry(self) -> bool:
        """Check if should retry.
        
        Returns:
            True if should retry, False otherwise
        """
        return self.attempt_count < self.config.max_retries
    
    def record_attempt(self, error: Optional[Exception] = None) -> None:
        """Record a retry attempt.
        
        Args:
            error: Optional exception that occurred
        """
        self.attempt_count += 1
        self.last_retry_time = datetime.utcnow()
        self.last_error = error
        
        if self.should_retry():
            delay = self.calculate_delay()
            self.next_retry_time = datetime.utcnow() + timedelta(seconds=delay)
            self.total_delays += delay
            logger.debug(
                f"Retry {self.attempt_count}/{self.config.max_retries} "
                f"scheduled in {delay:.1f}s (total delay: {self.total_delays:.1f}s)"
            )
    
    def reset(self) -> None:
        """Reset retry state."""
        self.attempt_count = 0
        self.last_error = None
        self.last_retry_time = None
        self.next_retry_time = None
        self.total_delays = 0.0
    
    @property
    def exhausted(self) -> bool:
        """Check if retry attempts exhausted."""
        return self.attempt_count >= self.config.max_retries
    
    @property
    def can_retry_now(self) -> bool:
        """Check if can retry now."""
        if not self.should_retry():
            return False
        if self.next_retry_time is None:
            return True
        return datetime.utcnow() >= self.next_retry_time


class ConnectionRetryManager:
    """Manages retry logic for peer connections."""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        """Initialize retry manager.
        
        Args:
            config: RetryConfig (uses defaults if not provided)
        """
        self.config = config or RetryConfig()
        self.retry_state = RetryState(self.config)
        self._retry_task: Optional[asyncio.Task] = None
        self._on_retry: Optional[Callable[[int, float], None]] = None
        self._on_exhausted: Optional[Callable[[], None]] = None
    
    async def execute_with_retry(
        self,
        operation: Callable[[], Coroutine[Any, Any, Any]],
        on_failure: Optional[Callable[[Exception], Coroutine[Any, Any, None]]] = None,
    ) -> Any:
        """Execute operation with retry logic.
        
        Args:
            operation: Async function to execute
            on_failure: Optional callback for failures
            
        Returns:
            Result from successful operation
            
        Raises:
            The last exception if all retries exhausted
        """
        while True:
            try:
                result = await operation()
                if self.retry_state.attempt_count > 0:
                    logger.info(
                        f"Connection succeeded after {self.retry_state.attempt_count} "
                        f"retries (total delay: {self.retry_state.total_delays:.1f}s)"
                    )
                    self.retry_state.reset()
                return result
            
            except Exception as e:
                self.retry_state.record_attempt(e)
                
                if on_failure:
                    await on_failure(e)
                
                if self.retry_state.exhausted:
                    logger.error(
                        f"Connection failed after {self.retry_state.attempt_count} retries. "
                        f"Last error: {e}"
                    )
                    if self._on_exhausted:
                        self._on_exhausted()
                    raise
                
                # Wait before retry
                delay = self.retry_state.calculate_delay()
                logger.warning(
                    f"Connection attempt {self.retry_state.attempt_count} failed: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                
                if self._on_retry:
                    self._on_retry(self.retry_state.attempt_count, delay)
                
                await asyncio.sleep(delay)
    
    def on_retry(self, callback: Callable[[int, float], None]) -> None:
        """Register callback for retry events.
        
        Args:
            callback: Function called with (attempt_number, delay_seconds)
        """
        self._on_retry = callback
    
    def on_exhausted(self, callback: Callable[[], None]) -> None:
        """Register callback when retries exhausted.
        
        Args:
            callback: Function called when all retries exhausted
        """
        self._on_exhausted = callback
    
    def reset(self) -> None:
        """Reset retry state."""
        self.retry_state.reset()
    
    @property
    def attempts_made(self) -> int:
        """Number of attempts made."""
        return self.retry_state.attempt_count
    
    @property
    def last_error(self) -> Optional[Exception]:
        """Last exception encountered."""
        return self.retry_state.last_error
    
    @property
    def total_delay(self) -> float:
        """Total delay accumulated from retries."""
        return self.retry_state.total_delays

"""Load testing for AIConexus WebRTC connections.

Tests concurrent connection establishment and performance metrics collection.
"""

import asyncio
import logging
import os
import uuid
import psutil
import time
from dataclasses import dataclass
from typing import List

import pytest

from aiconexus.webrtc.peer import PeerConnection
from aiconexus.webrtc.retry import ConnectionRetryManager, RetryConfig


logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for load testing."""

    total_connections: int
    successful_connections: int
    failed_connections: int
    total_duration: float  # seconds
    avg_connection_time: float  # milliseconds
    min_connection_time: float  # milliseconds
    max_connection_time: float  # milliseconds
    peak_memory_usage: float  # MB
    peak_cpu_usage: float  # percent
    connections_per_second: float


class LoadTestRunner:
    """Runner for load testing concurrent connections."""

    def __init__(self, target_connections: int):
        """Initialize load test runner.
        
        Args:
            target_connections: Number of concurrent connections to establish.
        """
        self.target_connections = target_connections
        self.process = psutil.Process(os.getpid())
        self.connection_times: List[float] = []
        self.failed_connections: int = 0

    async def _create_peer(self) -> tuple[PeerConnection, float]:
        """Create a single peer connection and measure time.
        
        Returns:
            Tuple of (peer_connection, time_in_ms).
        """
        start_time = time.time()
        try:
            peer = PeerConnection(
                local_did=f"did:peer:{uuid.uuid4()}",
                remote_did=f"did:peer:{uuid.uuid4()}",
                peer_id="load-test-peer"
            )
            elapsed_ms = (time.time() - start_time) * 1000
            return peer, elapsed_ms
        except Exception as e:
            logger.error(f"Failed to create peer: {e}")
            self.failed_connections += 1
            elapsed_ms = (time.time() - start_time) * 1000
            return None, elapsed_ms

    async def _create_peers_batch(self, batch_size: int) -> List[PeerConnection]:
        """Create a batch of peer connections concurrently.
        
        Args:
            batch_size: Number of peers to create in this batch.
            
        Returns:
            List of successfully created peers.
        """
        tasks = [self._create_peer() for _ in range(batch_size)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        peers = []
        for result in results:
            if isinstance(result, Exception):
                self.failed_connections += 1
                continue
            peer, elapsed_ms = result
            if peer is not None:
                peers.append(peer)
                self.connection_times.append(elapsed_ms)
        
        return peers

    async def run(self, batch_size: int = 100) -> PerformanceMetrics:
        """Run load test creating target number of connections.
        
        Args:
            batch_size: Number of connections per batch.
            
        Returns:
            PerformanceMetrics with test results.
        """
        start_time = time.time()
        initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        self.connection_times = []
        self.failed_connections = 0
        peers = []
        
        # Create peers in batches
        num_batches = (self.target_connections + batch_size - 1) // batch_size
        for batch_num in range(num_batches):
            batch = await self._create_peers_batch(batch_size)
            peers.extend(batch)
            
            # Monitor resource usage periodically
            current_memory = self.process.memory_info().rss / 1024 / 1024
            logger.info(
                f"Batch {batch_num + 1}/{num_batches}: "
                f"{len(peers)} peers created, "
                f"Memory: {current_memory:.1f} MB"
            )
            
            # Small delay to prevent resource spikes
            await asyncio.sleep(0.01)
        
        # Clean up connections
        for peer in peers:
            try:
                peer.close()
            except Exception as e:
                logger.warning(f"Error closing peer: {e}")
        
        total_duration = time.time() - start_time
        
        # Collect final metrics
        peak_memory = self.process.memory_info().rss / 1024 / 1024
        peak_cpu = self.process.cpu_percent(interval=0.1)
        successful_connections = len(self.connection_times)
        
        # Calculate statistics
        if self.connection_times:
            avg_connection_time = sum(self.connection_times) / len(self.connection_times)
            min_connection_time = min(self.connection_times)
            max_connection_time = max(self.connection_times)
        else:
            avg_connection_time = 0.0
            min_connection_time = 0.0
            max_connection_time = 0.0
        
        connections_per_second = successful_connections / total_duration if total_duration > 0 else 0
        
        metrics = PerformanceMetrics(
            total_connections=self.target_connections,
            successful_connections=successful_connections,
            failed_connections=self.failed_connections,
            total_duration=total_duration,
            avg_connection_time=avg_connection_time,
            min_connection_time=min_connection_time,
            max_connection_time=max_connection_time,
            peak_memory_usage=peak_memory,
            peak_cpu_usage=peak_cpu,
            connections_per_second=connections_per_second,
        )
        
        return metrics


# =============================================================================
# Load Tests
# =============================================================================


class TestLoadBaseline:
    """Baseline load testing with modest concurrency."""

    @pytest.mark.asyncio
    async def test_100_concurrent_connections(self):
        """Test 100 concurrent peer connections."""
        runner = LoadTestRunner(target_connections=100)
        metrics = await runner.run(batch_size=25)
        
        # Validate baseline requirements
        assert metrics.successful_connections >= 95, \
            f"Expected at least 95 successful connections, got {metrics.successful_connections}"
        assert metrics.peak_memory_usage < 500, \
            f"Memory usage too high: {metrics.peak_memory_usage:.1f} MB"
        assert metrics.avg_connection_time < 100, \
            f"Connection time too high: {metrics.avg_connection_time:.2f} ms"
        
        logger.info(f"100 Concurrent Connections Metrics:\n{metrics}")

    @pytest.mark.asyncio
    async def test_250_concurrent_connections(self):
        """Test 250 concurrent peer connections."""
        runner = LoadTestRunner(target_connections=250)
        metrics = await runner.run(batch_size=50)
        
        assert metrics.successful_connections >= 240, \
            f"Expected at least 240 successful connections, got {metrics.successful_connections}"
        assert metrics.peak_memory_usage < 1000, \
            f"Memory usage too high: {metrics.peak_memory_usage:.1f} MB"
        
        logger.info(f"250 Concurrent Connections Metrics:\n{metrics}")

    @pytest.mark.asyncio
    async def test_500_concurrent_connections(self):
        """Test 500 concurrent peer connections."""
        runner = LoadTestRunner(target_connections=500)
        metrics = await runner.run(batch_size=100)
        
        assert metrics.successful_connections >= 475, \
            f"Expected at least 475 successful connections, got {metrics.successful_connections}"
        assert metrics.peak_memory_usage < 2000, \
            f"Memory usage too high: {metrics.peak_memory_usage:.1f} MB"
        
        logger.info(f"500 Concurrent Connections Metrics:\n{metrics}")


class TestLoadWithRetry:
    """Load testing with connection retry logic."""

    @pytest.mark.asyncio
    async def test_100_connections_with_retry(self):
        """Test 100 concurrent connections with retry logic."""
        retry_config = RetryConfig(
            max_retries=2,
            initial_delay=0.01,
            backoff_multiplier=2.0,
            max_delay=0.5,
            jitter=0.1,
        )
        retry_manager = ConnectionRetryManager(retry_config)
        
        async def create_peer():
            """Create a single peer with retry."""
            start_time = time.time()
            
            async def operation():
                peer = PeerConnection(
                    local_did=f"did:peer:{uuid.uuid4()}",
                    remote_did=f"did:peer:{uuid.uuid4()}",
                )
                return peer
            
            peer = await retry_manager.execute_with_retry(operation)
            elapsed_ms = (time.time() - start_time) * 1000
            return peer, elapsed_ms
        
        # Create multiple peers with retry
        start_time = time.time()
        tasks = [create_peer() for _ in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_duration = time.time() - start_time
        
        # Validate results
        successful = 0
        connection_times = []
        for result in results:
            if isinstance(result, Exception):
                continue
            peer, elapsed_ms = result
            if peer is not None:
                successful += 1
                connection_times.append(elapsed_ms)
                peer.close()
        
        assert successful >= 95, f"Expected at least 95 successful connections, got {successful}"
        
        avg_time = sum(connection_times) / len(connection_times) if connection_times else 0
        logger.info(
            f"100 Connections with Retry:\n"
            f"  Successful: {successful}\n"
            f"  Total time: {total_duration:.2f}s\n"
            f"  Avg connection time: {avg_time:.2f}ms"
        )


class TestConnectionScaling:
    """Test connection creation scaling characteristics."""

    @pytest.mark.asyncio
    async def test_scaling_efficiency(self):
        """Test that connection creation time remains stable as concurrency increases."""
        batch_sizes = [50, 100, 150]
        times_per_connection = {}
        
        for batch_size in batch_sizes:
            runner = LoadTestRunner(target_connections=batch_size)
            metrics = await runner.run(batch_size=batch_size)
            
            times_per_connection[batch_size] = metrics.avg_connection_time
            logger.info(
                f"Batch size {batch_size}: "
                f"Avg connection time: {metrics.avg_connection_time:.2f}ms"
            )
        
        # Verify that time doesn't degrade significantly with higher concurrency
        # (allow 2x degradation as acceptable)
        assert times_per_connection[150] < times_per_connection[50] * 2, \
            f"Connection time degraded too much with concurrency: {times_per_connection}"


class TestResourceUsage:
    """Test resource usage patterns under load."""

    @pytest.mark.asyncio
    async def test_memory_scaling(self):
        """Test memory usage scales reasonably with connection count."""
        test_sizes = [100, 250]
        memory_per_connection = {}
        
        for size in test_sizes:
            runner = LoadTestRunner(target_connections=size)
            metrics = await runner.run(batch_size=50)
            
            if metrics.successful_connections > 0:
                mem_per_conn = metrics.peak_memory_usage / metrics.successful_connections
                memory_per_connection[size] = mem_per_conn
                logger.info(
                    f"Size {size}: "
                    f"Peak memory: {metrics.peak_memory_usage:.1f} MB, "
                    f"Per connection: {mem_per_conn:.2f} MB"
                )
        
        # Memory per connection should not increase dramatically
        if len(memory_per_connection) == 2:
            sizes = sorted(memory_per_connection.keys())
            ratio = memory_per_connection[sizes[1]] / memory_per_connection[sizes[0]]
            assert ratio < 1.5, f"Memory scaling too high: {ratio:.2f}x"

"""Tests for monitoring and metrics modules."""

import pytest
import asyncio

from aiconexus.monitoring.metrics import (
    MetricsCollector,
    MetricType,
    ConnectionMetrics,
    MessageMetrics,
    ErrorMetrics,
    RetryMetrics,
    get_collector,
    reset_collector,
)
from aiconexus.monitoring.health import (
    HealthChecker,
    HealthStatus,
    ComponentHealth,
    get_checker,
    reset_checker,
    check_memory,
    check_disk,
    check_network,
)


# =============================================================================
# Metrics Tests
# =============================================================================

class TestMetricsCollector:
    """Test metrics collector."""
    
    def setup_method(self):
        """Reset metrics before each test."""
        reset_collector()
    
    def test_register_metric(self):
        """Test registering a new metric."""
        collector = MetricsCollector()
        metric = collector.register_metric(
            "test_metric",
            "Test metric",
            MetricType.COUNTER
        )
        
        assert metric.name == "test_metric"
        assert metric.description == "Test metric"
        assert metric.metric_type == MetricType.COUNTER
    
    def test_record_metric(self):
        """Test recording metric values."""
        collector = MetricsCollector()
        collector.register_metric("test", "Test", MetricType.GAUGE)
        
        collector.record("test", 42.5)
        metric = collector.get_metric("test")
        
        assert len(metric.values) == 1
        values = list(metric.values.values())
        assert values[0].value == 42.5
    
    def test_record_metric_with_labels(self):
        """Test recording metrics with labels."""
        collector = MetricsCollector()
        collector.register_metric("test", "Test", MetricType.GAUGE)
        
        collector.record("test", 10.0, labels={"peer_id": "peer1"})
        collector.record("test", 20.0, labels={"peer_id": "peer2"})
        
        metric = collector.get_metric("test")
        assert len(metric.values) == 2
    
    def test_prometheus_export(self):
        """Test Prometheus format export."""
        collector = MetricsCollector()
        collector.register_metric("test", "Test metric", MetricType.GAUGE)
        collector.record("test", 42.0)
        
        export = collector.export_prometheus()
        
        assert "# HELP test Test metric" in export
        assert "# TYPE test gauge" in export
        assert "test 42.0" in export
    
    def test_uptime_seconds(self):
        """Test uptime calculation."""
        collector = MetricsCollector()
        uptime = collector.uptime_seconds()
        
        assert uptime >= 0
        assert isinstance(uptime, float)
    
    def test_get_all_metrics(self):
        """Test getting all metrics."""
        collector = MetricsCollector()
        metrics = collector.get_all_metrics()
        
        # Should have default metrics
        assert len(metrics) > 0
        assert "webrtc_peer_connections_total" in metrics


class TestConnectionMetrics:
    """Test connection metrics helper."""
    
    def test_connection_established(self):
        """Test recording connection establishment."""
        collector = MetricsCollector()
        conn_metrics = ConnectionMetrics(collector)
        
        conn_metrics.connection_started()
        conn_metrics.connection_established(0.5)
        
        metric = collector.get_metric("webrtc_connection_time_seconds")
        assert metric is not None
        assert len(metric.values) > 0
    
    def test_connection_closed(self):
        """Test recording connection closed."""
        collector = MetricsCollector()
        conn_metrics = ConnectionMetrics(collector)
        
        conn_metrics.connection_started()
        conn_metrics.connection_established(0.5)
        conn_metrics.connection_closed()
        
        metric = collector.get_metric("webrtc_peer_connections_active")
        assert metric is not None


class TestMessageMetrics:
    """Test message metrics helper."""
    
    def test_message_sent(self):
        """Test recording sent message."""
        collector = MetricsCollector()
        msg_metrics = MessageMetrics(collector)
        
        msg_metrics.message_sent(1024)
        
        sent_metric = collector.get_metric("webrtc_messages_sent_total")
        bytes_metric = collector.get_metric("webrtc_message_bytes_sent_total")
        
        assert sent_metric is not None
        assert bytes_metric is not None
    
    def test_message_received(self):
        """Test recording received message."""
        collector = MetricsCollector()
        msg_metrics = MessageMetrics(collector)
        
        msg_metrics.message_received(2048)
        
        received_metric = collector.get_metric("webrtc_messages_received_total")
        bytes_metric = collector.get_metric("webrtc_message_bytes_received_total")
        
        assert received_metric is not None
        assert bytes_metric is not None


class TestErrorMetrics:
    """Test error metrics helper."""
    
    def test_error_occurred(self):
        """Test recording errors."""
        collector = MetricsCollector()
        err_metrics = ErrorMetrics(collector)
        
        err_metrics.error_occurred("timeout")
        err_metrics.error_occurred("timeout")
        err_metrics.error_occurred("network")
        
        metric = collector.get_metric("webrtc_errors_total")
        assert len(metric.values) >= 2  # At least 2 different error types


class TestRetryMetrics:
    """Test retry metrics helper."""
    
    def test_retry_attempted(self):
        """Test recording retry attempts."""
        collector = MetricsCollector()
        retry_metrics = RetryMetrics(collector)
        
        retry_metrics.retry_attempted()
        retry_metrics.retry_attempted()
        
        metric = collector.get_metric("webrtc_connection_retries_total")
        assert len(metric.values) > 0
    
    def test_retry_success_rate(self):
        """Test retry success rate calculation."""
        collector = MetricsCollector()
        retry_metrics = RetryMetrics(collector)
        
        retry_metrics.retry_attempted()
        retry_metrics.retry_succeeded()
        retry_metrics.retry_attempted()
        # Second retry not succeeded, so 1/2 = 0.5
        
        metric = collector.get_metric("webrtc_retry_success_rate")
        assert metric is not None


# =============================================================================
# Health Check Tests
# =============================================================================

class TestHealthChecker:
    """Test health checker."""
    
    def setup_method(self):
        """Reset health checker before each test."""
        reset_checker()
    
    @pytest.mark.asyncio
    async def test_health_check_passing(self):
        """Test health check with passing components."""
        checker = HealthChecker()
        
        async def mock_check_pass():
            return HealthStatus.HEALTHY, "All good"
        
        checker.register_check("test", mock_check_pass)
        result = await checker.check_health()
        
        assert result.status == HealthStatus.HEALTHY
        assert result.checks_passed == 1
        assert result.checks_failed == 0
    
    @pytest.mark.asyncio
    async def test_health_check_failing(self):
        """Test health check with failing components."""
        checker = HealthChecker()
        
        async def mock_check_fail():
            return HealthStatus.UNHEALTHY, "Service down"
        
        checker.register_check("test", mock_check_fail)
        result = await checker.check_health()
        
        assert result.status == HealthStatus.UNHEALTHY
        assert result.checks_passed == 0
        assert result.checks_failed == 1
    
    @pytest.mark.asyncio
    async def test_health_check_degraded(self):
        """Test health check with degraded status."""
        checker = HealthChecker()
        
        async def check_good():
            return HealthStatus.HEALTHY, "OK"
        
        async def check_bad():
            return HealthStatus.UNHEALTHY, "Error"
        
        checker.register_check("good", check_good)
        checker.register_check("bad", check_bad)
        
        result = await checker.check_health()
        
        assert result.status == HealthStatus.DEGRADED
        assert result.checks_passed == 1
        assert result.checks_failed == 1
    
    @pytest.mark.asyncio
    async def test_health_check_exception(self):
        """Test health check handling exceptions."""
        checker = HealthChecker()
        
        async def mock_check_error():
            raise RuntimeError("Unexpected error")
        
        checker.register_check("error", mock_check_error)
        result = await checker.check_health()
        
        assert result.status == HealthStatus.UNHEALTHY
        assert result.checks_failed == 1
    
    @pytest.mark.asyncio
    async def test_health_check_timeout(self):
        """Test health check handling timeouts."""
        checker = HealthChecker()
        
        async def mock_check_slow():
            await asyncio.sleep(10)  # Longer than timeout
            return HealthStatus.HEALTHY, "OK"
        
        checker.register_check("slow", mock_check_slow)
        result = await checker.check_health()
        
        # Should timeout and be marked unhealthy
        assert result.checks_failed == 1
    
    @pytest.mark.asyncio
    async def test_component_health_tracking(self):
        """Test component health tracking."""
        checker = HealthChecker()
        
        async def mock_check():
            return HealthStatus.HEALTHY, "All good"
        
        checker.register_check("component", mock_check)
        
        result1 = await checker.check_health()
        result2 = await checker.check_health()
        
        component = result2.components["component"]
        assert component.check_count == 2
    
    @pytest.mark.asyncio
    async def test_health_result_to_dict(self):
        """Test converting health result to dictionary."""
        checker = HealthChecker()
        
        async def mock_check():
            return HealthStatus.HEALTHY, "OK"
        
        checker.register_check("test", mock_check)
        result = await checker.check_health()
        
        result_dict = result.to_dict()
        
        assert "status" in result_dict
        assert "timestamp" in result_dict
        assert "components" in result_dict
        assert "checks_passed" in result_dict


@pytest.mark.asyncio
async def test_check_memory():
    """Test memory health check."""
    status, message = await check_memory()
    
    assert status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY]
    assert isinstance(message, str)


@pytest.mark.asyncio
async def test_check_disk():
    """Test disk health check."""
    status, message = await check_disk()
    
    assert status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY]
    assert isinstance(message, str)


@pytest.mark.asyncio
async def test_check_network():
    """Test network health check."""
    status, message = await check_network()
    
    assert status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY]
    assert isinstance(message, str)


class TestGlobalInstances:
    """Test global singleton instances."""
    
    def test_get_collector(self):
        """Test getting global metrics collector."""
        reset_collector()
        
        collector1 = get_collector()
        collector2 = get_collector()
        
        # Should be same instance
        assert collector1 is collector2
    
    @pytest.mark.asyncio
    async def test_get_checker(self):
        """Test getting global health checker."""
        reset_checker()
        
        checker1 = get_checker()
        checker2 = get_checker()
        
        # Should be same instance
        assert checker1 is checker2
        
        # Should have default checks
        result = await checker1.check_health()
        assert len(result.components) >= 3  # memory, disk, network

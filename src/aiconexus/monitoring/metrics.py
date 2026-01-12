"""Metrics collection and Prometheus instrumentation for AIConexus.

Provides metrics for:
- Connection establishment time
- Message throughput
- WebRTC peer states
- Error rates and types
- System resource usage
"""

import time
import logging
from typing import Dict, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class MetricValue:
    """A single metric value with timestamp."""
    value: float
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class Metric:
    """Metric definition and values."""
    name: str
    description: str
    metric_type: MetricType
    values: Dict[str, MetricValue] = field(default_factory=dict)
    
    def record(self, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a metric value."""
        key = self._make_key(labels or {})
        self.values[key] = MetricValue(value=value, labels=labels or {})
    
    @staticmethod
    def _make_key(labels: Dict[str, str]) -> str:
        """Create a key from labels."""
        if not labels:
            return "no_labels"
        items = sorted(labels.items())
        return ",".join(f"{k}={v}" for k, v in items)


class MetricsCollector:
    """Collects and manages metrics for AIConexus."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: Dict[str, Metric] = {}
        self._start_time = time.time()
        self._register_default_metrics()
    
    def _register_default_metrics(self):
        """Register default metrics."""
        # Connection metrics
        self.register_metric(
            "webrtc_peer_connections_total",
            "Total number of peer connections established",
            MetricType.COUNTER
        )
        self.register_metric(
            "webrtc_peer_connections_active",
            "Currently active peer connections",
            MetricType.GAUGE
        )
        self.register_metric(
            "webrtc_connection_time_seconds",
            "Time taken to establish connection (seconds)",
            MetricType.HISTOGRAM
        )
        
        # Message metrics
        self.register_metric(
            "webrtc_messages_sent_total",
            "Total messages sent",
            MetricType.COUNTER
        )
        self.register_metric(
            "webrtc_messages_received_total",
            "Total messages received",
            MetricType.COUNTER
        )
        self.register_metric(
            "webrtc_message_bytes_sent_total",
            "Total bytes sent",
            MetricType.COUNTER
        )
        self.register_metric(
            "webrtc_message_bytes_received_total",
            "Total bytes received",
            MetricType.COUNTER
        )
        
        # State metrics
        self.register_metric(
            "webrtc_peer_state",
            "Current state of peer connections",
            MetricType.GAUGE
        )
        
        # Error metrics
        self.register_metric(
            "webrtc_errors_total",
            "Total errors encountered",
            MetricType.COUNTER
        )
        self.register_metric(
            "webrtc_error_rate",
            "Error rate per minute",
            MetricType.GAUGE
        )
        
        # Retry metrics
        self.register_metric(
            "webrtc_connection_retries_total",
            "Total connection retry attempts",
            MetricType.COUNTER
        )
        self.register_metric(
            "webrtc_retry_success_rate",
            "Success rate of retry attempts",
            MetricType.GAUGE
        )
    
    def register_metric(
        self,
        name: str,
        description: str,
        metric_type: MetricType
    ) -> Metric:
        """Register a new metric.
        
        Args:
            name: Metric name
            description: Human-readable description
            metric_type: Type of metric
            
        Returns:
            Registered Metric object
        """
        metric = Metric(name, description, metric_type)
        self.metrics[name] = metric
        logger.debug(f"Registered metric: {name}")
        return metric
    
    def record(
        self,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """Record a metric value.
        
        Args:
            metric_name: Name of the metric
            value: Value to record
            labels: Optional labels for the metric
        """
        if metric_name not in self.metrics:
            logger.warning(f"Unknown metric: {metric_name}")
            return
        
        self.metrics[metric_name].record(value, labels)
    
    def get_metric(self, metric_name: str) -> Optional[Metric]:
        """Get a metric by name.
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            Metric object or None if not found
        """
        return self.metrics.get(metric_name)
    
    def get_all_metrics(self) -> Dict[str, Metric]:
        """Get all registered metrics.
        
        Returns:
            Dictionary of all metrics
        """
        return self.metrics.copy()
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus text format.
        
        Returns:
            Metrics in Prometheus format
        """
        lines = []
        
        for metric_name, metric in sorted(self.metrics.items()):
            # Add HELP and TYPE lines
            lines.append(f"# HELP {metric_name} {metric.description}")
            lines.append(f"# TYPE {metric_name} {metric.metric_type.value}")
            
            # Add metric values
            for value in metric.values.values():
                labels_str = ""
                if value.labels:
                    label_parts = [f'{k}="{v}"' for k, v in sorted(value.labels.items())]
                    labels_str = "{" + ",".join(label_parts) + "}"
                
                line = f"{metric_name}{labels_str} {value.value}"
                lines.append(line)
            
            lines.append("")
        
        return "\n".join(lines)
    
    def uptime_seconds(self) -> float:
        """Get uptime in seconds.
        
        Returns:
            Uptime in seconds
        """
        return time.time() - self._start_time


class ConnectionMetrics:
    """Helper class for recording connection-related metrics."""
    
    def __init__(self, collector: MetricsCollector):
        """Initialize connection metrics helper.
        
        Args:
            collector: MetricsCollector instance
        """
        self.collector = collector
        self._active_connections = 0
        self._total_connections = 0
    
    def connection_started(self):
        """Record start of connection attempt."""
        self._active_connections += 1
    
    def connection_established(self, duration_seconds: float):
        """Record successful connection establishment.
        
        Args:
            duration_seconds: Time taken to establish connection
        """
        self.collector.record(
            "webrtc_connection_time_seconds",
            duration_seconds
        )
        self._total_connections += 1
        self.collector.record(
            "webrtc_peer_connections_total",
            float(self._total_connections)
        )
        self.collector.record(
            "webrtc_peer_connections_active",
            float(self._active_connections)
        )
    
    def connection_failed(self):
        """Record failed connection."""
        self._active_connections = max(0, self._active_connections - 1)
        self.collector.record(
            "webrtc_peer_connections_active",
            self._active_connections
        )
    
    def connection_closed(self):
        """Record closed connection."""
        self._active_connections = max(0, self._active_connections - 1)
        self.collector.record(
            "webrtc_peer_connections_active",
            self._active_connections
        )


class MessageMetrics:
    """Helper class for recording message-related metrics."""
    
    def __init__(self, collector: MetricsCollector):
        """Initialize message metrics helper.
        
        Args:
            collector: MetricsCollector instance
        """
        self.collector = collector
    
    def message_sent(self, size_bytes: int):
        """Record sent message.
        
        Args:
            size_bytes: Size of message in bytes
        """
        self.collector.record("webrtc_messages_sent_total", 1)
        self.collector.record("webrtc_message_bytes_sent_total", float(size_bytes))
    
    def message_received(self, size_bytes: int):
        """Record received message.
        
        Args:
            size_bytes: Size of message in bytes
        """
        self.collector.record("webrtc_messages_received_total", 1)
        self.collector.record("webrtc_message_bytes_received_total", float(size_bytes))


class ErrorMetrics:
    """Helper class for recording error-related metrics."""
    
    def __init__(self, collector: MetricsCollector):
        """Initialize error metrics helper.
        
        Args:
            collector: MetricsCollector instance
        """
        self.collector = collector
        self._error_count = 0
        self._last_minute_errors = 0
        self._last_minute_reset = time.time()
    
    def error_occurred(self, error_type: str = "unknown"):
        """Record error occurrence.
        
        Args:
            error_type: Type of error
        """
        self._error_count += 1
        self._last_minute_errors += 1
        
        self.collector.record(
            "webrtc_errors_total",
            float(self._error_count),
            labels={"error_type": error_type}
        )
    
    def update_error_rate(self):
        """Update error rate metric."""
        current_time = time.time()
        if current_time - self._last_minute_reset >= 60:
            error_rate = self._last_minute_errors / 60.0
            self.collector.record("webrtc_error_rate", error_rate)
            self._last_minute_errors = 0
            self._last_minute_reset = current_time


class RetryMetrics:
    """Helper class for recording retry-related metrics."""
    
    def __init__(self, collector: MetricsCollector):
        """Initialize retry metrics helper.
        
        Args:
            collector: MetricsCollector instance
        """
        self.collector = collector
        self._total_retries = 0
        self._successful_retries = 0
    
    def retry_attempted(self):
        """Record retry attempt."""
        self._total_retries += 1
        self.collector.record(
            "webrtc_connection_retries_total",
            float(self._total_retries)
        )
    
    def retry_succeeded(self):
        """Record successful retry."""
        self._successful_retries += 1
        self._update_success_rate()
    
    def _update_success_rate(self):
        """Update retry success rate."""
        if self._total_retries > 0:
            success_rate = self._successful_retries / self._total_retries
            self.collector.record("webrtc_retry_success_rate", success_rate)


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_collector() -> MetricsCollector:
    """Get or create global metrics collector.
    
    Returns:
        Global MetricsCollector instance
    """
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
        logger.info("Initialized global metrics collector")
    return _metrics_collector


def reset_collector():
    """Reset global metrics collector (for testing)."""
    global _metrics_collector
    _metrics_collector = None

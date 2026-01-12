"""Health check and liveness probe implementation.

Provides health check endpoints and diagnostics for AIConexus.
"""

import logging
import asyncio
from typing import Dict, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status values."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ComponentHealth:
    """Health status of a single component."""
    name: str
    status: HealthStatus
    message: str = ""
    last_check: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    check_count: int = 0


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    status: HealthStatus
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    uptime_seconds: float = 0.0
    components: Dict[str, ComponentHealth] = field(default_factory=dict)
    checks_passed: int = 0
    checks_failed: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "timestamp": self.timestamp,
            "uptime_seconds": self.uptime_seconds,
            "components": {
                name: {
                    "status": comp.status.value,
                    "message": comp.message,
                    "last_check": comp.last_check,
                    "check_count": comp.check_count,
                }
                for name, comp in self.components.items()
            },
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
        }


class HealthChecker:
    """Performs health checks on system components."""
    
    def __init__(self):
        """Initialize health checker."""
        self._checks: Dict[str, callable] = {}
        self._component_health: Dict[str, ComponentHealth] = {}
        self._start_time = datetime.utcnow()
    
    def register_check(self, name: str, check_fn: callable):
        """Register a health check function.
        
        Args:
            name: Name of the component
            check_fn: Async function that returns (status, message)
        """
        self._checks[name] = check_fn
        self._component_health[name] = ComponentHealth(
            name=name,
            status=HealthStatus.HEALTHY,
            message="Not yet checked"
        )
        logger.debug(f"Registered health check: {name}")
    
    async def check_health(self) -> HealthCheckResult:
        """Perform all health checks.
        
        Returns:
            HealthCheckResult with status and component details
        """
        checks_passed = 0
        checks_failed = 0
        
        # Run all checks concurrently
        check_tasks = [
            self._run_check(name, check_fn)
            for name, check_fn in self._checks.items()
        ]
        
        results = await asyncio.gather(*check_tasks, return_exceptions=True)
        
        # Process results
        for i, (name, check_fn) in enumerate(self._checks.items()):
            result = results[i]
            
            if isinstance(result, Exception):
                status = HealthStatus.UNHEALTHY
                message = f"Check failed with error: {str(result)}"
                checks_failed += 1
            else:
                status, message = result
                if status == HealthStatus.HEALTHY:
                    checks_passed += 1
                else:
                    checks_failed += 1
            
            # Update component health
            component = self._component_health[name]
            component.status = status
            component.message = message
            component.last_check = datetime.utcnow().isoformat()
            component.check_count += 1
        
        # Determine overall status
        if checks_failed == 0:
            overall_status = HealthStatus.HEALTHY
        elif checks_failed <= len(self._checks) // 2:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.UNHEALTHY
        
        # Calculate uptime
        uptime = (datetime.utcnow() - self._start_time).total_seconds()
        
        return HealthCheckResult(
            status=overall_status,
            uptime_seconds=uptime,
            components=self._component_health.copy(),
            checks_passed=checks_passed,
            checks_failed=checks_failed,
        )
    
    async def _run_check(
        self,
        name: str,
        check_fn: callable
    ) -> tuple[HealthStatus, str]:
        """Run a single health check with timeout.
        
        Args:
            name: Component name
            check_fn: Check function
            
        Returns:
            Tuple of (status, message)
        """
        try:
            result = await asyncio.wait_for(check_fn(), timeout=5.0)
            
            if isinstance(result, tuple):
                return result
            elif isinstance(result, bool):
                return (
                    HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY,
                    "Check " + ("passed" if result else "failed")
                )
            else:
                return HealthStatus.UNHEALTHY, f"Invalid check result: {result}"
        
        except asyncio.TimeoutError:
            logger.warning(f"Health check timeout for {name}")
            return HealthStatus.UNHEALTHY, "Check timed out"
        except Exception as e:
            logger.error(f"Health check error for {name}: {e}")
            return HealthStatus.UNHEALTHY, f"Check error: {str(e)}"


# Default health checks
async def check_memory() -> tuple[HealthStatus, str]:
    """Check available memory."""
    try:
        import psutil
        memory = psutil.virtual_memory()
        percent = memory.percent
        
        if percent > 90:
            return HealthStatus.UNHEALTHY, f"Memory usage critical: {percent}%"
        elif percent > 75:
            return HealthStatus.DEGRADED, f"Memory usage high: {percent}%"
        else:
            return HealthStatus.HEALTHY, f"Memory usage normal: {percent}%"
    except Exception as e:
        return HealthStatus.DEGRADED, f"Could not check memory: {e}"


async def check_disk() -> tuple[HealthStatus, str]:
    """Check available disk space."""
    try:
        import psutil
        disk = psutil.disk_usage('/')
        percent = disk.percent
        
        if percent > 95:
            return HealthStatus.UNHEALTHY, f"Disk usage critical: {percent}%"
        elif percent > 85:
            return HealthStatus.DEGRADED, f"Disk usage high: {percent}%"
        else:
            return HealthStatus.HEALTHY, f"Disk usage normal: {percent}%"
    except Exception as e:
        return HealthStatus.DEGRADED, f"Could not check disk: {e}"


async def check_network() -> tuple[HealthStatus, str]:
    """Check network connectivity."""
    try:
        import socket
        socket.create_connection(("1.1.1.1", 80), timeout=2)
        return HealthStatus.HEALTHY, "Network connectivity OK"
    except socket.timeout:
        return HealthStatus.DEGRADED, "Network timeout"
    except socket.error:
        return HealthStatus.UNHEALTHY, "Network unreachable"
    except Exception as e:
        return HealthStatus.DEGRADED, f"Network check error: {e}"


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_checker() -> HealthChecker:
    """Get or create global health checker.
    
    Returns:
        Global HealthChecker instance
    """
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
        
        # Register default checks
        _health_checker.register_check("memory", check_memory)
        _health_checker.register_check("disk", check_disk)
        _health_checker.register_check("network", check_network)
        
        logger.info("Initialized global health checker")
    return _health_checker


def reset_checker():
    """Reset global health checker (for testing)."""
    global _health_checker
    _health_checker = None

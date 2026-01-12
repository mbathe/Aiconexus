"""Pytest configuration and fixtures"""

import pytest
from aiconexus.config import Settings


@pytest.fixture(scope="session")
def test_settings():
    """Provide test settings"""
    return Settings(
        environment="test",
        debug=True,
        database_url="postgresql://aiconexus:aiconexus@localhost:5432/aiconexus_test",
        redis_url="redis://localhost:6379/1",
    )


@pytest.fixture(scope="function")
def settings(test_settings):
    """Provide settings for each test"""
    return test_settings


@pytest.fixture
def sample_agent_id():
    """Provide a sample agent UUID for tests"""
    from uuid import uuid4

    return uuid4()


@pytest.fixture
def sample_capability_spec():
    """Provide a sample capability specification"""
    return {
        "capability_id": "test_capability",
        "name": "Test Capability",
        "description": "A capability for testing",
        "version": "1.0",
        "input_schema": {"type": "object", "properties": {"input": {"type": "string"}}},
        "output_schema": {"type": "object", "properties": {"output": {"type": "string"}}},
        "sla": {"latency_ms": 100, "availability_percent": 99.9, "timeout_ms": 5000},
        "pricing": {
            "model_type": "per_call",
            "base_cost": "0.001",
            "unit": "call",
            "currency": "AIC",
        },
    }

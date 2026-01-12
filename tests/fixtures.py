"""Test utilities and helpers"""

from uuid import UUID

import pytest


def create_test_agent_id() -> UUID:
    """Create a test agent ID"""
    from uuid import uuid4

    return uuid4()


def create_test_contract(requester_id: UUID, provider_id: UUID, capability_id: str):
    """Create a test contract"""
    from datetime import datetime, timedelta

    from aiconexus.core.contract import Contract

    return Contract(
        requester_id=requester_id,
        provider_id=provider_id,
        capability_id=capability_id,
        terms={
            "sla": {"latency_ms": 100, "availability_percent": 99.9},
            "pricing": {"base_cost": 0.001, "currency": "AIC"},
        },
        status="PENDING",
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )

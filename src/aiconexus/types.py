"""Core type definitions for AIConexus"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SLATerms(BaseModel):
    """Service Level Agreement specifications"""

    latency_ms: int = Field(ge=0, description="Maximum latency in milliseconds")
    availability_percent: float = Field(ge=0, le=100, description="Required availability %")
    timeout_ms: int = Field(ge=0, description="Operation timeout in milliseconds")
    retry_count: int = Field(ge=0, le=10, description="Number of retry attempts")


class PricingModel(BaseModel):
    """Pricing model for a capability"""

    model_type: str = Field(description="per_call, per_unit, subscription, dynamic")
    base_cost: Decimal = Field(ge=0, description="Base cost per unit")
    unit: str = Field(description="Unit of measurement (call, minute, KB, etc)")
    currency: str = Field(default="AIC", description="Currency code")
    dynamic_pricing: Optional[Dict[str, Any]] = Field(
        default=None, description="Parameters for dynamic pricing"
    )


class Budget(BaseModel):
    """Agent budget allocation"""

    agent_id: UUID
    currency: str = "AIC"
    total_allocated: Decimal = Field(ge=0)
    consumed: Decimal = Field(ge=0, default=0)
    period: str = Field(description="monthly, yearly, unlimited")
    reset_date: Optional[datetime] = None

    @property
    def available(self) -> Decimal:
        """Available budget remaining"""
        return self.total_allocated - self.consumed

    def can_afford(self, amount: Decimal) -> bool:
        """Check if budget can afford amount"""
        return self.available >= amount


class ReputationScore(BaseModel):
    """Agent reputation metrics"""

    agent_id: UUID
    overall_score: float = Field(ge=0, le=5, default=5.0)
    total_calls: int = Field(ge=0, default=0)
    successful_calls: int = Field(ge=0, default=0)
    failed_calls: int = Field(ge=0, default=0)
    avg_latency_ms: float = Field(ge=0, default=0)
    uptime_percent: float = Field(ge=0, le=100, default=100)
    response_quality_avg: float = Field(ge=0, le=1, default=1.0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    @property
    def success_rate(self) -> float:
        """Percentage of successful calls"""
        if self.total_calls == 0:
            return 100.0
        return (self.successful_calls / self.total_calls) * 100


class Endpoint(BaseModel):
    """Network endpoint for an agent"""

    protocol: str = Field(description="http, ws, grpc, etc")
    url: str = Field(description="Full endpoint URL")
    authenticated: bool = Field(default=False)
    rate_limit_rps: Optional[int] = Field(default=None, description="Requests per second")


class AgentInfo(BaseModel):
    """Public information about an agent"""

    agent_id: UUID
    name: str
    description: str
    owner_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    status: str = "OFFLINE"
    version: str = "1.0"
    tags: List[str] = []


class CapabilitySpec(BaseModel):
    """Specification of a capability offered by agent"""

    capability_id: str
    name: str
    description: str
    version: str
    input_schema: Dict[str, Any] = Field(description="JSON Schema for inputs")
    output_schema: Dict[str, Any] = Field(description="JSON Schema for outputs")
    sla: SLATerms
    pricing: PricingModel
    tags: List[str] = []
    requires_authentication: bool = False


class ContractTerms(BaseModel):
    """Terms of a contract between agents"""

    sla: SLATerms
    pricing: PricingModel
    payment_method: str = Field(description="immediate, delayed, batch")
    refund_policy: str = Field(default="none", description="none, partial, full")
    dispute_resolution: str = Field(default="third_party", description="How to resolve disputes")


class MessageSignature(BaseModel):
    """Message signature and verification"""

    algorithm: str = Field(default="SHA-256")
    signature: str = Field(description="Hex-encoded signature")
    public_key: Optional[str] = Field(default=None, description="Signer public key")


class ExecutionResult(BaseModel):
    """Result of a capability execution"""

    execution_id: UUID
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: int = Field(ge=0)
    cost_actual: Decimal
    timestamp: datetime


class TransactionRecord(BaseModel):
    """Economic transaction record"""

    transaction_id: UUID
    timestamp: datetime
    from_agent_id: UUID
    to_agent_id: UUID
    amount: Decimal
    currency: str
    execution_id: UUID
    description: str
    status: str  # pending, settled, failed
    settlement_timestamp: Optional[datetime] = None

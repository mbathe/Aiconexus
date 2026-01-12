"""Contract management for AIConexus"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel


class Contract(BaseModel):
    """Agreement between agents for capability execution"""

    contract_id: UUID = None
    requester_id: UUID
    provider_id: UUID
    capability_id: str
    terms: Dict[str, Any]
    status: str = "PENDING"
    created_at: datetime = None
    expires_at: datetime = None
    signed_at: Optional[datetime] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.contract_id is None:
            self.contract_id = uuid4()
        if self.created_at is None:
            self.created_at = datetime.utcnow()

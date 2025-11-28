from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LeadBase(BaseModel):
    external_id: str
    phone: Optional[str] = None
    email: Optional[str] = None


class LeadResponse(LeadBase):
    id: int
    created_at: datetime
    tickets_count: int = 0

    model_config = {'from_attributes': True}
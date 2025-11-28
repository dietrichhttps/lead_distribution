from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.lead import LeadResponse
from app.schemas.operator import OperatorResponse
from app.schemas.source import SourceResponse


class TicketCreate(BaseModel):
    lead_external_id: str
    source_id: int
    phone: Optional[str] = None
    email: Optional[str] = None


class TicketResponse(BaseModel):
    id: int
    lead_id: int
    source_id: int
    operator_id: Optional[int]
    created_at: datetime
    status: str
    lead: LeadResponse
    source: SourceResponse
    operator: Optional[OperatorResponse] = None

    model_config = {'from_attributes': True}
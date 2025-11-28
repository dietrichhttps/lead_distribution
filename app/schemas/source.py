from pydantic import BaseModel


class SourceBase(BaseModel):
    name: str


class SourceResponse(SourceBase):
    id: int

    model_config = {'from_attributes': True}


class SourceOperatorAssignment(BaseModel):
    operator_id: int
    weight: int = 10
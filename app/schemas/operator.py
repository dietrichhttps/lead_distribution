from pydantic import BaseModel


class OperatorBase(BaseModel):
    name: str
    is_active: bool = True
    max_load: int = 5


class OperatorResponse(OperatorBase):
    id: int
    current_load: int = 0

    model_config = {'from_attributes': True}
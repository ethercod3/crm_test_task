from pydantic import BaseModel
from typing import Optional


class OperatorCreate(BaseModel):
    name: str
    active: bool = True
    load_limit: int = 10


class OperatorUpdate(BaseModel):
    active: Optional[bool] = None
    load_limit: Optional[int] = None


class SourceCreate(BaseModel):
    name: str


class WeightConfig(BaseModel):
    operator_id: int
    weight: int


class SourceWeightConfig(BaseModel):
    source_id: int
    weights: list[WeightConfig]


class ContactCreate(BaseModel):
    lead_external_id: str
    lead_name: Optional[str] = None
    source_id: int


class OperatorResponse(BaseModel):
    id: int
    name: str
    active: bool
    load_limit: int
    current_load: int

    class Config:
        from_attributes = True


class ContactResponse(BaseModel):
    id: int
    lead_id: int
    source_id: int
    operator_id: Optional[int]
    status: str

    class Config:
        from_attributes = True


class LeadResponse(BaseModel):
    id: int
    external_id: str
    name: Optional[str]
    contacts_count: int

    class Config:
        from_attributes = True

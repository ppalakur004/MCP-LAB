from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Decision(StrEnum):
    APPROVED = "approved"
    DENIED = "denied"
    ESCALATED = "escalated"


class EquipmentRecord(BaseModel):
    asset_id: str
    item: str
    issued_date: date
    status: str = "active"


class Employee(BaseModel):
    employee_id: str
    name: str
    role: str
    hire_date: date
    equipment: list[EquipmentRecord] = Field(default_factory=list)


class ItemPolicy(BaseModel):
    maximum_quantity: int = Field(ge=0)
    replacement_years: int = Field(ge=0)


class RolePolicy(BaseModel):
    role: str
    equipment: dict[str, ItemPolicy]


class EligibilityResult(BaseModel):
    decision: Decision
    employee_id: str
    item: str
    reason: str
    policy_source: str | None = None


class ReviewRecord(BaseModel):
    review_id: str
    request_id: str
    employee_id: str
    request: str
    reason: str
    status: str = "pending"
    created_at: datetime


class TraceStep(BaseModel):
    step: int
    reason: str
    tool: str
    arguments: dict[str, object]
    observation: dict[str, object]


class AgentResult(BaseModel):
    decision: Decision
    response: str
    trace: list[TraceStep]
    reflection: str

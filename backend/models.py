from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class Lead(BaseModel):
    company: str = Field(min_length=2, max_length=120)
    contact_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    employees: int | None = Field(default=None, ge=1, le=1_000_000)
    message: str = Field(min_length=10, max_length=3000)


class LeadAnalysis(BaseModel):
    company: str
    category: str
    priority: Literal["LOW", "MEDIUM", "HIGH"]
    budget_eur: int | None
    need: str
    summary: str
    suggested_action: str

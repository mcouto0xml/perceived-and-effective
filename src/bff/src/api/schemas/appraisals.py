"""Pydantic schemas for appraisal routes."""

from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field


class SendAppraisalRequest(BaseModel):
    user_id: UUID
    task_id: UUID
    perceived: int = Field(..., ge=0, le=10)
    explanation: Optional[str] = None


class SendAppraisalResponse(BaseModel):
    id: UUID
    user_id: UUID
    task_id: UUID
    perceived: int
    explanation: Optional[str] = None

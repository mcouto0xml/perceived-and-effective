"""Schemas for the /appraisal route."""

from uuid import UUID

from pydantic import BaseModel


class AppraisalRequest(BaseModel):
    task_id: UUID
    name: str
    description: str | None = None


class AppraisalResponse(BaseModel):
    effective_value: int
    explanation: str

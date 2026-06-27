"""Schemas for the /recommendation route."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class RecommendationRequest(BaseModel):
    task_id: Optional[UUID] = None
    effective: int
    effective_explanation: Optional[str] = None
    perceived: int
    perceived_explanation: Optional[str] = None
    description: Optional[str] = None
    name: str


class RecommendationResponse(BaseModel):
    recommendation: str
    task_id: Optional[UUID] = None

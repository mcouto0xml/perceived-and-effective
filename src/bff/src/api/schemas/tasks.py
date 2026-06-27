"""Pydantic schemas for task routes."""

from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class TaskResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    url: Optional[str] = None


class TaskEffectiveResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    effective: Optional[int] = None
    explanation: Optional[str] = None

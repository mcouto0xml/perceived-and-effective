"""Pydantic schemas for the send appraisal routes."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class SendAppraisalRequest(BaseModel):
    pass


class SendAppraisalResponse(BaseModel):
    pass
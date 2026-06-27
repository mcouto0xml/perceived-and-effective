"""Appraisal model"""

import uuid

from sqlalchemy import Integer, Column, ForeingKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.data.models.base import Base, TimestampMixin

class Appraisals(Base, TimestampMixin):
    """A task appraisal comming from a user"""

    __table_name__ = "appraisals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    perceived = Column(Integer, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeingKey("user.id"), nullable=True)
    task_id = Column(UUID(as_uuid=True), ForeingKey("task.id"), nullable=False)

    user = relationship("Users", back_populates="appraisals")
    task = relationship("Tasks", back_populates="appraisals")
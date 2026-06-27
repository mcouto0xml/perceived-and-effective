"""Appraisal model"""

import uuid

from sqlalchemy import Integer, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.data.models.base import Base, TimestampMixin


class Appraisals(Base, TimestampMixin):
    """A task appraisal submitted by a user"""

    __tablename__ = "appraisals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    perceived = Column(Integer, nullable=False)
    explanation = Column(String, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)

    user = relationship("Users", back_populates="appraisals")
    task = relationship("Tasks", back_populates="appraisals")
    recommendation = relationship("Recommendations", back_populates="appraisal", uselist=False)

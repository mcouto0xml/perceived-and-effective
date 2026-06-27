"""Recommendation model"""

import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.data.models.base import Base, TimestampMixin


class Recommendations(Base, TimestampMixin):
    """A recommendation generated when perceived vs effective diverges by more than 4"""

    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    value = Column(String, nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    appraisal_id = Column(UUID(as_uuid=True), ForeignKey("appraisals.id"), nullable=False, unique=True)

    task = relationship("Tasks", back_populates="recommendations")
    appraisal = relationship("Appraisals", back_populates="recommendation")

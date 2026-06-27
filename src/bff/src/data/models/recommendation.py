"""Recommendation model"""

import uuid

from sqlalchemy import Integer, Column, ForeingKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.data.models.base import Base, TimestampMixin

class Recommendations(Base, TimestampMixin):
    """A recommendation for a non-manager user"""

    __table_name__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    value = Column(String, nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeingKey("task.id"), nullable=False)
    

    task = relationship("Tasks", back_populates="recommendations")
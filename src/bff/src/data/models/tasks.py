"""Tasks model"""

import uuid

from sqlalchemy import Integer, Column, ForeingKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.data.models.base import Base, TimestampMixin

class Tasks(Base, TimestampMixin):
    """A single task from some project"""

    __table_name__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    effective = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    url = Column(String, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeingKey("user.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeingKey("project.id"), nullable=False)

    user_id = relationship("Users", back_populates="tasks")
    project = relationship("Projects", back_populates="tasks")
"""Tasks model"""

import uuid

from sqlalchemy import Integer, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.data.models.base import Base, TimestampMixin


class Tasks(Base, TimestampMixin):
    """A single task synced from GitLab"""

    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gitlab_issue_id = Column(Integer, nullable=False, unique=True)
    gitlab_project_id = Column(Integer, nullable=False)
    gitlab_iid = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    url = Column(String, nullable=True)
    effective = Column(Integer, nullable=True)
    explanation = Column(String, nullable=True)

    appraisals = relationship("Appraisals", back_populates="task")
    recommendations = relationship("Recommendations", back_populates="task")

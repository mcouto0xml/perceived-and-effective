"""Project model"""

import uuid

from sqlalchemy import Integer, Column, ForeingKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.data.models.base import Base, TimestampMixin

class Projects(Base, TimestampMixin):
    """A GitLab project"""

    __table_name__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    url = Column(String, nullable=False)
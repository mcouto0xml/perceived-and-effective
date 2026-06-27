"""User model"""

import uuid

from sqlalchemy import String, Column, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.data.models.base import Base, TimestampMixin

class Users(Base, TimestampMixin):
    """A user that is using the plataform"""

    __table_name__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=True)
    password = Column(String, nullable=True)
    is_manager = Column(Boolean, nullable=False)
    
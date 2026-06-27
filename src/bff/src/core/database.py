"""SQLAlchemy engine and session factory."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.data.models.base import Base

# Import all models so SQLAlchemy registers them before create_all
import src.data.models.users  # noqa: F401
import src.data.models.tasks  # noqa: F401
import src.data.models.appraisals  # noqa: F401
import src.data.models.recommendation  # noqa: F401

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

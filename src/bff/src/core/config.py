"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/perceived_and_effective"

    gitlab_url: str = "https://gitlab.com"
    gitlab_token: str = ""
    gitlab_project_id: int = 0

    effective_agent_url: str = "http://localhost:8001/effective"
    recommendation_agent_url: str = "http://localhost:8002/recommendation"

    poll_interval_minutes: int = 1

    class Config:
        env_file = ".env"


settings = Settings()

"""ADK agent that generates a recommendation when perceived and effective diverge."""

import uuid as uuid_module

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel

from src.core.config import settings
from src.prompts import RECOMMENDATION_AGENT_SYSTEM_PROMPT
from src.schemas.recommendation import RecommendationRequest

_APP_NAME = "recommendation-agent"


class _RecommendationOutput(BaseModel):
    recommendation: str


_session_service = InMemorySessionService()

_agent = LlmAgent(
    name="recommendation_agent",
    model=settings.gemini_model,
    instruction=RECOMMENDATION_AGENT_SYSTEM_PROMPT,
    output_schema=_RecommendationOutput,
    output_key="result",
)
_runner = Runner(
    agent=_agent,
    app_name=_APP_NAME,
    session_service=_session_service,
)


async def run_recommendation_agent(req: RecommendationRequest) -> str:
    """Call the recommendation agent and return the recommendation text."""
    message = (
        f"Task: {req.name}\n"
        f"Description: {req.description or ''}\n\n"
        f"Effective value: {req.effective}\n"
        f"Effective explanation: {req.effective_explanation or ''}\n\n"
        f"Perceived value: {req.perceived}\n"
        f"Perceived explanation: {req.perceived_explanation or ''}"
    )

    session_id = str(uuid_module.uuid4())

    await _session_service.create_session(
        app_name=_APP_NAME,
        user_id="system",
        session_id=session_id,
    )

    async for _ in _runner.run_async(
        user_id="system",
        session_id=session_id,
        new_message=types.Content(role="user", parts=[types.Part(text=message)]),
    ):
        pass

    session = await _session_service.get_session(
        app_name=_APP_NAME,
        user_id="system",
        session_id=session_id,
    )

    if session is None or "result" not in session.state:
        raise RuntimeError("Recommendation agent did not return a structured result")

    output = _RecommendationOutput.model_validate(session.state["result"])
    return output.recommendation

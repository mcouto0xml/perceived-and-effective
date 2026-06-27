"""
Two independent ADK agents that evaluate the effective value of a task.

Their numeric scores are averaged and their explanations are joined as two
separate paragraphs in the final response.
"""

import asyncio
import logging
import uuid as uuid_module

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel

from src.core.config import settings
from src.prompts import EFFECTIVE_AGENT_A_SYSTEM_PROMPT, EFFECTIVE_AGENT_B_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_APP_NAME = "effective-agents"
_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 60.0


class _EffectiveOutput(BaseModel):
    effective_value: int
    explanation: str


_session_service = InMemorySessionService()

_agent_a = LlmAgent(
    name="effective_agent_a",
    model=settings.gemini_model,
    instruction=EFFECTIVE_AGENT_A_SYSTEM_PROMPT,
    output_schema=_EffectiveOutput,
    output_key="result",
)
_runner_a = Runner(
    agent=_agent_a,
    app_name=_APP_NAME,
    session_service=_session_service,
)

_agent_b = LlmAgent(
    name="effective_agent_b",
    model=settings.gemini_model,
    instruction=EFFECTIVE_AGENT_B_SYSTEM_PROMPT,
    output_schema=_EffectiveOutput,
    output_key="result",
)
_runner_b = Runner(
    agent=_agent_b,
    app_name=_APP_NAME,
    session_service=_session_service,
)


async def _run(runner: Runner, message: str) -> _EffectiveOutput:
    for attempt in range(_MAX_RETRIES):
        session_id = str(uuid_module.uuid4())

        await _session_service.create_session(
            app_name=_APP_NAME,
            user_id="system",
            session_id=session_id,
        )

        try:
            async for _ in runner.run_async(
                user_id="system",
                session_id=session_id,
                new_message=types.Content(role="user", parts=[types.Part(text=message)]),
            ):
                pass
        except Exception as exc:
            if "429" in str(exc) and attempt < _MAX_RETRIES - 1:
                delay = _RETRY_BASE_DELAY * (2**attempt)
                logger.warning("Rate limited (429), retrying in %.0fs (attempt %d/%d)", delay, attempt + 1, _MAX_RETRIES)
                await asyncio.sleep(delay)
                continue
            raise

        session = await _session_service.get_session(
            app_name=_APP_NAME,
            user_id="system",
            session_id=session_id,
        )

        if session is None or "result" not in session.state:
            raise RuntimeError("Effective agent did not return a structured result")

        return _EffectiveOutput.model_validate(session.state["result"])

    raise RuntimeError("Effective agent exhausted all retries")


async def run_effective_agents(task_id: str, name: str, description: str | None) -> _EffectiveOutput:
    """Run both effective agents sequentially and merge their outputs."""
    message = f"Task ID: {task_id}\nName: {name}\nDescription: {description or ''}"

    result_a = await _run(_runner_a, message)
    await asyncio.sleep(10)
    result_b = await _run(_runner_b, message)

    avg_value = round((result_a.effective_value + result_b.effective_value) / 2)
    combined_explanation = f"{result_a.explanation}\n\n{result_b.explanation}"

    return _EffectiveOutput(effective_value=avg_value, explanation=combined_explanation)

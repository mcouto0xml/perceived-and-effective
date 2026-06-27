"""
Two independent ADK agents that evaluate the effective value of a task.

Their numeric scores are averaged and their explanations are joined as two
separate paragraphs in the final response.
"""

import asyncio
import uuid as uuid_module

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel

from src.core.config import settings
from src.prompts import EFFECTIVE_AGENT_A_SYSTEM_PROMPT, EFFECTIVE_AGENT_B_SYSTEM_PROMPT

_APP_NAME = "effective-agents"


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
    session_id = str(uuid_module.uuid4())

    await _session_service.create_session(
        app_name=_APP_NAME,
        user_id="system",
        session_id=session_id,
    )

    async for _ in runner.run_async(
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
        raise RuntimeError("Effective agent did not return a structured result")

    return _EffectiveOutput.model_validate(session.state["result"])


async def run_effective_agents(task_id: str, name: str, description: str) -> _EffectiveOutput:
    """Run both effective agents concurrently and merge their outputs."""
    message = f"Task ID: {task_id}\nName: {name}\nDescription: {description or ''}"

    result_a, result_b = await asyncio.gather(
        _run(_runner_a, message),
        _run(_runner_b, message),
    )

    avg_value = round((result_a.effective_value + result_b.effective_value) / 2)
    combined_explanation = f"{result_a.explanation}\n\n{result_b.explanation}"

    return _EffectiveOutput(effective_value=avg_value, explanation=combined_explanation)

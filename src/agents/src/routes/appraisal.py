"""POST /appraisal — evaluate the effective value of a task using two ADK agents."""

from fastapi import APIRouter, HTTPException

from src.agents.effective import run_effective_agents
from src.schemas.appraisal import AppraisalRequest, AppraisalResponse

router = APIRouter(tags=["appraisal"])


@router.post("/appraisal", response_model=AppraisalResponse)
async def appraisal(body: AppraisalRequest) -> AppraisalResponse:
    try:
        result = await run_effective_agents(
            task_id=str(body.task_id),
            name=body.name,
            description=body.description,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return AppraisalResponse(
        effective_value=result.effective_value,
        explanation=result.explanation,
    )

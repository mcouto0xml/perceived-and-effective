"""POST /recommendation — generate a recommendation for a perceived/effective divergence."""

from fastapi import APIRouter, HTTPException

from src.agents.recommendation import run_recommendation_agent
from src.schemas.recommendation import RecommendationRequest, RecommendationResponse

router = APIRouter(tags=["recommendation"])


@router.post("/recommendation", response_model=RecommendationResponse)
async def recommendation(body: RecommendationRequest) -> RecommendationResponse:
    try:
        text = await run_recommendation_agent(body)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return RecommendationResponse(recommendation=text, task_id=body.task_id)

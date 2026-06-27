"""
Periodic GitLab sync job.

Every POLL_INTERVAL_MINUTES minutes:
1. Fetch open issues from the configured GitLab project.
2. Upsert each issue as a Task in the DB.
3. For tasks without an effective value, call the effective agent and store the result.
4. For every appraisal of that task where |perceived - effective| > 4 and no recommendation
   exists yet, call the recommendation agent, store the result, and post a GitLab comment.
"""

import logging

import httpx
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.database import SessionLocal
from src.data.models.appraisals import Appraisals
from src.data.models.recommendation import Recommendations
from src.data.models.tasks import Tasks

logger = logging.getLogger(__name__)

DIVERGENCE_THRESHOLD = 4


def _gitlab_headers() -> dict:
    return {"PRIVATE-TOKEN": settings.gitlab_token}


def _fetch_gitlab_issues(client: httpx.Client) -> list[dict]:
    url = f"{settings.gitlab_url}/api/v4/projects/{settings.gitlab_project_id}/issues"
    response = client.get(url, params={"state": "opened", "per_page": 100}, headers=_gitlab_headers())
    response.raise_for_status()
    return response.json()


def _post_gitlab_comment(client: httpx.Client, iid: int, body: str) -> None:
    url = (
        f"{settings.gitlab_url}/api/v4/projects/{settings.gitlab_project_id}"
        f"/issues/{iid}/notes"
    )
    client.post(url, json={"body": body}, headers=_gitlab_headers()).raise_for_status()


def _call_effective_agent(client: httpx.Client, task: Tasks) -> tuple[int, str | None]:
    response = client.post(
        settings.effective_agent_url,
        json={
            "task_id": str(task.id),
            "name": task.name,
            "description": task.description,
        },
    )
    response.raise_for_status()
    data = response.json()
    return int(data["effective_value"]), data.get("explanation")


def _call_recommendation_agent(client: httpx.Client, task: Tasks, appraisal: Appraisals) -> str:
    response = client.post(
        settings.recommendation_agent_url,
        json={
            "task_id": str(task.id),
            "effective": task.effective,
            "effective_explanation": task.explanation,
            "perceived": appraisal.perceived,
            "perceived_explanation": appraisal.explanation,
            "description": task.description,
            "name": task.name,
        },
    )
    response.raise_for_status()
    return response.json()["recommendation"]


def _upsert_task(db: Session, issue: dict) -> Tasks:
    task = db.query(Tasks).filter(Tasks.gitlab_issue_id == issue["id"]).first()
    if task is None:
        task = Tasks(
            gitlab_issue_id=issue["id"],
            gitlab_project_id=settings.gitlab_project_id,
            gitlab_iid=issue["iid"],
            name=issue["title"],
            description=issue.get("description"),
            url=issue.get("web_url"),
        )
        db.add(task)
        db.flush()
    else:
        task.name = issue["title"]
        task.description = issue.get("description")
        task.url = issue.get("web_url")
        db.flush()
    return task


def run_sync() -> None:
    logger.info("Starting GitLab sync")
    try:
        with httpx.Client(timeout=30) as client:
            issues = _fetch_gitlab_issues(client)
            logger.info("Fetched %d open issues from GitLab", len(issues))

            with SessionLocal() as db:
                for issue in issues:
                    _process_issue(db, client, issue)
                db.commit()

    except Exception:
        logger.exception("GitLab sync failed")


def _process_issue(db: Session, client: httpx.Client, issue: dict) -> None:
    task = _upsert_task(db, issue)

    if task.effective is None:
        try:
            effective_value, explanation = _call_effective_agent(client, task)
            task.effective = effective_value
            task.explanation = explanation
            db.flush()
            logger.info("Task %s effective=%d", task.name, effective_value)
        except Exception:
            logger.exception("Effective agent call failed for task %s", task.gitlab_issue_id)
            return

    appraisals = db.query(Appraisals).filter(Appraisals.task_id == task.id).all()
    for appraisal in appraisals:
        if appraisal.recommendation is not None:
            continue

        if abs(appraisal.perceived - task.effective) > DIVERGENCE_THRESHOLD:
            _generate_recommendation(db, client, task, appraisal)


def _generate_recommendation(
    db: Session, client: httpx.Client, task: Tasks, appraisal: Appraisals
) -> None:
    try:
        recommendation_text = _call_recommendation_agent(client, task, appraisal)
    except Exception:
        logger.exception("Recommendation agent call failed for appraisal %s", appraisal.id)
        return

    recommendation = Recommendations(
        value=recommendation_text,
        task_id=task.id,
        appraisal_id=appraisal.id,
    )
    db.add(recommendation)
    db.flush()

    try:
        comment = (
            f"**Recommendation** (perceived: {appraisal.perceived}, "
            f"effective: {task.effective})\n\n{recommendation_text}"
        )
        _post_gitlab_comment(client, task.gitlab_iid, comment)
    except Exception:
        logger.exception("Failed to post GitLab comment for task %s", task.gitlab_issue_id)

"""Tasks routes."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.schemas.tasks import TaskEffectiveResponse, TaskResponse
from src.core.database import get_db
from src.data.models.appraisals import Appraisals
from src.data.models.tasks import Tasks
from src.data.models.users import Users

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/unevaluated/manager", response_model=list[TaskEffectiveResponse])
def get_tasks_unevaluated_by_manager(db: Session = Depends(get_db)):
    evaluated_by_manager = (
        db.query(Appraisals.task_id)
        .join(Users, Appraisals.user_id == Users.id)
        .filter(Users.is_manager.is_(True))
        .scalar_subquery()
    )
    tasks = db.query(Tasks).filter(Tasks.id.not_in(evaluated_by_manager)).all()
    return [
        TaskEffectiveResponse(
            id=t.id,
            name=t.name,
            description=t.description,
            url=t.url,
            effective=t.effective,
            explanation=t.explanation,
        )
        for t in tasks
    ]


@router.get("/unevaluated/{user_id}", response_model=list[TaskResponse])
def get_unevaluated_tasks(user_id: UUID, db: Session = Depends(get_db)):
    if not db.query(Users).filter(Users.id == user_id).first():
        raise HTTPException(status_code=404, detail="User not found")

    evaluated_task_ids = (
        db.query(Appraisals.task_id).filter(Appraisals.user_id == user_id).scalar_subquery()
    )
    tasks = db.query(Tasks).filter(Tasks.id.not_in(evaluated_task_ids)).all()
    return [TaskResponse(id=t.id, name=t.name, description=t.description, url=t.url) for t in tasks]


@router.get("/effective", response_model=list[TaskEffectiveResponse])
def get_tasks_effective(
    evaluated_only: Optional[bool] = Query(default=False, description="Return only tasks that already have an effective value"),
    db: Session = Depends(get_db),
):
    query = db.query(Tasks)
    if evaluated_only:
        query = query.filter(Tasks.effective.isnot(None))
    tasks = query.order_by(Tasks.created_at.desc()).all()
    return [
        TaskEffectiveResponse(
            id=t.id,
            name=t.name,
            description=t.description,
            url=t.url,
            effective=t.effective,
            explanation=t.explanation,
        )
        for t in tasks
    ]


@router.get("/effective/{task_id}", response_model=TaskEffectiveResponse)
def get_task_effective(task_id: UUID, db: Session = Depends(get_db)):
    task = db.query(Tasks).filter(Tasks.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskEffectiveResponse(
        id=task.id,
        name=task.name,
        description=task.description,
        url=task.url,
        effective=task.effective,
        explanation=task.explanation,
    )

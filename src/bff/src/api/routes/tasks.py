"""Tasks route: list tasks not yet appraised by a given user."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.schemas.tasks import TaskResponse
from src.core.database import get_db
from src.data.models.appraisals import Appraisals
from src.data.models.tasks import Tasks
from src.data.models.users import Users

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/unevaluated/{user_id}", response_model=list[TaskResponse])
def get_unevaluated_tasks(user_id: UUID, db: Session = Depends(get_db)):
    if not db.query(Users).filter(Users.id == user_id).first():
        raise HTTPException(status_code=404, detail="User not found")

    evaluated_task_ids = (
        db.query(Appraisals.task_id).filter(Appraisals.user_id == user_id).subquery()
    )
    tasks = db.query(Tasks).filter(Tasks.id.not_in(evaluated_task_ids)).all()
    return [TaskResponse(id=t.id, name=t.name, description=t.description, url=t.url) for t in tasks]

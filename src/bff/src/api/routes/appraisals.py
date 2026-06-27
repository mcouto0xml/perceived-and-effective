"""Appraisals route: submit a perceived value for a task."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.schemas.appraisals import SendAppraisalRequest, SendAppraisalResponse
from src.core.database import get_db
from src.data.models.appraisals import Appraisals
from src.data.models.tasks import Tasks
from src.data.models.users import Users

router = APIRouter(prefix="/appraisals", tags=["appraisals"])


@router.post("", response_model=SendAppraisalResponse, status_code=status.HTTP_201_CREATED)
def send_appraisal(body: SendAppraisalRequest, db: Session = Depends(get_db)):
    if not db.query(Users).filter(Users.id == body.user_id).first():
        raise HTTPException(status_code=404, detail="User not found")

    if not db.query(Tasks).filter(Tasks.id == body.task_id).first():
        raise HTTPException(status_code=404, detail="Task not found")

    existing = (
        db.query(Appraisals)
        .filter(Appraisals.user_id == body.user_id, Appraisals.task_id == body.task_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Appraisal already submitted for this task")

    appraisal = Appraisals(
        user_id=body.user_id,
        task_id=body.task_id,
        perceived=body.perceived,
        explanation=body.explanation,
    )
    db.add(appraisal)
    db.commit()
    db.refresh(appraisal)
    return SendAppraisalResponse(
        id=appraisal.id,
        user_id=appraisal.user_id,
        task_id=appraisal.task_id,
        perceived=appraisal.perceived,
        explanation=appraisal.explanation,
    )

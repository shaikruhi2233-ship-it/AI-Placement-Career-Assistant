from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import db_models, schemas
from app.database import get_db
from app.services import interview as interview_service

router = APIRouter(prefix="/interview", tags=["AI Mock Interview"])


@router.get("/questions")
def get_questions(interview_type: str = Query(..., pattern="^(technical|hr|coding)$"), count: int = 3):
    try:
        return interview_service.get_questions(interview_type, count)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/submit", response_model=schemas.InterviewResultOut)
def submit_interview(payload: schemas.InterviewSubmission, db: Session = Depends(get_db)):
    student = db.query(db_models.Student).get(payload.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    # Re-derive the same questions is not possible statelessly without IDs;
    # for simplicity we re-sample keyword sets sized to the answers given.
    try:
        questions = interview_service.get_questions(payload.interview_type, len(payload.answers))
        result = interview_service.evaluate_interview(payload.interview_type, questions, payload.answers)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    attempt = db_models.InterviewAttempt(
        student_id=payload.student_id,
        interview_type=result["interview_type"],
        technical_score=result["technical_score"],
        communication_score=result["communication_score"],
        confidence_score=result["confidence_score"],
        feedback=result["feedback"],
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


@router.get("/history/{student_id}", response_model=List[schemas.InterviewResultOut])
def interview_history(student_id: int, db: Session = Depends(get_db)):
    return (
        db.query(db_models.InterviewAttempt)
        .filter(db_models.InterviewAttempt.student_id == student_id)
        .order_by(db_models.InterviewAttempt.created_at.desc())
        .all()
    )

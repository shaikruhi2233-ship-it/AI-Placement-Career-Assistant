from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import db_models, schemas
from app.database import get_db
from app.services import coding_test

router = APIRouter(prefix="/coding", tags=["Coding Tests"])


@router.get("/problems", response_model=List[schemas.CodingProblemOut])
def list_problems(difficulty: Optional[str] = Query(None, pattern="^(easy|medium|hard)$")):
    return coding_test.list_problems(difficulty)


@router.get("/problems/{problem_id}", response_model=schemas.CodingProblemOut)
def get_problem(problem_id: str):
    try:
        return coding_test.get_problem(problem_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/submit", response_model=schemas.CodingResultOut)
def submit_solution(payload: schemas.CodingSubmission, db: Session = Depends(get_db)):
    student = db.query(db_models.Student).get(payload.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    try:
        result = coding_test.run_submission(payload.problem_id, payload.code)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    attempt = db_models.CodingAttempt(
        student_id=payload.student_id,
        problem_id=result["problem_id"],
        difficulty=result["difficulty"],
        passed_test_cases=result["passed_test_cases"],
        total_test_cases=result["total_test_cases"],
        score=result["score"],
        passed=result["passed"],
        submitted_code=payload.code,
        error_message=result["error_message"],
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


@router.get("/history/{student_id}", response_model=List[schemas.CodingResultOut])
def coding_history(student_id: int, db: Session = Depends(get_db)):
    return (
        db.query(db_models.CodingAttempt)
        .filter(db_models.CodingAttempt.student_id == student_id)
        .order_by(db_models.CodingAttempt.created_at.desc())
        .all()
    )

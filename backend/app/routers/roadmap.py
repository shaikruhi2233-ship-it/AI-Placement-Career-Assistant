from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app import db_models, schemas
from app.database import get_db
from app.services import career_guidance, roadmap as roadmap_service, weekly_quiz

router = APIRouter(prefix="/roadmap", tags=["Personalized Career Roadmap"])


# IMPORTANT: this static route must be registered BEFORE "/{student_id}"
# below. FastAPI/Starlette matches routes in registration order, and
# "/{student_id}" (typed as int) still matches ANY string segment at the
# routing stage — the int check only happens afterwards, as a 422
# validation error, so it would otherwise swallow "/week-quiz" requests
# before this handler ever runs.
@router.get("/week-quiz", response_model=List[schemas.QuizQuestionOut])
def get_week_quiz(skills: str = Query(..., description="Comma-separated list of that week's focus skills")):
    """End-of-week exam for the roadmap: a short quiz covering exactly the
    skills assigned to that week's sprint."""
    skill_list = [s.strip() for s in skills.split(",") if s.strip()]
    return weekly_quiz.get_week_quiz(skill_list)


@router.get("/{student_id}", response_model=schemas.RoadmapOut)
def get_roadmap(student_id: int, target_role: str = Query(...), db: Session = Depends(get_db)):
    student = db.query(db_models.Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    try:
        result = roadmap_service.generate_roadmap(student.technical_skills, student.soft_skills, target_role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


@router.get("/guidance/{student_id}", response_model=schemas.CareerGuidanceOut)
def get_guidance(student_id: int, target_role: str = Query(...), db: Session = Depends(get_db)):
    """Priority 5 - AI Career Guidance narrative, e.g. 'You are 58% ready
    for this role. First learn Docker and statistics, then build an ML
    deployment project.'"""
    student = db.query(db_models.Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    try:
        result = career_guidance.generate_guidance(student.technical_skills, student.soft_skills, target_role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result

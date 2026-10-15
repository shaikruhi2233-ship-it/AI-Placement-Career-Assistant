from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import db_models, schemas
from app.database import get_db
from app.services import skill_gap

router = APIRouter(prefix="/skills", tags=["Skill Gap Analysis"])


@router.get("/roles", response_model=List[str])
def list_target_roles():
    return skill_gap.available_roles()


@router.get("/gap/{student_id}", response_model=schemas.SkillGapOut)
def get_skill_gap(student_id: int, target_role: str = Query(...), db: Session = Depends(get_db)):
    student = db.query(db_models.Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    try:
        result = skill_gap.analyze_skill_gap(student.technical_skills, student.soft_skills, target_role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result

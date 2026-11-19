from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import db_models, schemas
from app.database import get_db
from app.services import external_jobs

router = APIRouter(prefix="/external-jobs", tags=["LinkedIn & GitHub Opportunities"])


@router.get("/{student_id}", response_model=List[schemas.ExternalOpportunityOut])
def get_external_opportunities(student_id: int, db: Session = Depends(get_db)):
    student = db.query(db_models.Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    return external_jobs.recommend_external_opportunities(student.technical_skills)

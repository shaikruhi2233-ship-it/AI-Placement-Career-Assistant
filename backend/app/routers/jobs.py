from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import db_models, schemas
from app.database import get_db
from app.services import job_recommend, live_jobs

router = APIRouter(prefix="/jobs", tags=["Job Recommendation"])


@router.get("/recommend/{student_id}", response_model=List[schemas.JobRecommendationOut])
def recommend(student_id: int, db: Session = Depends(get_db)):
    student = db.query(db_models.Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    # Blend in the latest resume's full text (if any) for the semantic
    # match signal, on top of the plain skill-overlap signal.
    latest_resume = (
        db.query(db_models.Resume)
        .filter(db_models.Resume.student_id == student_id)
        .order_by(db_models.Resume.uploaded_at.desc())
        .first()
    )
    resume_text = latest_resume.raw_text if latest_resume else None
    return job_recommend.recommend_jobs(student.technical_skills, resume_text=resume_text)


def _student_skills(student_id: Optional[int], db: Session) -> List[str]:
    if student_id is None:
        return []
    student = db.query(db_models.Student).get(student_id)
    return student.technical_skills if student else []


@router.get("/opportunities/{role}", response_model=List[schemas.JobOpportunityOut])
def opportunities(role: str, student_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Priority 3 - real-time job opportunities for a role: company,
    location, job type, required skills, match %, and apply link. Fetches
    live postings from a job-board API; falls back to the curated sample
    dataset automatically if a live fetch isn't possible."""
    return live_jobs.get_job_opportunities(role, _student_skills(student_id, db), want_internships=False)


@router.get("/internships/{role}", response_model=List[schemas.JobOpportunityOut])
def internships(role: str, student_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Priority 3 - real-time internships for a role, same fields and
    fallback behaviour as /jobs/opportunities."""
    return live_jobs.get_job_opportunities(role, _student_skills(student_id, db), want_internships=True)

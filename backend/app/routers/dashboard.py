from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import db_models, schemas
from app.database import get_db
from app.services.dashboard_insights import build_insights

router = APIRouter(prefix="/dashboard", tags=["Analytics Dashboard"])


@router.get("/{student_id}", response_model=schemas.DashboardOut)
def get_dashboard(student_id: int, db: Session = Depends(get_db)):
    student = db.query(db_models.Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    resumes = (
        db.query(db_models.Resume)
        .filter(db_models.Resume.student_id == student_id)
        .order_by(db_models.Resume.uploaded_at.desc())
        .all()
    )
    latest_resume = resumes[0] if resumes else None

    interview_history = (
        db.query(db_models.InterviewAttempt)
        .filter(db_models.InterviewAttempt.student_id == student_id)
        .order_by(db_models.InterviewAttempt.created_at.desc())
        .all()
    )
    all_predictions = (
        db.query(db_models.PredictionRecord)
        .filter(db_models.PredictionRecord.student_id == student_id)
        .order_by(db_models.PredictionRecord.created_at.asc())
        .all()
    )
    latest_prediction = all_predictions[-1] if all_predictions else None
    coding_attempts = (
        db.query(db_models.CodingAttempt)
        .filter(db_models.CodingAttempt.student_id == student_id)
        .all()
    )
    applications = (
        db.query(db_models.Application)
        .filter(db_models.Application.student_id == student_id)
        .all()
    )

    readiness_trend = [
        {"date": p.created_at.isoformat(), "readiness_score": p.readiness_score}
        for p in all_predictions
    ]

    insights = build_insights(
        student, latest_resume, all_predictions, interview_history, coding_attempts, applications
    )
    if len(resumes) >= 2:
        insights["ats_delta"] = round(resumes[0].ats_score - resumes[1].ats_score, 1)

    return {
        "student": student,
        "latest_resume": latest_resume,
        "latest_prediction": latest_prediction,
        "interview_history": interview_history,
        "readiness_trend": readiness_trend,
        "insights": insights,
    }

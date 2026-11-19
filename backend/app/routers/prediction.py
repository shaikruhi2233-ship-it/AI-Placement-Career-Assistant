from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import db_models, schemas
from app.database import get_db
from app.services import ml_model, model_evaluation

router = APIRouter(prefix="/prediction", tags=["Placement Readiness Prediction & Explainable AI"])


def _average(values, default=0.0):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else default


@router.get("/model/metrics")
def model_metrics():
    """Held-out evaluation of the readiness model: accuracy, precision,
    recall, F1, ROC-AUC, confusion matrix, 5-fold CV and feature importance."""
    try:
        return model_evaluation.get_metrics()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/{student_id}", response_model=schemas.PredictionOut)
def run_prediction(student_id: int, db: Session = Depends(get_db)):
    student = db.query(db_models.Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    latest_resume = (
        db.query(db_models.Resume)
        .filter(db_models.Resume.student_id == student_id)
        .order_by(db_models.Resume.uploaded_at.desc())
        .first()
    )
    recent_interviews = (
        db.query(db_models.InterviewAttempt)
        .filter(db_models.InterviewAttempt.student_id == student_id)
        .order_by(db_models.InterviewAttempt.created_at.desc())
        .limit(5)
        .all()
    )

    features = {
        "cgpa": student.cgpa,
        "attendance": student.attendance,
        "aptitude_score": student.aptitude_score,
        "coding_score": student.coding_score,
        "communication_score": student.communication_score,
        "internship_months": student.internship_months,
        "num_technical_skills": len(student.technical_skills or []),
        "num_certifications": len(student.certifications or []),
        "num_projects": len(student.projects or []),
        "ats_score": latest_resume.ats_score if latest_resume else 40.0,
        "resume_quality_score": latest_resume.resume_quality_score if latest_resume else 40.0,
        "interview_technical_score": _average([i.technical_score for i in recent_interviews], 40.0),
        "interview_communication_score": _average([i.communication_score for i in recent_interviews], 40.0),
        "interview_confidence_score": _average([i.confidence_score for i in recent_interviews], 40.0),
    }

    try:
        result = ml_model.predict_readiness(features)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    record = db_models.PredictionRecord(
        student_id=student_id,
        readiness_score=result["readiness_score"],
        placement_probability=result["placement_probability"],
        confidence_score=result["confidence_score"],
        readiness_label=result["readiness_label"],
        feature_importance=result["feature_importance"],
        feature_breakdown=result["feature_breakdown"],
        performance_status=result["performance_status"],
        top_positive_factors=result["top_positive_factors"],
        top_negative_factors=result["top_negative_factors"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{student_id}/latest", response_model=schemas.PredictionOut)
def latest_prediction(student_id: int, db: Session = Depends(get_db)):
    record = (
        db.query(db_models.PredictionRecord)
        .filter(db_models.PredictionRecord.student_id == student_id)
        .order_by(db_models.PredictionRecord.created_at.desc())
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="No prediction has been run for this student yet.")
    return record

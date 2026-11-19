from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import db_models, schemas
from app.database import get_db
from app.routers.auth import get_current_student

router = APIRouter(prefix="/applications", tags=["Job Applications (Tracker)"])

VALID_STATUSES = {"Applied", "Interviewing", "Rejected", "Selected"}


@router.get("/", response_model=List[schemas.ApplicationOut])
def list_my_applications(
    db: Session = Depends(get_db),
    current_student: db_models.Student = Depends(get_current_student),
):
    return (
        db.query(db_models.Application)
        .filter(db_models.Application.student_id == current_student.id)
        .order_by(db_models.Application.applied_at.desc())
        .all()
    )


@router.post("/", response_model=schemas.ApplicationOut)
def apply_to_job(
    payload: schemas.ApplicationCreate,
    db: Session = Depends(get_db),
    current_student: db_models.Student = Depends(get_current_student),
):
    existing = (
        db.query(db_models.Application)
        .filter(
            db_models.Application.student_id == current_student.id,
            db_models.Application.role == payload.role,
            db_models.Application.company == payload.company,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="You've already applied to this role.")

    application = db_models.Application(
        student_id=current_student.id,
        role=payload.role,
        company=payload.company,
        match_score=payload.match_score,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.put("/{application_id}", response_model=schemas.ApplicationOut)
def update_application_status(
    application_id: int,
    payload: schemas.ApplicationUpdate,
    db: Session = Depends(get_db),
    current_student: db_models.Student = Depends(get_current_student),
):
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Status must be one of {sorted(VALID_STATUSES)}.")

    application = (
        db.query(db_models.Application)
        .filter(db_models.Application.id == application_id, db_models.Application.student_id == current_student.id)
        .first()
    )
    if not application:
        raise HTTPException(status_code=404, detail="Application not found.")

    application.status = payload.status
    db.commit()
    db.refresh(application)
    return application


@router.delete("/{application_id}")
def withdraw_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_student: db_models.Student = Depends(get_current_student),
):
    application = (
        db.query(db_models.Application)
        .filter(db_models.Application.id == application_id, db_models.Application.student_id == current_student.id)
        .first()
    )
    if not application:
        raise HTTPException(status_code=404, detail="Application not found.")
    db.delete(application)
    db.commit()
    return {"detail": "Application withdrawn."}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import db_models, schemas
from app.database import get_db
from app.services import semester_tracker

router = APIRouter(prefix="/semesters", tags=["Semester-wise Improvement Tracking"])


@router.post("/{student_id}", response_model=schemas.SemesterRecordOut)
def add_semester_record(student_id: int, payload: schemas.SemesterRecordCreate, db: Session = Depends(get_db)):
    student = db.query(db_models.Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    record = db_models.SemesterRecord(student_id=student_id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{student_id}", response_model=schemas.SemesterTrendOut)
def get_semester_trend(student_id: int, db: Session = Depends(get_db)):
    student = db.query(db_models.Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    records = (
        db.query(db_models.SemesterRecord)
        .filter(db_models.SemesterRecord.student_id == student_id)
        .order_by(db_models.SemesterRecord.semester_number.asc())
        .all()
    )
    records_dicts = [
        {"semester_number": r.semester_number, "sgpa": r.sgpa, "attendance": r.attendance, "backlogs": r.backlogs}
        for r in records
    ]
    trend = semester_tracker.compute_trend(records_dicts)
    return {"records": records, **trend}


@router.delete("/{student_id}/{record_id}")
def delete_semester_record(student_id: int, record_id: int, db: Session = Depends(get_db)):
    record = (
        db.query(db_models.SemesterRecord)
        .filter(db_models.SemesterRecord.id == record_id, db_models.SemesterRecord.student_id == student_id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Semester record not found.")
    db.delete(record)
    db.commit()
    return {"detail": "Semester record deleted."}

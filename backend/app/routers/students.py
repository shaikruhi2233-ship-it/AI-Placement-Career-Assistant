from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import db_models, schemas
from app.database import get_db
from app.routers.auth import get_current_student

router = APIRouter(prefix="/students", tags=["Student Profile Management"])

# Note: account creation happens via POST /auth/register (sets a password).
# This router manages the profile data for an already-registered account.


@router.get("/", response_model=List[schemas.StudentOut])
def list_students(db: Session = Depends(get_db)):
    return db.query(db_models.Student).all()


@router.get("/{student_id}", response_model=schemas.StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(db_models.Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    return student


@router.put("/{student_id}", response_model=schemas.StudentOut)
def update_student(
    student_id: int,
    payload: schemas.StudentUpdate,
    db: Session = Depends(get_db),
    current_student: db_models.Student = Depends(get_current_student),
):
    if current_student.id != student_id:
        raise HTTPException(status_code=403, detail="You can only edit your own profile.")
    student = db.query(db_models.Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_student: db_models.Student = Depends(get_current_student),
):
    if current_student.id != student_id:
        raise HTTPException(status_code=403, detail="You can only delete your own account.")
    db.delete(current_student)
    db.commit()
    return {"detail": "Student deleted."}

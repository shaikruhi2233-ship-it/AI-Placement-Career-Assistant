from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app import db_models, schemas
from app.database import get_db
from app.services import auth

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_current_student(
    authorization: str = Header(None), db: Session = Depends(get_db)
) -> db_models.Student:
    """
    FastAPI dependency that extracts and validates the Bearer token from the
    Authorization header, returning the associated Student. Raise 401 if
    missing/invalid. Use as `Depends(get_current_student)` on any route
    that should require login.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated.")
    token = authorization.split(" ", 1)[1]
    student_id = auth.decode_access_token(token)
    if student_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    student = db.query(db_models.Student).get(student_id)
    if not student:
        raise HTTPException(status_code=401, detail="Account no longer exists.")
    return student


@router.post("/register", response_model=schemas.TokenOut)
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(db_models.Student).filter(db_models.Student.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    student = db_models.Student(
        name=payload.name,
        email=payload.email,
        hashed_password=auth.hash_password(payload.password),
        branch=payload.branch,
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    token = auth.create_access_token(student.id, student.email)
    return {"access_token": token, "student": student}


@router.post("/login", response_model=schemas.TokenOut)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    student = db.query(db_models.Student).filter(db_models.Student.email == payload.email).first()
    if not student or not auth.verify_password(payload.password, student.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    token = auth.create_access_token(student.id, student.email)
    return {"access_token": token, "student": student}


@router.get("/me", response_model=schemas.StudentOut)
def me(current_student: db_models.Student = Depends(get_current_student)):
    return current_student


@router.post("/reset-password", response_model=schemas.TokenOut)
def reset_password(payload: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    """Simplified 'Forgot Password' flow for the demo build: verifies the
    account exists by email and sets a new password directly (no SMTP/OTP
    service configured in this project). Logs the student straight in
    with the new password so the flow completes end to end."""
    student = db.query(db_models.Student).filter(db_models.Student.email == payload.email).first()
    if not student:
        raise HTTPException(status_code=404, detail="No account found with this email.")

    student.hashed_password = auth.hash_password(payload.new_password)
    db.commit()
    db.refresh(student)

    token = auth.create_access_token(student.id, student.email)
    return {"access_token": token, "student": student}

"""ORM models covering student profiles, resumes, assessments, and predictions."""
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship

from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    branch = Column(String, default="")
    cgpa = Column(Float, default=0.0)
    attendance = Column(Float, default=0.0)
    aptitude_score = Column(Float, default=0.0)
    coding_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    internship_months = Column(Integer, default=0)
    technical_skills = Column(JSON, default=list)   # ["python","sql",...]
    soft_skills = Column(JSON, default=list)
    certifications = Column(JSON, default=list)
    projects = Column(JSON, default=list)
    career_interest = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    resumes = relationship("Resume", back_populates="student", cascade="all, delete-orphan")
    interviews = relationship("InterviewAttempt", back_populates="student", cascade="all, delete-orphan")
    predictions = relationship("PredictionRecord", back_populates="student", cascade="all, delete-orphan")
    semester_records = relationship("SemesterRecord", back_populates="student", cascade="all, delete-orphan")
    coding_attempts = relationship("CodingAttempt", back_populates="student", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="student", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="student", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    filename = Column(String)
    raw_text = Column(Text)
    extracted_skills = Column(JSON, default=list)
    extracted_education = Column(JSON, default=list)
    extracted_experience = Column(JSON, default=list)
    ats_score = Column(Float, default=0.0)
    resume_quality_score = Column(Float, default=0.0)
    semantic_score = Column(Float, default=0.0)  # TF-IDF/cosine semantic match vs target role
    missing_keywords = Column(JSON, default=list)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="resumes")


class InterviewAttempt(Base):
    __tablename__ = "interview_attempts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    interview_type = Column(String)  # technical | hr | coding
    technical_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)
    feedback = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="interviews")


class PredictionRecord(Base):
    __tablename__ = "prediction_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    readiness_score = Column(Float)
    placement_probability = Column(Float)
    confidence_score = Column(Float)
    readiness_label = Column(String)   # Ready / Moderate / Needs Work
    feature_importance = Column(JSON, default=dict)
    feature_breakdown = Column(JSON, default=list)  # clean name, value, contribution %, rating
    performance_status = Column(JSON, default=list)  # category-level High/Medium/Average/Below Average/Low
    top_positive_factors = Column(JSON, default=list)
    top_negative_factors = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="predictions")


class SemesterRecord(Base):
    """Module - Semester-wise Improvement Tracking."""
    __tablename__ = "semester_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    semester_number = Column(Integer, nullable=False)
    sgpa = Column(Float, default=0.0)
    attendance = Column(Float, default=0.0)
    backlogs = Column(Integer, default=0)
    skills_gained = Column(JSON, default=list)
    remarks = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="semester_records")


class CodingAttempt(Base):
    """Module - Coding Tests."""
    __tablename__ = "coding_attempts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    problem_id = Column(String, nullable=False)
    difficulty = Column(String, default="")
    passed_test_cases = Column(Integer, default=0)
    total_test_cases = Column(Integer, default=0)
    score = Column(Float, default=0.0)
    passed = Column(Integer, default=0)  # 1/0 boolean flag (SQLite-friendly)
    submitted_code = Column(Text, default="")
    error_message = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="coding_attempts")


class ChatMessage(Base):
    """Module - AI Career Chatbot conversation log."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    role = Column(String)  # "user" | "bot"
    message = Column(Text)
    intent = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="chat_messages")


class Application(Base):
    """Tracks jobs a student has applied to from the Job Recommendation page."""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    role = Column(String, nullable=False)
    company = Column(String, default="")
    match_score = Column(Float, default=0.0)
    status = Column(String, default="Applied")  # Applied | Interviewing | Rejected | Selected
    applied_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="applications")

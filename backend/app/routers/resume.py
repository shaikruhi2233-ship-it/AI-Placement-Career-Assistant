from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session

from app import db_models, schemas
from app.database import get_db
from app.services import resume_parser, ats_analyzer, nlp_pipeline
from app.services.job_recommend import INDUSTRY_SKILLS

router = APIRouter(prefix="/resume", tags=["Resume Parsing & ATS Analysis"])


@router.post("/upload/{student_id}", response_model=schemas.ResumeOut)
async def upload_resume(
    student_id: int,
    target_role: str = Query(..., description="Target job role for ATS keyword matching"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    student = db.query(db_models.Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    if not file.filename.lower().endswith((".pdf", ".docx", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, or TXT resumes are supported.")

    raw_bytes = await file.read()
    parsed = resume_parser.parse_resume(raw_bytes, file.filename)

    all_skills = parsed["technical_skills"] + parsed["soft_skills"]
    ats_result = ats_analyzer.analyze_ats(parsed["raw_text"], all_skills, target_role)

    resume = db_models.Resume(
        student_id=student_id,
        filename=file.filename,
        raw_text=parsed["raw_text"],
        extracted_skills=all_skills,
        extracted_education=parsed["education"],
        extracted_experience=parsed["experience"],
        ats_score=ats_result["ats_score"],
        resume_quality_score=ats_result["resume_quality_score"],
        semantic_score=ats_result["semantic_score"],
        missing_keywords=ats_result["missing_keywords"],
    )
    db.add(resume)

    # Merge extracted skills into the student profile so downstream modules
    # (skill gap, roadmap, job recommendation) see the latest competencies.
    merged_technical = sorted(set(student.technical_skills) | set(parsed["technical_skills"]))
    merged_soft = sorted(set(student.soft_skills) | set(parsed["soft_skills"]))
    student.technical_skills = merged_technical
    student.soft_skills = merged_soft

    db.commit()
    db.refresh(resume)
    return resume


@router.get("/{student_id}/latest", response_model=schemas.ResumeOut)
def latest_resume(student_id: int, db: Session = Depends(get_db)):
    resume = (
        db.query(db_models.Resume)
        .filter(db_models.Resume.student_id == student_id)
        .order_by(db_models.Resume.uploaded_at.desc())
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="No resume uploaded for this student yet.")
    return resume


@router.get("/{student_id}/nlp-analysis")
def nlp_analysis(student_id: int, target_role: str = Query(None), db: Session = Depends(get_db)):
    """Full NLP pipeline breakdown of the student's latest resume:
    preprocessing stats, detected sections, rule-based named entities,
    linked skills with evidence, TF-IDF keywords, writing-quality signals,
    semantic similarity to every role, and prioritised suggestions."""
    resume = (
        db.query(db_models.Resume)
        .filter(db_models.Resume.student_id == student_id)
        .order_by(db_models.Resume.uploaded_at.desc())
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="No resume uploaded for this student yet.")
    student = db.query(db_models.Student).get(student_id)
    role = target_role or (student.career_interest if student and student.career_interest in INDUSTRY_SKILLS else None)
    result = nlp_pipeline.analyze(resume.raw_text or "", INDUSTRY_SKILLS, role)
    result["filename"] = resume.filename
    return result

"""
AI Placement and Career Assistant — FastAPI backend entrypoint.

Run locally:
    pip install -r requirements.txt
    python train_model.py          # one-time: trains the ML model
    uvicorn app.main:app --reload  # http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import (
    students, resume, skills, industry, roadmap, interview, prediction, jobs, dashboard,
    semesters, learning, coding, chatbot, external_jobs, auth, applications,
)

# Create tables on startup (use Alembic migrations in production)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Placement and Career Assistant",
    description=(
        "An Intelligent AI-Based Placement Readiness Prediction and Career Guidance "
        "System with Explainable Recommendations."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(resume.router)
app.include_router(skills.router)
app.include_router(industry.router)
app.include_router(roadmap.router)
app.include_router(interview.router)
app.include_router(prediction.router)
app.include_router(jobs.router)
app.include_router(dashboard.router)
app.include_router(semesters.router)
app.include_router(learning.router)
app.include_router(coding.router)
app.include_router(chatbot.router)
app.include_router(external_jobs.router)
app.include_router(applications.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "AI Placement and Career Assistant API"}

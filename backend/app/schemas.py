from datetime import datetime
from typing import List, Optional, Dict

from pydantic import BaseModel, EmailStr, ConfigDict


class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    branch: str = ""
    cgpa: float = 0.0
    attendance: float = 0.0
    aptitude_score: float = 0.0
    coding_score: float = 0.0
    communication_score: float = 0.0
    internship_months: int = 0
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    certifications: List[str] = []
    projects: List[str] = []
    career_interest: str = ""


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    branch: Optional[str] = None
    cgpa: Optional[float] = None
    attendance: Optional[float] = None
    aptitude_score: Optional[float] = None
    coding_score: Optional[float] = None
    communication_score: Optional[float] = None
    internship_months: Optional[int] = None
    technical_skills: Optional[List[str]] = None
    soft_skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    projects: Optional[List[str]] = None
    career_interest: Optional[str] = None


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    branch: str
    cgpa: float
    attendance: float
    aptitude_score: float
    coding_score: float
    communication_score: float
    internship_months: int
    technical_skills: List[str]
    soft_skills: List[str]
    certifications: List[str]
    projects: List[str]
    career_interest: str
    created_at: datetime


# ---- Authentication ----

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    branch: str = ""


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    student: StudentOut


class ResumeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    filename: str
    extracted_skills: List[str]
    extracted_education: List[str]
    extracted_experience: List[str]
    ats_score: float
    resume_quality_score: float
    semantic_score: float = 0.0
    missing_keywords: List[str]
    uploaded_at: datetime


class SkillGapOut(BaseModel):
    target_role: str
    matched_skills: List[str]
    missing_technical_skills: List[str]
    missing_soft_skills: List[str]
    recommended_certifications: List[str]
    recommended_projects: List[str]
    match_percentage: float


class IndustryDemandOut(BaseModel):
    trending_technologies: List[Dict]
    trending_roles: List[Dict]
    emerging_languages: List[str]
    computed_skill_demand: List[Dict] = []
    computed_role_demand: List[Dict] = []


# ---- AI Career Guidance (Priority 5) ----

class CareerGuidanceOut(BaseModel):
    target_role: str
    readiness_percentage: float
    stage: str
    narrative: str
    priority_skills: List[str]
    suggested_first_project: str


# ---- Skill-specific Learning Resources (Priority 4) ----

class SkillResourceItem(BaseModel):
    label: str
    title: str
    url: str


class SkillResourcesOut(BaseModel):
    skill: str
    resources: Dict[str, SkillResourceItem]


# ---- Real Job Opportunities (Priority 3) ----

class JobOpportunityOut(BaseModel):
    role: str
    company: str
    location: str
    job_type: str
    required_skills: List[str]
    match_score: float
    apply_link: str
    linkedin_link: str = ""      # real LinkedIn job-search deep link for this role/company
    source: str = "Sample"       # "Live" (fetched in real time) or "Sample" (offline fallback)
    posted_date: str = ""        # populated for live results only


class QuizQuestionOut(BaseModel):
    question: str
    options: List[str]
    correct_index: int
    explanation: str


class RoadmapOut(BaseModel):
    target_role: str
    weekly_plan: List[Dict]
    recommended_courses: List[Dict]
    certification_roadmap: List[str]
    project_recommendations: List[str]
    interview_prep_schedule: List[str]


class InterviewSubmission(BaseModel):
    student_id: int
    interview_type: str  # technical | hr | coding
    answers: List[str]


class InterviewResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    interview_type: str
    technical_score: float
    communication_score: float
    confidence_score: float
    feedback: str
    created_at: datetime


class PredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    readiness_score: float
    placement_probability: float
    confidence_score: float
    readiness_label: str
    feature_importance: Dict
    feature_breakdown: List[Dict] = []
    performance_status: List[Dict] = []
    top_positive_factors: List[str]
    top_negative_factors: List[str]
    created_at: datetime


class JobRecommendationOut(BaseModel):
    role: str
    match_score: float
    skill_match: float = 0.0
    semantic_match: float = 0.0
    companies: List[str]
    required_skills: List[str]
    matched_skills: List[str] = []


# ---- Semester-wise Improvement Tracking ----

class SemesterRecordCreate(BaseModel):
    semester_number: int
    sgpa: float = 0.0
    attendance: float = 0.0
    backlogs: int = 0
    skills_gained: List[str] = []
    remarks: str = ""


class SemesterRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    semester_number: int
    sgpa: float
    attendance: float
    backlogs: int
    skills_gained: List[str]
    remarks: str
    created_at: datetime


class SemesterTrendOut(BaseModel):
    records: List[SemesterRecordOut]
    sgpa_change: float
    attendance_change: float
    improvement_summary: str


# ---- Learning Portals ----

class LearningPortalItem(BaseModel):
    name: str
    url: str
    description: str


class LearningPortalsOut(BaseModel):
    categories: Dict[str, List[LearningPortalItem]]


# ---- Coding Tests ----

class CodingProblemOut(BaseModel):
    id: str
    title: str
    difficulty: str
    description: str
    starter_code: str


class CodingSubmission(BaseModel):
    student_id: int
    problem_id: str
    code: str


class CodingResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    problem_id: str
    difficulty: str
    passed_test_cases: int
    total_test_cases: int
    score: float
    passed: int
    error_message: str
    created_at: datetime


# ---- AI Career Chatbot ----

class ChatRequest(BaseModel):
    student_id: Optional[int] = None
    message: str


class ChatResponseOut(BaseModel):
    reply: str
    intent: str
    confidence: float = 0.0      # cosine similarity of the nearest training utterance (0-100)
    grounded: bool = False       # True when the answer used the student's own data


class ChatHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role: str
    message: str
    created_at: datetime


# ---- LinkedIn / GitHub Job & Internship Recommendations ----

class ExternalOpportunityOut(BaseModel):
    source: str          # "LinkedIn" | "GitHub"
    type: str            # "Job" | "Internship"
    title: str
    company_or_org: str
    match_score: float
    url: str
    location: str = ""


# ---- Job Applications (Job Tracker) ----

class ApplicationCreate(BaseModel):
    role: str
    company: str = ""
    match_score: float = 0.0


class ApplicationUpdate(BaseModel):
    status: str  # Applied | Interviewing | Rejected | Selected


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    company: str
    match_score: float
    status: str
    applied_at: datetime


class DashboardOut(BaseModel):
    student: StudentOut
    latest_resume: Optional[ResumeOut]
    latest_prediction: Optional[PredictionOut]
    interview_history: List[InterviewResultOut]
    readiness_trend: List[Dict]
    # Computed at-a-glance metrics + prioritised next steps
    # (see app/services/dashboard_insights.py)
    insights: Dict = {}

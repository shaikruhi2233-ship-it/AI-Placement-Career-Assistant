"""
Module 10 - Intelligent Job Recommendation (Priority 2 + Priority 3).

Priority 2 - "Resume -> Multiple Job Roles":
`recommend_jobs()` blends two signals per role and returns a ranked list
with a single match percentage per role (Python Developer 88%, Data
Analyst 82%, ...):
  1. skill_match       overlap between the student's (resume-extracted)
                        technical skills and the role's required skills
  2. semantic_match     TF-IDF/cosine similarity between the resume's full
                        text and the role's requirement corpus (see
                        app/services/nlp_semantic.py) - credits related
                        experience even when it isn't phrased with the
                        exact vocabulary term

Priority 3 - "Real Job Opportunities":
`real_job_opportunities()` turns a chosen role into concrete postings -
company, location, job type, required skills, match % and an apply link -
sourced from the sample job-market dataset in app/data/real_jobs.json
(the swap-in point for a live job-board API/scraper in production).
"""
import json
import os
from typing import List, Optional

from app.services.nlp_semantic import role_corpus, semantic_similarity

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
with open(os.path.join(DATA_DIR, "industry_skills.json")) as f:
    INDUSTRY_SKILLS = json.load(f)
with open(os.path.join(DATA_DIR, "real_jobs.json")) as f:
    REAL_JOBS = json.load(f)


def _skill_overlap_score(student_skills_lower: set, required: List[str]) -> float:
    if not required:
        return 0.0
    matched = [s for s in required if s in student_skills_lower]
    return round((len(matched) / len(required)) * 100, 2)


def recommend_jobs(student_technical: List[str], resume_text: Optional[str] = None, top_n: int = 6) -> List[dict]:
    student_skills = {s.lower() for s in student_technical}
    scored = []
    for role, data in INDUSTRY_SKILLS.items():
        required = [s.lower() for s in data["technical_skills"]]
        matched = [s for s in required if s in student_skills]
        skill_score = _skill_overlap_score(student_skills, required)
        semantic_score = semantic_similarity(resume_text, role_corpus(data)) if resume_text else 0.0

        # Skill overlap stays the primary, verifiable signal; semantic
        # similarity adds credit for related experience phrased
        # differently to the exact vocabulary list. Falls back to pure
        # skill overlap when no resume text is available yet.
        match_score = round(0.7 * skill_score + 0.3 * semantic_score, 2) if resume_text else skill_score

        scored.append({
            "role": role,
            "match_score": min(match_score, 100.0),
            "skill_match": skill_score,
            "semantic_match": semantic_score,
            "companies": data.get("companies", []),
            "required_skills": data["technical_skills"],
            "matched_skills": matched,
        })
    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return scored[:top_n]


def real_job_opportunities(role: str, student_technical: Optional[List[str]] = None) -> List[dict]:
    """Priority 3 - concrete job postings for a role: company, location,
    job type, required skills, match % and apply link."""
    postings = REAL_JOBS.get(role, [])
    student_skills = {s.lower() for s in (student_technical or [])}
    role_data = INDUSTRY_SKILLS.get(role, {})

    results = []
    for post in postings:
        posting_required = [s.lower() for s in post.get("required_skills", role_data.get("technical_skills", []))]
        matched = [s for s in posting_required if s in student_skills]
        match_pct = round((len(matched) / len(posting_required)) * 100, 2) if posting_required else 0.0
        results.append({
            "role": role,
            "company": post["company"],
            "location": post["location"],
            "job_type": post["job_type"],
            "required_skills": post.get("required_skills", role_data.get("technical_skills", [])),
            "match_score": match_pct,
            "apply_link": post["apply_link"],
        })
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results


def available_job_roles() -> List[str]:
    return list(REAL_JOBS.keys())

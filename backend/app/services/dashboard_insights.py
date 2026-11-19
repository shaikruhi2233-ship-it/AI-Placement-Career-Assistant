"""
Dashboard Insights - turns everything the platform knows about a student
into the at-a-glance numbers and the prioritised "Next Steps" list shown on
the Analytics Dashboard.

Everything here is computed from data the other modules already store
(profile, latest resume, predictions, mock interviews, coding attempts,
job applications) - no new tables, no extra user input.
"""
from typing import Dict, List, Optional

from app.services.job_recommend import INDUSTRY_SKILLS, recommend_jobs
from app.services.skill_gap import analyze_skill_gap

# (field, label, weight) - what a "complete" placement profile contains.
PROFILE_FIELDS = [
    ("branch", "Branch", 10),
    ("cgpa", "CGPA", 15),
    ("attendance", "Attendance", 10),
    ("technical_skills", "Technical skills", 20),
    ("soft_skills", "Soft skills", 10),
    ("projects", "Projects", 15),
    ("certifications", "Certifications", 10),
    ("career_interest", "Career interest", 10),
]


def _filled(value) -> bool:
    if value is None:
        return False
    if isinstance(value, (list, tuple, str)):
        return len(value) > 0
    if isinstance(value, (int, float)):
        return value > 0
    return bool(value)


def profile_completeness(student) -> Dict:
    total = sum(w for _, _, w in PROFILE_FIELDS)
    got = 0
    missing: List[str] = []
    for field, label, weight in PROFILE_FIELDS:
        if _filled(getattr(student, field, None)):
            got += weight
        else:
            missing.append(label)
    return {"percentage": round(got / total * 100), "missing_fields": missing}


def _resolve_target_role(student, top_matches: List[Dict]) -> Optional[str]:
    """The student's stated career interest if it maps to a known role,
    otherwise the role their skills currently match best."""
    interest = (student.career_interest or "").strip().lower()
    if interest:
        for role in INDUSTRY_SKILLS:
            if role.lower() == interest or interest in role.lower() or role.lower() in interest:
                return role
    # Only infer a role once the student actually matches something.
    if top_matches and top_matches[0]["match_score"] > 0:
        return top_matches[0]["role"]
    return None


# Display names for skills whose casing a plain .title() gets wrong.
SKILL_DISPLAY = {
    "sql": "SQL", "html": "HTML", "css": "CSS", "javascript": "JavaScript", "typescript": "TypeScript",
    "node.js": "Node.js", "rest api": "REST API", "aws": "AWS", "gcp": "GCP", "ci/cd": "CI/CD",
    "power bi": "Power BI", "mongodb": "MongoDB", "mysql": "MySQL", "postgresql": "PostgreSQL",
    "nlp": "NLP", "github": "GitHub", "api": "API", "ui/ux": "UI/UX", "oop": "OOP",
}


def pretty_skill(skill: str) -> str:
    return SKILL_DISPLAY.get(skill.lower(), skill.title() if skill.islower() else skill)


def _delta(series: List[float]) -> Optional[float]:
    if len(series) < 2:
        return None
    return round(series[-1] - series[-2], 1)


def build_insights(student, latest_resume, predictions, interviews, coding_attempts, applications) -> Dict:
    profile = profile_completeness(student)

    resume_text = latest_resume.raw_text if latest_resume else None
    matches = recommend_jobs(student.technical_skills or [], resume_text=resume_text, top_n=3)
    top_matches = [
        {"role": m["role"], "match_score": m["match_score"], "companies": m["companies"][:3]}
        for m in matches
    ]

    target_role = _resolve_target_role(student, matches)
    skill_gap = None
    if target_role:
        gap = analyze_skill_gap(student.technical_skills or [], student.soft_skills or [], target_role)
        skill_gap = {
            "target_role": target_role,
            "match_percentage": gap["match_percentage"],
            "matched_skills": gap["matched_skills"],
            "missing_skills": gap["missing_technical_skills"],
            "required_count": len(gap["matched_skills"]) + len(gap["missing_technical_skills"]),
        }

    readiness_series = [p.readiness_score for p in predictions]  # oldest -> newest
    interview_scores = [
        round((i.technical_score + i.communication_score + i.confidence_score) / 3, 1) for i in interviews
    ]
    coding_scores = [c.score for c in coding_attempts]

    interview_stats = {
        "count": len(interviews),
        "average": round(sum(interview_scores) / len(interview_scores), 1) if interview_scores else None,
        "types_done": sorted({i.interview_type for i in interviews}),
    }
    coding_stats = {
        "count": len(coding_attempts),
        "solved": sum(1 for c in coding_attempts if c.passed),
        "average": round(sum(coding_scores) / len(coding_scores), 1) if coding_scores else None,
    }

    # ---- Prioritised next steps (most impactful first, max 5) ----
    steps: List[Dict] = []

    def add(title, detail, to, priority):
        steps.append({"title": title, "detail": detail, "to": to, "priority": priority})

    if profile["percentage"] < 100:
        add(
            "Complete your profile",
            f"Add {', '.join(profile['missing_fields'][:3])} to unlock accurate predictions.",
            "/profile",
            "high" if profile["percentage"] < 60 else "medium",
        )
    if not latest_resume:
        add("Upload your resume", "Get your ATS score and auto-extract your skills.", "/resume", "high")
    elif latest_resume.ats_score < 60:
        kw = ", ".join((latest_resume.missing_keywords or [])[:3])
        add(
            "Improve your resume ATS score",
            f"Currently {latest_resume.ats_score:.0f}/100." + (f" Add keywords: {kw}." if kw else ""),
            "/resume",
            "high",
        )
    if skill_gap and skill_gap["missing_skills"]:
        nxt = skill_gap["missing_skills"][:2]
        add(
            f"Learn {' & '.join(pretty_skill(s) for s in nxt)}",
            f"Top missing skills for {skill_gap['target_role']} ({skill_gap['match_percentage']:.0f}% match).",
            "/skill-gap",
            "high" if skill_gap["match_percentage"] < 50 else "medium",
        )
    if not predictions:
        add("Run your readiness prediction", "See your placement score with an AI explanation.", "/prediction", "medium")
    if "hr" not in interview_stats["types_done"]:
        add("Take an HR mock interview", "Practise behavioural answers with instant feedback.", "/interview", "medium")
    elif "technical" not in interview_stats["types_done"]:
        add("Take a technical mock interview", "Test your core concepts with instant scoring.", "/interview", "medium")
    if coding_stats["count"] < 3:
        add("Solve coding problems", f"{coding_stats['count']} attempted so far - aim for at least 3.", "/coding", "low")
    if not applications and matches and matches[0]["match_score"] >= 50:
        add(
            f"Apply for {matches[0]['role']} roles",
            f"You already match {matches[0]['match_score']:.0f}% - explore live openings.",
            "/jobs",
            "low",
        )

    order = {"high": 0, "medium": 1, "low": 2}
    steps.sort(key=lambda s: order[s["priority"]])

    return {
        "profile": profile,
        "readiness_delta": _delta(readiness_series),
        "ats_delta": None,
        "interview_stats": interview_stats,
        "coding_stats": coding_stats,
        "applications_count": len(applications),
        "skill_gap": skill_gap,
        "top_matches": top_matches,
        "next_steps": steps[:5],
    }

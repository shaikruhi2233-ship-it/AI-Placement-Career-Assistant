"""
Module 4 - Skill Gap Analysis.

Compares a student's current technical/soft skills against the
requirements of a target industry role and reports missing competencies
plus recommended certifications and projects to close the gap.
"""
import json
import os
from typing import List

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
with open(os.path.join(DATA_DIR, "industry_skills.json")) as f:
    INDUSTRY_SKILLS = json.load(f)


def available_roles() -> List[str]:
    return list(INDUSTRY_SKILLS.keys())


def analyze_skill_gap(student_technical: List[str], student_soft: List[str], target_role: str) -> dict:
    role = INDUSTRY_SKILLS.get(target_role)
    if role is None:
        raise ValueError(f"Unknown target role '{target_role}'. Choose from {available_roles()}")

    student_tech_lower = {s.lower() for s in student_technical}
    student_soft_lower = {s.lower() for s in student_soft}

    required_tech = [s.lower() for s in role["technical_skills"]]
    required_soft = [s.lower() for s in role["soft_skills"]]

    matched = [s for s in required_tech if s in student_tech_lower]
    missing_tech = [s for s in required_tech if s not in student_tech_lower]
    missing_soft = [s for s in required_soft if s not in student_soft_lower]

    match_pct = round((len(matched) / len(required_tech)) * 100, 2) if required_tech else 0.0

    return {
        "target_role": target_role,
        "matched_skills": matched,
        "missing_technical_skills": missing_tech,
        "missing_soft_skills": missing_soft,
        "recommended_certifications": role.get("certifications", []),
        "recommended_projects": role.get("projects", []),
        "match_percentage": match_pct,
    }

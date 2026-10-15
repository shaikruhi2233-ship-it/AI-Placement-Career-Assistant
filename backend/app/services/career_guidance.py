"""
Module - AI Career Guidance narrative (Priority 5 - "AI Career Guidance").

Turns a skill-gap result into the plain-language guidance from the
feature spec: "You are 58% ready for this role. First learn Docker and
statistics, then build an ML deployment project." Missing skills are
ordered so foundational skills (languages, core CS, core tools) are
recommended before advanced/tooling skills, since those unlock everything
else.
"""
from typing import List

from app.services.skill_gap import analyze_skill_gap

# Skills tagged "foundational" are surfaced before "advanced" ones,
# regardless of the order they appear in the industry_skills dataset.
FOUNDATIONAL_SKILLS = {
    "python", "sql", "java", "javascript", "statistics", "data structures",
    "html", "css", "excel", "git", "linux",
}


def _priority_sort(missing: List[str]) -> List[str]:
    foundational = [s for s in missing if s in FOUNDATIONAL_SKILLS]
    advanced = [s for s in missing if s not in FOUNDATIONAL_SKILLS]
    return foundational + advanced


def generate_guidance(student_technical: List[str], student_soft: List[str], target_role: str) -> dict:
    gap = analyze_skill_gap(student_technical, student_soft, target_role)
    readiness_pct = gap["match_percentage"]
    ordered_missing = _priority_sort(gap["missing_technical_skills"])

    if readiness_pct >= 85:
        stage = "You're placement-ready for this role."
    elif readiness_pct >= 60:
        stage = "You're close — a few targeted skills will get you there."
    else:
        stage = "You have a meaningful gap to close, but a clear path forward."

    first_two = ordered_missing[:2]
    project = gap["recommended_projects"][0] if gap["recommended_projects"] else "a portfolio project for this role"

    if first_two:
        learn_clause = f"First learn {' and '.join(first_two)}, then build {project}."
    else:
        learn_clause = f"Your core skills already match — focus on {project} and mock interviews to stand out."

    narrative = f"You are {readiness_pct:.0f}% ready for {target_role}. {learn_clause}"

    return {
        "target_role": target_role,
        "readiness_percentage": readiness_pct,
        "stage": stage,
        "narrative": narrative,
        "priority_skills": ordered_missing,
        "suggested_first_project": project,
    }

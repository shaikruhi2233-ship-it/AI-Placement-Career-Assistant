"""
Module 6 - Personalized Career Roadmap Generator.

Turns a skill-gap result into a week-by-week learning plan, course
recommendations, a certification roadmap, and an interview prep schedule.
"""
import json
import os
from typing import List

from app.services.skill_gap import analyze_skill_gap

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
with open(os.path.join(DATA_DIR, "courses.json")) as f:
    COURSES = json.load(f)


def _courses_for(skill: str) -> List[dict]:
    return COURSES.get(skill.lower(), [{"title": f"Search: {skill} fundamentals", "provider": "YouTube / Coursera"}])


def generate_roadmap(student_technical: List[str], student_soft: List[str], target_role: str) -> dict:
    gap = analyze_skill_gap(student_technical, student_soft, target_role)
    missing_skills = gap["missing_technical_skills"]

    # Distribute missing skills across weekly sprints (max 2 skills/week)
    weekly_plan = []
    week = 1
    for i in range(0, len(missing_skills), 2):
        chunk = missing_skills[i:i + 2]
        weekly_plan.append({
            "week": week,
            "focus_skills": chunk,
            "goal": f"Build fundamentals in {', '.join(chunk)} and complete one hands-on exercise per skill.",
        })
        week += 1

    if not weekly_plan:
        weekly_plan.append({
            "week": 1,
            "focus_skills": [],
            "goal": "Core skill set already matches the target role — focus on advanced projects and mock interviews.",
        })

    recommended_courses = []
    for skill in missing_skills:
        for course in _courses_for(skill):
            recommended_courses.append({"skill": skill, **course})

    interview_prep_schedule = [
        "Week 1-2: Revise core CS fundamentals (DSA, DBMS, OS, Networks)",
        "Week 3: Practice 2 mock technical interviews",
        "Week 4: Practice 1 mock HR interview + resume review",
        "Week 5: Company-specific preparation (aptitude + coding rounds)",
    ]

    return {
        "target_role": target_role,
        "weekly_plan": weekly_plan,
        "recommended_courses": recommended_courses,
        "certification_roadmap": gap["recommended_certifications"],
        "project_recommendations": gap["recommended_projects"],
        "interview_prep_schedule": interview_prep_schedule,
    }

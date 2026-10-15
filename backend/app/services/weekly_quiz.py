"""
Weekly Roadmap Exam (per-week quiz).

The Personalized Career Roadmap breaks missing skills into weekly
sprints (see roadmap.py). This module generates a short multiple-choice
exam covering exactly the skills assigned to a given week, so a student
can check their understanding before moving to the next week.
"""
import json
import os
import random
from typing import List

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
with open(os.path.join(DATA_DIR, "skill_quizzes.json")) as f:
    QUIZ_BANK = json.load(f)

# Used only when none of the week's skills have a curated question bank yet,
# so the exam still has something reasonable to ask.
GENERIC_FALLBACK_QUESTIONS = [
    {
        "question": "Which of these is the best first step when learning a new technical skill?",
        "options": ["Skip the basics and go straight to advanced topics", "Build a small hands-on project alongside the fundamentals", "Only read documentation, never practice", "Wait until you feel 100% confident before trying anything"],
        "correct_index": 1,
        "explanation": "Pairing fundamentals with a small hands-on project reinforces learning far better than theory alone.",
    },
    {
        "question": "What is generally the most reliable way to verify you understand a new concept?",
        "options": ["Memorizing definitions", "Explaining it in your own words or teaching it to someone else", "Reading it once", "Watching a video without taking notes"],
        "correct_index": 1,
        "explanation": "Being able to explain a concept in your own words is a strong signal of real understanding.",
    },
]


def get_week_quiz(focus_skills: List[str], num_questions: int = 5) -> List[dict]:
    """Builds a shuffled quiz drawn from the given skills' question banks.
    Falls back to generic study-check questions if none of the skills are
    in the curated bank yet, so the exam is never empty."""
    pool: List[dict] = []
    for skill in focus_skills:
        pool.extend(QUIZ_BANK.get(skill.lower().strip(), []))

    if not pool:
        pool = list(GENERIC_FALLBACK_QUESTIONS)

    random.shuffle(pool)
    return pool[:num_questions]

"""
Module 7 - AI Mock Interview System.

Presents questions from the question bank and evaluates free-text answers
using keyword-coverage scoring as a proxy for technical correctness, plus
simple linguistic heuristics (answer length, filler-word ratio) as a proxy
for communication and confidence. Swappable for an LLM-graded rubric.
"""
import json
import os
import random
import re
from typing import List

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
with open(os.path.join(DATA_DIR, "interview_questions.json")) as f:
    QUESTION_BANK = json.load(f)

FILLER_WORDS = {"um", "uh", "like", "basically", "actually", "you know"}


def get_questions(interview_type: str, count: int = 3) -> List[dict]:
    pool = QUESTION_BANK.get(interview_type, [])
    if not pool:
        raise ValueError(f"Unknown interview type '{interview_type}'")
    return random.sample(pool, min(count, len(pool)))


def _keyword_score(answer: str, keywords: List[str]) -> float:
    answer_lower = answer.lower()
    hits = sum(1 for kw in keywords if kw in answer_lower)
    return (hits / len(keywords)) * 100 if keywords else 50.0


def _communication_score(answer: str) -> float:
    words = re.findall(r"\w+", answer.lower())
    if not words:
        return 0.0
    filler_ratio = sum(1 for w in words if w in FILLER_WORDS) / len(words)
    length_score = min(len(words) / 40 * 100, 100)  # reward substantive answers up to ~40 words
    return round(max(0.0, length_score * (1 - filler_ratio)), 2)


def evaluate_interview(interview_type: str, questions: List[dict], answers: List[str]) -> dict:
    if len(answers) != len(questions):
        raise ValueError("Number of answers must match number of questions")

    technical_scores, communication_scores = [], []
    for q, a in zip(questions, answers):
        technical_scores.append(_keyword_score(a, q.get("keywords", [])))
        communication_scores.append(_communication_score(a))

    avg_technical = round(sum(technical_scores) / len(technical_scores), 2)
    avg_communication = round(sum(communication_scores) / len(communication_scores), 2)
    # Confidence proxied by consistency (low variance) + communication score
    variance_penalty = (max(communication_scores) - min(communication_scores)) if len(communication_scores) > 1 else 0
    confidence_score = round(max(0.0, avg_communication - variance_penalty * 0.2), 2)

    feedback_bits = []
    if avg_technical < 50:
        feedback_bits.append("Revisit core concepts — key terms were missing from your answers.")
    else:
        feedback_bits.append("Good grasp of core concepts.")
    if avg_communication < 50:
        feedback_bits.append("Try to elaborate more and reduce filler words for clearer communication.")
    else:
        feedback_bits.append("Communication was clear and reasonably detailed.")

    return {
        "interview_type": interview_type,
        "technical_score": avg_technical,
        "communication_score": avg_communication,
        "confidence_score": confidence_score,
        "feedback": " ".join(feedback_bits),
    }

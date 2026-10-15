"""
Module - AI Career Chatbot (answers with the student's REAL data).

Two layers:
1. NLP intent classification - every training utterance in
   app/data/chatbot_intents.json is preprocessed (lower-casing, alias
   canonicalisation, lemmatisation) and embedded as a TF-IDF vector over
   word uni/bi-grams PLUS character 3-5-grams (robust to typos such as
   "intervew" or "resum"). An incoming message is embedded the same way and
   classified by cosine similarity to the nearest utterance (a 1-nearest-
   neighbour classifier in TF-IDF space). Below a confidence threshold the
   bot falls back instead of guessing.
2. Data-grounded answer generation - for intents that map to something
   this app already computes (skill gap, resume ATS, placement
   prediction, job matches, learning resources, semester trend), the
   chatbot calls the SAME services the dashboard pages use and answers
   with the student's actual numbers, not a "go check this page"
   redirect. It only falls back to the canned navigation-style response
   when there truly isn't enough context yet (no student_id, no resume
   uploaded, target role not recognised in the question, etc.).
"""
import json
import os
import random
import re
from typing import Optional

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.pipeline import FeatureUnion
from sqlalchemy.orm import Session

from app import db_models
from app.services import career_guidance, job_recommend, skill_gap, skill_resources
from app.services.job_recommend import INDUSTRY_SKILLS
from app.services.skill_resources import SKILL_RESOURCES
from app.services.nlp_pipeline import lemmatize, normalize_for_matching

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
with open(os.path.join(DATA_DIR, "chatbot_intents.json")) as f:
    INTENTS = json.load(f)

# Free-text ways students phrase a role, mapped to the canonical role name
# used across industry_skills.json / skill_gap / job_recommend.
ROLE_ALIASES = {
    "full stack developer": "Full Stack Developer",
    "full stack": "Full Stack Developer",
    "fullstack": "Full Stack Developer",
    "software development engineer": "Software Development Engineer",
    "software developer": "Software Development Engineer",
    "software engineer": "Software Development Engineer",
    "sde": "Software Development Engineer",
    "data analyst": "Data Analyst",
    "machine learning engineer": "Machine Learning Engineer",
    "ml engineer": "Machine Learning Engineer",
    "devops engineer": "DevOps Engineer",
    "devops": "DevOps Engineer",
    "business analyst": "Business Analyst",
}


CONFIDENCE_THRESHOLD = 0.28


# Question words / fillers carry no intent signal ("what is the weather"
# must not look like "what is my ats score"), but a few short words do.
_KEEP = {"hi", "hey", "my", "me", "i", "next", "thank", "thanks", "you", "good", "chance", "low"}
_STOP = {w for w in ENGLISH_STOP_WORDS if w not in _KEEP}


def _preprocess(text: str) -> str:
    """Lower-case, canonicalise skill aliases, drop stop words, lemmatise."""
    words = re.findall(r"[a-z0-9+#.]+", normalize_for_matching(text))
    content = [w for w in words if w not in _STOP] or words
    return " ".join(lemmatize(w) for w in content)


def _build_classifier():
    utterances, labels = [], []
    for intent in INTENTS:
        for pattern in intent["patterns"]:
            utterances.append(_preprocess(pattern))
            labels.append(intent["intent"])
    vectorizer = FeatureUnion([
        ("word", TfidfVectorizer(analyzer="word", ngram_range=(1, 2), token_pattern=r"[a-z0-9+#.]+")),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))),
    ])
    matrix = vectorizer.fit_transform(utterances)
    return vectorizer, matrix, labels


_VECTORIZER, _UTTERANCE_MATRIX, _LABELS = _build_classifier()
_INTENT_BY_NAME = {i["intent"]: i for i in INTENTS}


def classify_intent(message: str):
    """Returns (intent_dict, confidence 0-1)."""
    vec = _VECTORIZER.transform([_preprocess(message)])
    sims = cosine_similarity(vec, _UTTERANCE_MATRIX)[0]
    best = int(sims.argmax()) if len(sims) else 0
    confidence = float(sims[best]) if len(sims) else 0.0
    if confidence < CONFIDENCE_THRESHOLD:
        return _INTENT_BY_NAME["fallback"], confidence
    return _INTENT_BY_NAME[_LABELS[best]], confidence


def _match_intent(message: str) -> dict:
    return classify_intent(message)[0]


def _detect_role(message: str) -> Optional[str]:
    text = message.lower()
    for alias in sorted(ROLE_ALIASES, key=len, reverse=True):
        if alias in text:
            return ROLE_ALIASES[alias]
    for role in INDUSTRY_SKILLS:
        if role.lower() in text:
            return role
    return None


def _detect_skill(message: str) -> Optional[str]:
    text = message.lower()
    for skill_key in SKILL_RESOURCES:
        if skill_key in text:
            return skill_key
    for role_data in INDUSTRY_SKILLS.values():
        for skill in role_data.get("technical_skills", []):
            if skill.lower() in text:
                return skill.lower()
    return None


def _get_student(student_id: Optional[int], db: Optional[Session]):
    if not student_id or db is None:
        return None
    return db.query(db_models.Student).get(student_id)


def _answer_skill_gap(message: str, student, db: Session) -> Optional[str]:
    role = _detect_role(message)
    if not student or not role:
        return None
    try:
        gap = skill_gap.analyze_skill_gap(student.technical_skills, student.soft_skills, role)
    except ValueError:
        return None
    guidance = career_guidance.generate_guidance(student.technical_skills, student.soft_skills, role)
    missing = gap["missing_technical_skills"]
    missing_txt = ", ".join(missing) if missing else "none — your technical skills already match!"
    certs = ", ".join(gap["recommended_certifications"][:3]) or "no extra certifications needed right now"
    return (
        f"For {role}, you're at {gap['match_percentage']}% skill match. "
        f"Missing technical skills: {missing_txt}. "
        f"Recommended certifications: {certs}. {guidance['narrative']}"
    )


def _answer_resume(message: str, student, db: Session) -> Optional[str]:
    if not student:
        return None
    resume = (
        db.query(db_models.Resume)
        .filter(db_models.Resume.student_id == student.id)
        .order_by(db_models.Resume.uploaded_at.desc())
        .first()
    )
    if not resume:
        return None
    missing = ", ".join(resume.missing_keywords[:8]) if resume.missing_keywords else "none found"
    return (
        f"Your latest resume scores {resume.ats_score}% ATS compatibility, "
        f"{resume.resume_quality_score}% overall resume quality, and {resume.semantic_score}% AI semantic "
        f"match against your target role. Missing keywords: {missing}."
    )


def _answer_prediction(message: str, student, db: Session) -> Optional[str]:
    if not student:
        return None
    record = (
        db.query(db_models.PredictionRecord)
        .filter(db_models.PredictionRecord.student_id == student.id)
        .order_by(db_models.PredictionRecord.created_at.desc())
        .first()
    )
    if not record:
        return None
    positives = ", ".join(record.top_positive_factors[:3]) or "no strong positive factors yet"
    negatives = ", ".join(record.top_negative_factors[:3]) or "no major weak points"
    return (
        f"Your latest placement readiness score is {record.readiness_score}% ({record.readiness_label}), "
        f"with {record.confidence_score}% model confidence. Helping you most: {positives}. "
        f"Holding you back: {negatives}."
    )


def _answer_jobs(message: str, student, db: Session) -> Optional[str]:
    if not student:
        return None
    resume = (
        db.query(db_models.Resume)
        .filter(db_models.Resume.student_id == student.id)
        .order_by(db_models.Resume.uploaded_at.desc())
        .first()
    )
    resume_text = resume.raw_text if resume else None
    recs = job_recommend.recommend_jobs(student.technical_skills, resume_text=resume_text, top_n=3)
    if not recs:
        return None
    lines = "; ".join(f"{r['role']} ({r['match_score']}% match)" for r in recs)
    return (
        f"Your top role matches right now: {lines}. "
        "Open 'Job Recommendations' to see real live postings and internships, with LinkedIn apply links, for any of these."
    )


def _answer_learning(message: str, student, db: Session) -> Optional[str]:
    skill = _detect_skill(message)
    if not skill:
        return None
    bundle = skill_resources.get_resources(skill)
    lines = " | ".join(f"{r['label']}: {r['title']}" for r in bundle["resources"].values())
    return f"Here's where to learn {skill}: {lines}"


def _answer_semester(message: str, student, db: Session) -> Optional[str]:
    if not student:
        return None
    records = (
        db.query(db_models.SemesterRecord)
        .filter(db_models.SemesterRecord.student_id == student.id)
        .order_by(db_models.SemesterRecord.semester_number.asc())
        .all()
    )
    if not records:
        return None
    trend = ", ".join(f"Sem {r.semester_number}: {r.sgpa} SGPA" for r in records)
    return f"Your semester trend so far: {trend}."


# Maps an intent to the function that tries to build a real, data-grounded
# answer for it. If the builder returns None (missing student/data/role),
# get_reply() falls through to the canned navigation-style response.
ANSWER_BUILDERS = {
    "skill_gap": _answer_skill_gap,
    "resume_help": _answer_resume,
    "placement_prediction": _answer_prediction,
    "job_search": _answer_jobs,
    "learning_resources": _answer_learning,
    "semester_progress": _answer_semester,
}


def get_reply(message: str, student_id: Optional[int] = None, db: Optional[Session] = None) -> dict:
    """
    Returns {"reply": str, "intent": str, "confidence": float, "grounded": bool}.

    When `student_id` and `db` are supplied, the chatbot tries to answer
    with the student's real numbers (skill gap %, ATS score, readiness
    score, top job matches, ...) instead of only pointing at a page.
    """
    intent, confidence = classify_intent(message)
    confidence = round(confidence * 100, 1)
    student = _get_student(student_id, db)

    builder = ANSWER_BUILDERS.get(intent["intent"])
    if builder is not None:
        grounded = builder(message, student, db)
        if grounded:
            return {"reply": grounded, "intent": intent["intent"], "confidence": confidence, "grounded": True}

    reply = random.choice(intent["responses"])
    return {"reply": reply, "intent": intent["intent"], "confidence": confidence, "grounded": False}

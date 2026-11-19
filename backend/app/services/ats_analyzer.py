"""
Module 3 - ATS Resume Analyzer (Priority 1 - "Real AI Resume Analysis").

Scores a resume against a blend of signals rather than keyword matching
alone:
  - keyword_score          exact/alias-aware skill-vocabulary coverage
  - semantic_score          TF-IDF/cosine similarity between the resume's
                             full text and the target role's requirement
                             corpus (see app/services/nlp_semantic.py) -
                             this is the "NLP + semantic analysis + AI"
                             layer the original version was missing
  - section_score           resume structure completeness
  - length_score            formatting/length heuristic

and reports missing keywords relative to a target job role's requirement
list.
"""
import json
import os
from typing import List

from app.services.nlp_pipeline import clean_text, segment_sections
from app.services.nlp_semantic import role_corpus, semantic_similarity

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
with open(os.path.join(DATA_DIR, "industry_skills.json")) as f:
    INDUSTRY_SKILLS = json.load(f)

REQUIRED_SECTIONS = ["Experience", "Education", "Skills", "Projects"]


def _section_completeness_score(text: str) -> float:
    """Share of the core resume sections detected by the NLP section
    segmenter (header recognition), not a raw substring search."""
    detected = segment_sections(clean_text(text))
    present = sum(1 for s in REQUIRED_SECTIONS if s in detected)
    if present == 0:  # resume without recognisable headers: fall back to keywords
        low = text.lower()
        present = sum(1 for s in ("experience", "education", "skills", "project") if s in low)
    return round((present / len(REQUIRED_SECTIONS)) * 100, 2)


def _length_score(text: str) -> float:
    word_count = len(text.split())
    if word_count < 150:
        return 40.0   # too thin
    if word_count > 1200:
        return 60.0   # likely too verbose for ATS parsing
    return 100.0


def analyze_ats(resume_text: str, extracted_skills: List[str], target_role: str) -> dict:
    role_data = INDUSTRY_SKILLS.get(target_role, {})
    required_skills = [s.lower() for s in role_data.get("technical_skills", [])]

    extracted_lower = [s.lower() for s in extracted_skills]
    matched = [s for s in required_skills if s in extracted_lower]
    missing = [s for s in required_skills if s not in extracted_lower]

    keyword_score = (len(matched) / len(required_skills) * 100) if required_skills else 50.0
    section_score = _section_completeness_score(resume_text)
    length_score = _length_score(resume_text)
    semantic_score = semantic_similarity(resume_text, role_corpus(role_data)) if role_data else 0.0

    # Weighted ATS compatibility score - keyword coverage is still the
    # single biggest factor (real ATS systems rank on it heavily) but
    # semantic alignment now carries real weight instead of being ignored.
    ats_score = round(
        0.40 * keyword_score + 0.25 * semantic_score + 0.20 * section_score + 0.15 * length_score, 2
    )
    resume_quality_score = round(
        0.20 * keyword_score + 0.20 * semantic_score + 0.35 * section_score + 0.25 * length_score, 2
    )

    return {
        "ats_score": min(ats_score, 100.0),
        "resume_quality_score": min(resume_quality_score, 100.0),
        "semantic_score": semantic_score,
        "missing_keywords": missing,
        "matched_keywords": matched,
        "section_completeness": section_score,
    }

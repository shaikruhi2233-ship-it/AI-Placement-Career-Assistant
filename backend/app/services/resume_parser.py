"""
Module 2 - Resume Parsing.

Extracts raw text from PDF/DOCX resumes and runs the NLP pipeline
(app/services/nlp_pipeline.py) for skill entity linking, plus line-level
extraction of education and experience entries.
"""
import io
import re
from typing import List, Tuple

import PyPDF2
import docx

from app.data.skill_vocabulary import (
    TECHNICAL_SKILLS, SOFT_SKILLS, EDUCATION_KEYWORDS, EXPERIENCE_KEYWORDS
)
from app.services.nlp_pipeline import link_skills


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract raw text from an uploaded PDF or DOCX resume."""
    lower = filename.lower()
    if lower.endswith(".pdf"):
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if lower.endswith(".docx"):
        document = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in document.paragraphs)
    # Fallback: treat as plain text
    return file_bytes.decode("utf-8", errors="ignore")


def extract_skills(text: str) -> Tuple[List[str], List[str]]:
    """Skill entity linking (technical + soft skills) via the NLP pipeline:
    alias-aware, token-boundary-safe matching (see app/services/nlp_pipeline.py)."""
    return link_skills(text)


def extract_education(text: str) -> List[str]:
    lines = text.split("\n")
    hits = []
    for line in lines:
        low = line.lower()
        if any(kw in low for kw in EDUCATION_KEYWORDS):
            cleaned = line.strip()
            if cleaned and cleaned not in hits:
                hits.append(cleaned)
    return hits[:10]


def extract_experience(text: str) -> List[str]:
    lines = text.split("\n")
    hits = []
    for line in lines:
        low = line.lower()
        if any(kw in low for kw in EXPERIENCE_KEYWORDS):
            cleaned = line.strip()
            if cleaned and cleaned not in hits:
                hits.append(cleaned)
    return hits[:10]


def parse_resume(file_bytes: bytes, filename: str) -> dict:
    text = extract_text(file_bytes, filename)
    technical_skills, soft_skills = extract_skills(text)
    return {
        "raw_text": text,
        "technical_skills": technical_skills,
        "soft_skills": soft_skills,
        "education": extract_education(text),
        "experience": extract_experience(text),
    }

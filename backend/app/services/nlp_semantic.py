"""
NLP + Semantic Analysis layer (Priority 1 - "Real AI Resume Analysis").

The original implementation matched resumes to roles using plain
substring/keyword lookup only. This module adds two things on top of
that, without removing it:

1. Alias/abbreviation normalisation, so "JS", "K8s", "ML" etc. are
   recognised as the same skill as "javascript", "kubernetes",
   "machine learning" - something pure keyword matching misses.
2. A TF-IDF + cosine-similarity *semantic* similarity score between a
   resume's full text and a role's requirement corpus (its skills,
   certifications and projects joined into one document). This captures
   overall alignment even when the resume doesn't use the exact
   vocabulary string the role dataset uses.

Both scikit-learn primitives used here (`TfidfVectorizer`,
`cosine_similarity`) are already a project dependency. The function
signatures are intentionally small and dependency-light so a heavier
embedding model (e.g. `sentence-transformers`, referenced in the
project's algorithm table as Sentence-BERT) can be dropped in behind
`semantic_similarity()` later without touching any calling code.
"""
import re
from typing import Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Common abbreviations / aliases seen on student resumes, mapped to the
# canonical skill name used across industry_skills.json, courses.json etc.
SKILL_ALIASES: Dict[str, str] = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "k8s": "kubernetes",
    "ml": "machine learning",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "oop": "object oriented programming",
    "dsa": "data structures",
    "db": "database",
    "ai": "artificial intelligence",
    "gcp": "google cloud platform",
    "aws": "amazon web services",
    "reactjs": "react",
    "react.js": "react",
    "node": "node.js",
    "nodejs": "node.js",
    "postgres": "postgresql",
    "rdbms": "sql",
    "oops": "object oriented programming",
    "tf": "tensorflow",
}


def normalize_text(text: str) -> str:
    """Canonicalise skill aliases before matching/embedding so surface-form
    differences (resume says "JS", role requires "javascript") don't cause
    a false miss. Single-pass and token-boundary-safe (see nlp_pipeline)."""
    from app.services.nlp_pipeline import normalize_for_matching
    return normalize_for_matching(text)


def expand_skills_from_text(text: str, vocabulary: List[str]) -> List[str]:
    """Alias-aware skill detection restricted to `vocabulary`."""
    from app.services.nlp_pipeline import link_skills
    technical, soft = link_skills(text)
    wanted = {v.lower() for v in vocabulary}
    return [s for s in technical + soft if s in wanted]


def role_corpus(role_data: dict) -> str:
    """Builds a single 'job description' style document for a role out of
    its structured requirement fields, for semantic comparison."""
    parts = (
        list(role_data.get("technical_skills", []))
        + list(role_data.get("soft_skills", []))
        + list(role_data.get("certifications", []))
        + list(role_data.get("projects", []))
    )
    return " ".join(parts)


def semantic_similarity(resume_text: str, role_text: str) -> float:
    """Cosine similarity (0-100) between resume text and a role's
    requirement corpus, using TF-IDF vectors as a lightweight stand-in for
    sentence embeddings. Returns 0.0 when either document is empty."""
    doc_a, doc_b = normalize_text(resume_text), normalize_text(role_text)
    if not doc_a.strip() or not doc_b.strip():
        return 0.0
    try:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=3000)
        matrix = vectorizer.fit_transform([doc_a, doc_b])
        score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    except ValueError:
        # Happens if, after stop-word removal, a document is empty.
        return 0.0
    return round(float(score) * 100, 2)

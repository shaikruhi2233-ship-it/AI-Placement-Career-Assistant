"""
Module - Skill-specific Learning Resources (Priority 4).

For any skill (matched from the vocabulary, or typed in freely), returns
a categorized bundle of learning resources: video, structured notes,
official documentation, a structured course, a practice platform, and a
project idea — the "click a missing skill -> get the full learning
stack" flow from the feature spec:

    🎥 YouTube   📚 Notes   📖 Documentation
    🎓 Course    🧪 Practice   💻 Project
"""
import json
import os
from typing import Dict

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
with open(os.path.join(DATA_DIR, "skill_resources.json")) as f:
    SKILL_RESOURCES = json.load(f)

CATEGORY_ORDER = ["youtube", "notes", "documentation", "course", "practice", "project"]
CATEGORY_LABELS = {
    "youtube": "🎥 YouTube",
    "notes": "📚 Notes",
    "documentation": "📖 Documentation",
    "course": "🎓 Course",
    "practice": "🧪 Practice",
    "project": "💻 Project",
}


def _fallback(skill: str) -> Dict[str, dict]:
    """Generated search links for a skill that isn't in the curated set, so
    every skill in the system — not only the pre-authored ones — always
    resolves to something clickable."""
    query = skill.replace(" ", "+")
    return {
        "youtube": {"title": f"{skill} crash course", "url": f"https://www.youtube.com/results?search_query={query}+tutorial"},
        "notes": {"title": f"{skill} notes", "url": f"https://www.geeksforgeeks.org/?s={query}"},
        "documentation": {"title": f"{skill} official documentation", "url": f"https://www.google.com/search?q={query}+official+documentation"},
        "course": {"title": f"{skill} course", "url": f"https://www.coursera.org/search?query={query}"},
        "practice": {"title": f"{skill} practice problems", "url": "https://www.hackerrank.com/domains"},
        "project": {"title": f"Build a {skill} project", "url": f"https://github.com/search?q={query}+project&type=repositories"},
    }


def get_resources(skill: str) -> dict:
    key = skill.strip().lower()
    curated = SKILL_RESOURCES.get(key)
    fallback = _fallback(skill)

    bundle = {}
    for cat in CATEGORY_ORDER:
        entry = curated.get(cat) if curated else None
        entry = entry or fallback[cat]
        bundle[cat] = {"label": CATEGORY_LABELS[cat], "title": entry["title"], "url": entry["url"]}

    return {"skill": skill, "resources": bundle}

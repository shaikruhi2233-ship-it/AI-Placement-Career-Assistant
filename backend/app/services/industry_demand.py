"""
Module 5 - Industry Demand Analyzer (novel contribution) (Priority 6 -
"Real-time Industry Demand").

Combines the maintained trends dataset with a *computed* pipeline over
current job postings, matching the problem statement's expected flow:

    current job data (real_jobs.json)
        -> technology frequency count
        -> skill demand ranking
        -> trending roles by open-postings count

The postings dataset is the same one used by
`job_recommend.real_job_opportunities`, so both modules stay consistent.
In production this feed would be refreshed periodically from job-board
APIs / a scraping pipeline instead of a static file.
"""
import json
import os
from collections import Counter
from typing import List

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
with open(os.path.join(DATA_DIR, "industry_trends.json")) as f:
    TRENDS = json.load(f)
with open(os.path.join(DATA_DIR, "real_jobs.json")) as f:
    REAL_JOBS = json.load(f)


def _skill_demand_from_postings() -> List[dict]:
    """technology frequency -> skill demand statistics."""
    counter = Counter()
    total_postings = 0
    for postings in REAL_JOBS.values():
        for post in postings:
            total_postings += 1
            for skill in post.get("required_skills", []):
                counter[skill.lower()] += 1

    return [
        {
            "skill": skill,
            "postings_mentioning": count,
            "demand_share": round(count / total_postings * 100, 1) if total_postings else 0.0,
        }
        for skill, count in counter.most_common(15)
    ]


def _role_demand_from_postings() -> List[dict]:
    """skill demand -> trending roles, ranked by current open-postings count."""
    return sorted(
        [{"role": role, "open_postings": len(postings)} for role, postings in REAL_JOBS.items()],
        key=lambda r: r["open_postings"],
        reverse=True,
    )


def get_industry_demand() -> dict:
    return {
        "trending_technologies": TRENDS["trending_technologies"],
        "trending_roles": TRENDS["trending_roles"],
        "emerging_languages": TRENDS["emerging_languages"],
        "computed_skill_demand": _skill_demand_from_postings(),
        "computed_role_demand": _role_demand_from_postings(),
    }

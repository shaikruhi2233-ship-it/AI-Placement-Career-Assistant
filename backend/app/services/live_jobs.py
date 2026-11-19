"""
Live Job & Internship Fetcher (Priority 3, extended — "real-time job and
internship" listings).

Calls the free, key-less Remotive job-board API (https://remotive.com/api)
in real time and maps the results into the same shape used everywhere else
in the app (company, location, job type, required skills, match %, apply
link, plus a posting date). Remotive tags some listings with
`job_type == "internship"`, which is used to split real jobs from real
internships.

If the live call fails for any reason — no internet from this machine,
the API is down, a timeout — it falls back to the curated sample dataset
in app/data/real_jobs.json (via job_recommend.real_job_opportunities), so
the feature degrades gracefully instead of breaking the page. Every
result is tagged with `source` ("Live" or "Sample") so the frontend can
be transparent about which one is showing.
"""
import html
import re
import urllib.parse
from typing import List, Optional

import requests

from app.services.job_recommend import INDUSTRY_SKILLS, real_job_opportunities

REMOTIVE_URL = "https://remotive.com/api/remote-jobs"
REQUEST_TIMEOUT = 6  # seconds — fail fast and fall back rather than hang the request


def linkedin_search_link(role: str, company: Optional[str] = None, location: Optional[str] = None) -> str:
    """Real, working deep link into LinkedIn's own job search — not scraped
    or fabricated data. LinkedIn doesn't offer a public/key-less API to
    fetch individual postings (that needs a Talent Solutions partnership),
    so this is the legitimate way to send a student straight to real,
    live LinkedIn listings for the role (optionally narrowed to one
    company), where they can use LinkedIn's own Apply / Easy Apply."""
    keywords = f"{role} {company}".strip() if company else role
    params = {"keywords": keywords}
    if location and location.lower() not in ("remote", "worldwide", ""):
        params["location"] = location
    return "https://www.linkedin.com/jobs/search/?" + urllib.parse.urlencode(params)


def _strip_html(text: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", text or ""))


def _extract_required_skills(description: str, role: str) -> List[str]:
    vocabulary = [s.lower() for s in INDUSTRY_SKILLS.get(role, {}).get("technical_skills", [])]
    text = _strip_html(description).lower()
    found = [s for s in vocabulary if re.search(rf"\b{re.escape(s)}\b", text)]
    return found or INDUSTRY_SKILLS.get(role, {}).get("technical_skills", [])[:5]


def _search_term_for_role(role: str) -> str:
    # Remotive's free-text search matches better on the core role words
    # than the full formal title (e.g. "machine learning" beats
    # "Machine Learning Engineer").
    stripped = role.replace("Engineer", "").replace("Developer", "").strip()
    return stripped or role


def _fetch_remotive(role: str, want_internship: bool, limit: int) -> Optional[List[dict]]:
    try:
        resp = requests.get(
            REMOTIVE_URL,
            params={"search": _search_term_for_role(role), "limit": 30},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        payload = resp.json()
    except Exception:
        return None  # signals the caller to fall back to the sample dataset

    jobs = payload.get("jobs", [])
    filtered = [j for j in jobs if (j.get("job_type") == "internship") == want_internship]

    results = []
    for j in filtered[:limit]:
        job_type_raw = j.get("job_type", "full_time")
        company = j.get("company_name") or "Unknown"
        location = j.get("candidate_required_location") or "Remote"
        results.append({
            "role": role,
            "company": company,
            "location": location,
            "job_type": "Internship" if job_type_raw == "internship" else job_type_raw.replace("_", " ").title(),
            "required_skills": _extract_required_skills(j.get("description", ""), role),
            "apply_link": j.get("url", "https://remotive.com/"),
            "linkedin_link": linkedin_search_link(role, company, location),
            "posted_date": (j.get("publication_date") or "")[:10],
            "source": "Live",
        })
    return results


def get_job_opportunities(
    role: str,
    student_technical: Optional[List[str]] = None,
    want_internships: bool = False,
    limit: int = 6,
) -> List[dict]:
    """Priority 3 (extended) — real-time job/internship postings for a
    role, with an automatic offline fallback to the curated sample
    dataset."""
    student_skills = {s.lower() for s in (student_technical or [])}
    live = _fetch_remotive(role, want_internships, limit)

    if live:
        for item in live:
            required = [s.lower() for s in item["required_skills"]]
            matched = [s for s in required if s in student_skills]
            item["match_score"] = round((len(matched) / len(required)) * 100, 2) if required else 0.0
        return live

    # Fallback: curated sample dataset (no internet available right now).
    fallback = real_job_opportunities(role, student_technical)
    is_internship = lambda f: f["job_type"].strip().lower() == "internship"
    fallback = [f for f in fallback if is_internship(f) == want_internships]
    for item in fallback:
        item["source"] = "Sample"
        item["posted_date"] = ""
        item["linkedin_link"] = linkedin_search_link(role, item["company"], item["location"])
    return fallback

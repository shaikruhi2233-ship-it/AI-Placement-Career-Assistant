"""
Module - LinkedIn & GitHub Job and Internship Recommendations.

Ships with a curated, skill-matched sample dataset so the project works
without any API credentials. LinkedIn's official Jobs API requires a
partnership agreement, and GitHub Jobs was deprecated — so real
integrations typically go through:
  - LinkedIn: the Talent/Jobs API (partner access) or authorized scraping
    via a licensed provider.
  - GitHub: the "Jobs" ecosystem now lives in third-party boards, but
    GitHub's REST API (`/search/repositories`) can surface repos tagged
    "good first issue" / "hiring" for open-source-based internship leads.

Swap `_SAMPLE_LINKEDIN` / `_SAMPLE_GITHUB` below for real API calls without
changing the router or frontend — `recommend_external_opportunities()` is
the single call site.
"""
from typing import List

_SAMPLE_LINKEDIN = [
    {"title": "Software Engineer Intern", "company_or_org": "Flipkart", "type": "Internship",
     "url": "https://www.linkedin.com/jobs/", "location": "Bengaluru, India",
     "required_skills": ["python", "data structures", "git", "sql"]},
    {"title": "Junior Data Analyst", "company_or_org": "Deloitte", "type": "Job",
     "url": "https://www.linkedin.com/jobs/", "location": "Hyderabad, India",
     "required_skills": ["sql", "excel", "power bi", "python"]},
    {"title": "Frontend Developer Intern", "company_or_org": "Zoho", "type": "Internship",
     "url": "https://www.linkedin.com/jobs/", "location": "Chennai, India",
     "required_skills": ["react", "javascript", "html", "css"]},
    {"title": "Machine Learning Engineer", "company_or_org": "Fractal Analytics", "type": "Job",
     "url": "https://www.linkedin.com/jobs/", "location": "Mumbai, India",
     "required_skills": ["python", "scikit-learn", "tensorflow", "sql"]},
    {"title": "DevOps Intern", "company_or_org": "Freshworks", "type": "Internship",
     "url": "https://www.linkedin.com/jobs/", "location": "Chennai, India",
     "required_skills": ["linux", "docker", "aws", "bash"]},
    {"title": "Business Analyst", "company_or_org": "Genpact", "type": "Job",
     "url": "https://www.linkedin.com/jobs/", "location": "Gurugram, India",
     "required_skills": ["sql", "excel", "jira", "communication"]},
]

_SAMPLE_GITHUB = [
    {"title": "Open Source Contributor — REST API project", "company_or_org": "FastAPI Community",
     "type": "Internship", "url": "https://github.com/topics/fastapi",
     "location": "Remote", "required_skills": ["python", "fastapi", "rest api", "git"]},
    {"title": "Good First Issues — React Dashboard", "company_or_org": "Open Source (React)",
     "type": "Internship", "url": "https://github.com/topics/react",
     "location": "Remote", "required_skills": ["react", "javascript", "css"]},
    {"title": "ML Model Contributor — scikit-learn ecosystem", "company_or_org": "Open Source (scikit-learn)",
     "type": "Internship", "url": "https://github.com/topics/scikit-learn",
     "location": "Remote", "required_skills": ["python", "scikit-learn", "pandas"]},
    {"title": "DevOps Tooling Contributor — Kubernetes ecosystem", "company_or_org": "Open Source (CNCF)",
     "type": "Internship", "url": "https://github.com/topics/kubernetes",
     "location": "Remote", "required_skills": ["docker", "kubernetes", "bash"]},
]


def _score(student_skills: List[str], required: List[str]) -> float:
    student_lower = {s.lower() for s in student_skills}
    required_lower = [s.lower() for s in required]
    if not required_lower:
        return 0.0
    matched = sum(1 for s in required_lower if s in student_lower)
    return round((matched / len(required_lower)) * 100, 2)


def recommend_external_opportunities(student_skills: List[str], top_n: int = 5) -> List[dict]:
    results = []
    for item in _SAMPLE_LINKEDIN:
        results.append({
            "source": "LinkedIn",
            "type": item["type"],
            "title": item["title"],
            "company_or_org": item["company_or_org"],
            "match_score": _score(student_skills, item["required_skills"]),
            "url": item["url"],
            "location": item["location"],
        })
    for item in _SAMPLE_GITHUB:
        results.append({
            "source": "GitHub",
            "type": item["type"],
            "title": item["title"],
            "company_or_org": item["company_or_org"],
            "match_score": _score(student_skills, item["required_skills"]),
            "url": item["url"],
            "location": item["location"],
        })
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:top_n]

"""
Module - Semester-wise Student Improvement Tracking.

Lets a student log per-semester academic records (SGPA, attendance,
backlogs, skills gained) and computes a trend summary comparing the
earliest and latest semesters, which also feeds into the placement
readiness narrative shown on the dashboard.
"""
from typing import List


def compute_trend(records: List[dict]) -> dict:
    if len(records) < 2:
        return {
            "sgpa_change": 0.0,
            "attendance_change": 0.0,
            "improvement_summary": "Log at least two semesters to see an improvement trend.",
        }

    ordered = sorted(records, key=lambda r: r["semester_number"])
    first, last = ordered[0], ordered[-1]

    sgpa_change = round(last["sgpa"] - first["sgpa"], 2)
    attendance_change = round(last["attendance"] - first["attendance"], 2)

    if sgpa_change > 0.3:
        trend_desc = "Strong upward trend in academic performance."
    elif sgpa_change < -0.3:
        trend_desc = "SGPA has declined — consider revisiting study habits and time management."
    else:
        trend_desc = "SGPA has remained relatively stable across semesters."

    if last["backlogs"] > 0:
        trend_desc += f" {last['backlogs']} active backlog(s) — clearing these will improve placement eligibility."

    return {
        "sgpa_change": sgpa_change,
        "attendance_change": attendance_change,
        "improvement_summary": trend_desc,
    }

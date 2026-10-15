"""
Module - Coding Tests.

Runs a student's submitted Python code against a bank of practice problems
with hidden test cases, executing each in an isolated subprocess with a
strict timeout and capturing stdout for comparison.

SECURITY NOTE: subprocess isolation with a timeout is sufficient for a
local/trusted demo environment, but is NOT a hardened sandbox. For a
public-facing deployment, run submissions inside a locked-down container
(no network, restricted filesystem, resource limits via cgroups) or a
managed code-execution API.
"""
import json
import os
import subprocess
import sys
import tempfile
from typing import List

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
with open(os.path.join(DATA_DIR, "coding_problems.json")) as f:
    PROBLEM_BANK = json.load(f)

TIMEOUT_SECONDS = 5


def _all_problems() -> List[dict]:
    problems = []
    for difficulty, items in PROBLEM_BANK.items():
        problems.extend(items)
    return problems


def list_problems(difficulty: str = None) -> List[dict]:
    if difficulty:
        return PROBLEM_BANK.get(difficulty, [])
    return _all_problems()


def get_problem(problem_id: str) -> dict:
    for p in _all_problems():
        if p["id"] == problem_id:
            return p
    raise ValueError(f"Unknown problem id '{problem_id}'")


def run_submission(problem_id: str, code: str) -> dict:
    problem = get_problem(problem_id)
    test_cases = problem["test_cases"]

    passed = 0
    error_message = ""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        script_path = f.name

    try:
        for case in test_cases:
            try:
                result = subprocess.run(
                    [sys.executable, script_path],
                    input=case["input"],
                    capture_output=True,
                    text=True,
                    timeout=TIMEOUT_SECONDS,
                )
                actual = result.stdout.strip()
                expected = case["expected_output"].strip()
                if result.returncode != 0:
                    error_message = result.stderr.strip()[:500]
                    continue
                if actual == expected:
                    passed += 1
            except subprocess.TimeoutExpired:
                error_message = f"Time limit exceeded ({TIMEOUT_SECONDS}s)"
    finally:
        os.unlink(script_path)

    total = len(test_cases)
    score = round((passed / total) * 100, 2) if total else 0.0

    return {
        "problem_id": problem_id,
        "difficulty": problem["difficulty"],
        "passed_test_cases": passed,
        "total_test_cases": total,
        "score": score,
        "passed": 1 if passed == total else 0,
        "error_message": error_message,
    }

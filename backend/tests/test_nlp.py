"""
Self-test for the NLP modules - run from the backend/ folder:

    python tests/test_nlp.py

Checks (1) skill entity linking, including the tricky cases that plain
keyword matching gets wrong, (2) the rule-based NER, (3) section
segmentation, and (4) chatbot intent classification accuracy on a set of
test questions (with typos and off-topic questions).
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.nlp_pipeline import analyze, link_skills  # noqa: E402
from app.services.job_recommend import INDUSTRY_SKILLS  # noqa: E402

SAMPLE = """T. Anitha
anitha.t@gmail.com | +91 98765 43210 | linkedin.com/in/anitha-t | github.com/anitha-dev
Career Objective
MCA student seeking a Full Stack Developer role.
Education
MCA, Sree Vidyanikethan Engineering College, 2025 - 2027, CGPA: 8.4/10
Technical Skills
Languages: C, C++, Python, JavaScript
Web: HTML, CSS, React.js, Node.js, RESTful APIs
Databases: MySQL, MongoDB
Cloud: Amazon Web Services, GCP | Testing: Selenium, Postman
Projects
Developed a placement assistant with React and FastAPI used by 120+ students.
Internship
Web Development Intern, Techwave Solutions Pvt Ltd, 2024
"""

passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}")


print("1. Skill entity linking")
tech, _ = link_skills(SAMPLE)
for skill in ["aws", "gcp", "c++", "c", "react", "node.js", "rest api", "sql", "selenium"]:
    check(f"detects {skill}", skill in tech)
check("'Download my CV' is NOT computer vision", "computer vision" not in link_skills("Download my CV")[0])
check("'Grade C' is NOT the C language", "c" not in link_skills("Got grade C in maths")[0])
check("'React.js' does NOT imply JavaScript", "javascript" not in link_skills("React.js developer")[0])

print("2. Named entities")
r = analyze(SAMPLE, INDUSTRY_SKILLS, "Full Stack Developer")
check("email", r["entities"]["EMAIL"] == ["anitha.t@gmail.com"])
check("phone", len(r["entities"]["PHONE"]) == 1)
check("linkedin + github links", len(r["entities"]["LINK"]) == 2)
check("degree MCA", "MCA" in r["entities"]["DEGREE"])
check("CGPA", any("8.4" in s for s in r["entities"]["SCORE"]))

print("3. Section segmentation")
for sec in ["Summary", "Education", "Skills", "Projects", "Experience"]:
    check(f"section {sec}", sec in r["sections"]["detected"])
check("top semantic role is Full Stack Developer", r["role_similarity"][0]["role"] == "Full Stack Developer")

print("4. Chatbot intent classification")
try:
    import types
    sys.modules.setdefault("app.db_models", types.ModuleType("app.db_models"))
    from app.services.chatbot import classify_intent
    tests = [
        ("hi", "greeting"), ("what is my ats score?", "resume_help"), ("how to improve my resum", "resume_help"),
        ("which skills am i missing for data analyst", "skill_gap"), ("tips for hr intervew", "interview_prep"),
        ("am i ready for placement", "placement_prediction"), ("find me internships", "job_search"),
        ("best course to learn react", "learning_resources"), ("how is my sgpa trend", "semester_progress"),
        ("thank u", "thanks"), ("what is the weather today", "fallback"), ("who won the cricket match", "fallback"),
    ]
    correct = sum(classify_intent(q)[0]["intent"] == exp for q, exp in tests)
    check(f"intent accuracy {correct}/{len(tests)}", correct >= len(tests) - 1)
except ImportError as e:  # sqlalchemy missing outside the venv
    print("  SKIP  chatbot test:", e)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)

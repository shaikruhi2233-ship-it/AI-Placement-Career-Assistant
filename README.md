# AI Placement and Career Assistant

An Intelligent AI-Based Placement Readiness Prediction and Career Guidance
System with Explainable Recommendations.

This project is a working full-stack implementation of 16 modules: Student
Profile Management, Resume Parsing, ATS Resume Analyzer, Skill Gap
Analysis, Industry Demand Analyzer, Personalized Career Roadmap, Learning
Portals, Semester-wise Improvement Tracking, Coding Tests, AI Mock
Interview, Placement Readiness Prediction, Explainable AI, Job
Recommendation, LinkedIn & GitHub Opportunities, an AI Career Chatbot, and
an Analytics Dashboard.

```
project/
├── backend/     FastAPI + SQLite API, ML model, NLP/ATS/skill-gap logic
└── frontend/    React (Vite) single-page app that consumes the API
```

## Latest update - NLP pipeline, model evaluation and UI redesign

**NLP (resume intelligence)** - `app/services/nlp_pipeline.py`, shown on the *Resume & ATS* page:
1. Preprocessing - cleaning, sentence segmentation, tokenisation, stop-word removal, rule-based lemmatisation
2. Section segmentation - Summary / Education / Skills / Projects / Experience / Certifications / Achievements
3. Rule-based named-entity recognition - EMAIL, PHONE, LINK, DEGREE, SCORE (CGPA / %), YEAR, ORG
4. Skill entity linking - alias-aware, token-boundary-safe matching ("JS" -> javascript, "Amazon Web Services" -> aws),
   fixing earlier false negatives (AWS, NLP, GCP, C++) and false positives ("CV" -> computer vision, "React.js" -> javascript)
5. TF-IDF keyword extraction (uni + bi-grams) against the industry role corpus
6. Writing-quality analysis - action verbs, quantified achievements, weak phrases
7. Semantic role similarity - TF-IDF vectors + cosine similarity to every role

**Chatbot** - `app/services/chatbot.py`: TF-IDF (word + character n-gram) intent classifier with cosine similarity,
a confidence threshold for out-of-scope questions, and answers grounded in the student's own data.

**Model evaluation** - `app/services/model_evaluation.py`, shown under *Readiness Prediction -> Model performance*:
accuracy, precision, recall, F1, ROC-AUC, confusion matrix and 5-fold cross-validation on the 20% held-out split,
plus a comparison with Logistic Regression, Decision Tree, KNN and Gradient Boosting.
Training data is synthetic (rule-based ground truth with noise, see `train_model.py`); retrain on real placement
records for production use.

**Self-test** - from `backend/` with the venv active: `python tests/test_nlp.py` (24 checks).

**UI** - new landing, login and register pages, redesigned dashboard (readiness gauge, KPI cards, trend chart,
AI-prioritised next steps from `app/services/dashboard_insights.py`, profile-balance radar, role matches),
grouped sidebar with icons, and a shared design system in `src/index.css`.

### Run on Windows (VS Code terminals)

Terminal 1 - backend:
```
cd project\backend
python -m venv venv            (first time only)
venv\Scripts\activate
pip install -r requirements.txt   (first time only)
uvicorn app.main:app --reload
```
Terminal 2 - frontend:
```
cd project\frontend
npm install                    (first time only)
npm run dev
```
Open http://localhost:5173

## What's new in this version (Priorities 1-6)

This update layers the six priority features requested for the
placement-readiness problem statement on top of the existing 17-module
app, keeping the same **React → FastAPI → SQLAlchemy → SQLite**
architecture end to end (no MongoDB, no parallel backend).

| Priority | What changed | Where |
|---|---|---|
| 1. Real AI Resume Analysis | ATS/resume scoring now blends keyword coverage with a TF-IDF/cosine **semantic similarity** score between the full resume text and a role's requirement corpus, plus alias-aware skill detection (JS→javascript, K8s→kubernetes, ML→machine learning, ...) instead of plain substring matching. | `app/services/nlp_semantic.py`, `app/services/ats_analyzer.py`, `app/services/resume_parser.py` |
| 2. Resume → Multiple Job Roles | Job recommendation now blends skill overlap (70%) with the same semantic score (30%) and returns every role ranked by match % (🥇🥈🥉ready), plus a breakdown of `skill_match` vs `semantic_match`. | `app/services/job_recommend.py`, `app/routers/jobs.py`, `pages/Jobs.jsx` |
| 3. Real Job Opportunities | Live, real-time postings fetched from a job-board API at request time (company / location / job type / required skills / match % / apply link / posted date), split into **Jobs** and **Internships**, each with a real **LinkedIn Jobs search deep link** so students apply/search through LinkedIn directly. Falls back to a curated sample dataset automatically if a live fetch isn't possible. | `app/services/live_jobs.py`, `GET /jobs/opportunities/{role}`, `GET /jobs/internships/{role}`, `pages/Jobs.jsx` |
| 4. Skill-specific Learning Resources | Clicking any missing skill **opens its top learning source in a new tab immediately** (no second click needed) and also lists the full categorized bundle — 🎥 YouTube · 📚 Notes · 📖 Documentation · 🎓 Course · 🧪 Practice · 💻 Project — curated for common skills with a generated-search fallback for anything else. | `app/data/skill_resources.json`, `app/services/skill_resources.py`, `GET /learning/resources/{skill}`, `pages/SkillGap.jsx` |
| 5. AI Career Guidance | New narrative endpoint: *"You are 58% ready for Machine Learning Engineer. First learn Docker and statistics, then build an End-to-end ML pipeline."* | `app/services/career_guidance.py`, `GET /roadmap/guidance/{student_id}`, `pages/Jobs.jsx` |
| 6. Real-time Industry Demand | Industry Demand now also computes technology frequency → skill demand → trending roles **directly from the current job-postings dataset**, alongside the maintained trends file. | `app/services/industry_demand.py`, `pages/Industry.jsx` |

Also added, per follow-up requests:
- **Explainable AI, made readable**: the SHAP feature table now shows clean labels with no underscores (`coding_score` → "Coding Score"), each feature's contribution as a **signed %** (all rows sum to ±100%), the student's actual value for it, and a **High / Medium / Average / Below Average / Low** rating of that value. A new **Performance Status** summary rolls those same ratings up into four categories (Academic, Technical & Project, Resume, Interview). `app/services/ml_model.py`, `pages/Prediction.jsx`.
- **Login/Register branding**: both pages now show the project's full title and "with Explainable Recommendations" tagline from the problem statement above the form. `pages/Login.jsx`, `pages/Register.jsx`.
- **Public landing page**: `/` now shows the project title, subtitle, and Register/Log In buttons for anyone not signed in, instead of jumping straight to the login form. `pages/Landing.jsx`, `App.jsx`.
- **AI Career Chatbot bug fix**: the chatbot's data-grounded answer logic (real skill-gap %, ATS score, readiness score, top job matches — not just "go check this page") already existed in `chatbot.py`, but the router never passed `student_id`/`db` into it, so every reply silently fell back to the canned navigation response. Fixed in `app/routers/chatbot.py` — the chatbot now answers with the student's real numbers whenever it has enough context.
- **Student Snapshot panel**: a right-hand panel now shows the logged-in student's key details (branch, CGPA, attendance, skills/certs/projects counts, latest resume scores, latest readiness score) immediately after login, and refreshes automatically on every page navigation and every 30 seconds. `components/StudentSnapshot.jsx`, `App.jsx`.
- **Professional auth redesign**: Landing, Log In, Register, and the new Forgot Password page now share one polished split-screen layout (`components/AuthLayout.jsx`) — a dark gradient brand panel with the project title/tagline/feature highlights on the left, and a tabbed white form panel on the right, so switching between Log In and Register feels like one continuous page. `pages/Landing.jsx`, `pages/Login.jsx`, `pages/Register.jsx`, `pages/ForgotPassword.jsx`.
- **Forgot Password**: a "Forgot password?" link on the Log In page leads to a reset flow (email + new password). This is a simplified, demo-friendly reset — it verifies the account exists by email and sets the new password directly, since no SMTP/OTP service is configured in this project. `POST /auth/reset-password`, `app/routers/auth.py`, `pages/ForgotPassword.jsx`.
- **Feature Importance table simplified**: the "Contribution %" column (a signed, sometimes-negative SHAP-based number) was replaced with a plain 0-100% **Score %** — your actual value for that feature normalized onto a percentage scale, matching the High/Medium/Average/Below Average/Low rating next to it. `app/services/ml_model.py`, `pages/Prediction.jsx`.
- **Job Recommendations cleanup**: removed the internal "Apply" tracking button from each role card (kept "What should I learn for this role?" and the real LinkedIn/posting apply links, which are the actual useful apply paths). `pages/Jobs.jsx`.
- **Student Profile page**: now shows a read-only "Your Details" summary (all fields, skills as chips, certifications/projects as lists) right when you open the page, above the editable form. `pages/Profile.jsx`.
- **Weekly Roadmap Exam**: each week in the Personalized Career Roadmap now ends with a short multiple-choice exam covering exactly that week's focus skills, with instant scoring and per-question explanations. Backed by a curated question bank covering every technical skill used across all roles, with a generic fallback if a skill isn't in the bank yet. `app/data/skill_quizzes.json`, `app/services/weekly_quiz.py`, `GET /roadmap/week-quiz`, `pages/Roadmap.jsx`.
- **Dashboard redesign**: a "Build Your Career with AI" hero banner (with a clickable Student Profile card linking to `/profile`), a stat strip, and a full **Career Tools** grid covering every tool in the sidebar (Student Profile, Resume & ATS, ATS Analyzer, Skill Gap Analysis, Industry Demand, Career Roadmap, Learning Portals, Semester Progress, Coding Tests, AI Mock Interview, Placement Prediction, Job Recommendations, LinkedIn & GitHub, AI Career Chatbot) — each a clickable card, not just the original 8. `pages/Dashboard.jsx`.
- **Skill Gap resource links, un-forced**: clicking a missing skill no longer auto-opens a YouTube tab — it just shows the categorized resource bundle (video/notes/docs/course/practice/project) so the student picks which one to open. `pages/SkillGap.jsx`.
- **Register → Log In → Dashboard flow**: registering no longer logs the student in automatically. After registering, they land on the Log In tab with a "Account created" banner and sign in explicitly with their new credentials. `pages/Register.jsx`, `pages/Login.jsx`.
- **Weekly Roadmap Exam**: each week in the Personalized Career Roadmap now ends with a short multiple-choice exam on exactly that week's focus skills (curated question bank of 30+ skills, generic fallback questions for anything else), graded instantly with a pass/fail (≥60%) and per-question explanations. `app/data/skill_quizzes.json`, `app/services/weekly_quiz.py`, `GET /roadmap/week-quiz`, `pages/Roadmap.jsx`.
- **Voice-based AI Mock Interview**: a "Voice mode" toggle (Chrome/Edge) lets students have each question read aloud (text-to-speech) and dictate their answer by speaking (speech-to-text via the Web Speech API) instead of typing — voice and typed text can be mixed freely, and the feature degrades gracefully (hidden) in browsers without speech support. `pages/Interview.jsx`.

**Database note:** this update adds new columns to `prediction_records` (`feature_breakdown`, `performance_status`) and `resumes` (`semantic_score`). If you have an existing `placement_assistant.db` from an older run, delete it before restarting the backend so SQLAlchemy recreates the tables with the new columns — otherwise you'll get a "no such column" error.

Database stays SQLite via SQLAlchemy as shipped in this ZIP (see
"Technology stack" below) — no MongoDB mixing. If/when you deploy, swap
`SQLALCHEMY_DATABASE_URL` in `app/database.py` for PostgreSQL/MySQL
without touching any service code.

**Note on live job/internship data:** `app/services/live_jobs.py` calls a
free, key-less job-board API (Remotive) over the internet at request
time. It needs outbound internet access from wherever the backend runs.
If that call fails or times out for any reason, the endpoint
automatically falls back to the curated sample dataset in
`app/data/real_jobs.json` — the response always includes a `source`
field (`"Live"` or `"Sample"`) so the UI can be transparent about which
one is showing.

**Note on LinkedIn:** LinkedIn does not offer a public, key-less API to
fetch individual job postings — pulling real posting data requires a
LinkedIn Talent Solutions partnership. What this project does instead,
honestly, is generate a real, working **LinkedIn job-search deep link**
per posting (`linkedin_link`) and per role ("Search all &lt;role&gt; jobs on
LinkedIn"), which opens LinkedIn's own live search results — where a
student can use LinkedIn's Apply / Easy Apply directly. This is not
scraped or fabricated data; it's a standard deep link into LinkedIn's
own site.

## Quick start

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python train_model.py             # one-time: trains the RandomForest model
uvicorn app.main:app --reload     # http://localhost:8000
```

Interactive API docs (Swagger UI) are auto-generated at
`http://localhost:8000/docs` — useful for testing every endpoint without
the frontend.

The API uses a local SQLite file (`placement_assistant.db`) created
automatically on first run. To use PostgreSQL/MySQL instead, edit
`SQLALCHEMY_DATABASE_URL` in `app/database.py`.

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev                       # http://localhost:5173
```

The Vite dev server proxies `/api/*` requests to `http://localhost:8000`
(see `vite.config.js`), so make sure the backend is running first.

### 3. Using the app

1. Open `http://localhost:5173` — you'll land on the **Login** page.
2. Click **Register here** to create an account (name, email, branch,
   password). This creates your student profile and logs you in
   automatically with a JWT stored in the browser.
3. Go to **Student Profile** to fill in academics, skills, certifications,
   and projects.
4. Upload a resume under **Resume & ATS** — it's parsed automatically and
   scored against a target job role.
5. Explore **Skill Gap Analysis**, **Industry Demand**, and **Career
   Roadmap** for that role.
6. Take a **Mock Interview** (technical / HR / coding).
7. Run **Readiness Prediction** to get a placement-readiness score with a
   SHAP-based explanation of the contributing factors.
8. Check **Job Recommendations** and the **Dashboard** for a consolidated
   view.
9. Use **Log Out** in the sidebar to end your session; log back in any
   time with the same email/password.

## Module → code map

| # | Module | Backend location |
|---|---|---|
| 1 | Student Profile Management | `app/routers/students.py` |
| 2 | Resume Parsing | `app/services/resume_parser.py` |
| 3 | ATS Resume Analyzer | `app/services/ats_analyzer.py` |
| 4 | Skill Gap Analysis | `app/services/skill_gap.py` |
| 5 | Industry Demand Analyzer | `app/services/industry_demand.py` |
| 6 | Personalized Career Roadmap | `app/services/roadmap.py` |
| 7 | AI Mock Interview | `app/services/interview.py` |
| 8 | Placement Readiness Prediction | `app/services/ml_model.py`, `train_model.py` |
| 9 | Explainable AI | `app/services/ml_model.py` (SHAP TreeExplainer) |
| 10 | Job Recommendation | `app/services/job_recommend.py` |
| 11 | Analytics Dashboard | `app/routers/dashboard.py` |
| 12 | Learning Portals | `app/services/learning_portal.py` |
| 13 | Semester-wise Improvement Tracking | `app/services/semester_tracker.py` |
| 14 | Coding Tests | `app/services/coding_test.py` |
| 15 | AI Career Chatbot | `app/services/chatbot.py` |
| 16 | LinkedIn & GitHub Opportunities | `app/services/external_jobs.py` |
| 17 | Job Applications (Apply & Track) | `app/routers/applications.py` |
| — | Authentication (Registration & Login) | `app/routers/auth.py`, `app/services/auth.py` |

## The connected Resume → Jobs → Skill Gap flow

This is the core workflow the app is built around, end to end:

1. **Upload a resume** on the Resume & ATS page for a chosen target role. The
   server extracts your technical/soft skills from the actual resume text
   and merges them into your profile — no manual re-entry.
2. **Job Recommendations** immediately reflects those skills, ranking every
   role by real overlap with your profile (not academic marks).
3. On any recommended role, click **"What should I learn for this role?"**
   — this loads that exact role's Skill Gap (missing technical/soft skills)
   and AI-guided Career Roadmap (weekly plan, certifications, projects)
   inline, without leaving the page.
4. Click **Apply** to log the role in your **Job Tracker** — every applied
   role, company, match score, and status is persisted per-student and
   shown at the bottom of the Job Recommendations page.

This was verified with a live end-to-end test: uploading a resume with
Python/SQL/Excel skills correctly ranked Data Analyst top, surfaced pandas/
Power BI/Tableau/statistics as the missing skills for that role, generated
a matching weekly roadmap, and recorded the application after clicking Apply.

## Notes on the demo data and extension points

This is a fully working reference implementation, built to be extended
rather than a hollow scaffold:

- **ML model**: `train_model.py` trains on a synthetic but transparent
  dataset (a weighted-sum ground truth + noise) so the SHAP explanations
  line up with intuitive placement-readiness factors. Swap
  `generate_synthetic_dataset()` for a loader over your institution's real
  historical placement records to retrain on actual data.
- **Skill/role datasets**: `app/data/industry_skills.json`,
  `industry_trends.json`, `courses.json`, and `interview_questions.json`
  are hand-curated seed datasets. Extend them with more roles, skills, and
  questions, or replace with a live job-board API integration for the
  Industry Demand Analyzer.
- **NLP resume parsing**: `app/services/resume_parser.py` uses
  keyword-matching against a curated vocabulary
  (`app/data/skill_vocabulary.py`). For production-grade Named Entity
  Recognition, swap in a trained spaCy pipeline
  (`nlp = spacy.load("en_core_web_sm")`) without changing the calling code.
- **Mock interview grading**: `app/services/interview.py` scores answers
  via keyword coverage and linguistic heuristics. This is a clearly
  labeled proxy — swap in an LLM-graded rubric for higher-fidelity
  evaluation.
- **Coding test execution**: `app/services/coding_test.py` runs
  submissions in a subprocess with a timeout — adequate for a local/trusted
  demo, but NOT a hardened sandbox. For a public deployment, run
  submissions in a locked-down container (no network, resource limits) or
  a managed code-execution API.
- **AI chatbot**: `app/services/chatbot.py` is a zero-dependency,
  intent-matching FAQ bot so the project runs with no API keys. Swap the
  body of `get_reply()` for an LLM call (e.g. the Anthropic API) with the
  student's dashboard data injected as context, for natural-language,
  personalized responses — the function signature is already designed for
  this upgrade.
- **LinkedIn / GitHub opportunities**: `app/services/external_jobs.py`
  ships with a curated sample dataset, since LinkedIn's Jobs API requires
  a partner agreement and GitHub Jobs was deprecated. See the module
  docstring for how real integrations are typically sourced, and swap the
  sample lists for live API calls without touching the router or frontend.
- **Auth**: JWT-based authentication is implemented — `POST /auth/register`
  and `POST /auth/login` issue a 7-day bearer token (`app/services/auth.py`,
  password hashing via `bcrypt`; token signing via `python-jose`). The
  demo `SECRET_KEY` is hardcoded for convenience — set the
  `JWT_SECRET_KEY` environment variable before any real deployment.
  Currently only the student's own profile update/delete routes enforce
  the token (`Depends(get_current_student)` in `app/routers/students.py`);
  extend the same dependency to other routers if you want per-student
  data fully locked down end-to-end.

## Technology stack

Frontend: React 18, Vite, React Router, Recharts, Axios
Backend: FastAPI, SQLAlchemy, SQLite
AI/ML: scikit-learn (RandomForest), SHAP
NLP: keyword-based extraction (PyPDF2 / python-docx for text extraction)
Coding tests: subprocess-based Python execution with per-testcase timeout
Chatbot: intent-matching (keyword overlap), swappable for an LLM backend

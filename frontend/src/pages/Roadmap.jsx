import React, { useEffect, useState } from "react";
import api from "../api";
import { useStudent } from "../AuthContext";
import NoStudentBanner from "../components/NoStudentBanner";

export default function Roadmap() {
  const { studentId } = useStudent();
  const [roles, setRoles] = useState([]);
  const [targetRole, setTargetRole] = useState("");
  const [roadmap, setRoadmap] = useState(null);
  const [error, setError] = useState("");
  const [exams, setExams] = useState({}); // week -> { questions, answers, submitted, score, loading }

  useEffect(() => {
    api.listRoles().then((r) => { setRoles(r); if (r.length) setTargetRole(r[0]); });
  }, []);

  useEffect(() => {
    if (!studentId || !targetRole) return;
    setError("");
    setExams({});
    api.getRoadmap(studentId, targetRole).then(setRoadmap)
      .catch((err) => setError(err.response?.data?.detail || "Could not generate roadmap."));
  }, [studentId, targetRole]);

  const startExam = async (week, focusSkills) => {
    setExams((prev) => ({ ...prev, [week]: { loading: true } }));
    try {
      const quiz = await api.getWeekQuiz(focusSkills);
      setExams((prev) => ({
        ...prev,
        [week]: {
          loading: false,
          questions: quiz,
          answers: new Array(quiz.length).fill(null),
          submitted: false,
        },
      }));
    } catch {
      setExams((prev) => ({ ...prev, [week]: { loading: false, error: "Could not load the exam." } }));
    }
  };

  const selectAnswer = (week, qIndex, optionIndex) => {
    setExams((prev) => {
      const exam = prev[week];
      const answers = [...exam.answers];
      answers[qIndex] = optionIndex;
      return { ...prev, [week]: { ...exam, answers } };
    });
  };

  const submitExam = (week) => {
    setExams((prev) => {
      const exam = prev[week];
      const correctCount = exam.questions.filter((q, i) => exam.answers[i] === q.correct_index).length;
      const score = Math.round((correctCount / exam.questions.length) * 100);
      return { ...prev, [week]: { ...exam, submitted: true, score, correctCount } };
    });
  };

  if (!studentId) return <div><h2>Personalized Career Roadmap</h2><NoStudentBanner /></div>;

  return (
    <div>
      <h2>Personalized Career Roadmap</h2>
      <div className="card">
        <label>Target Job Role</label>
        <select value={targetRole} onChange={(e) => setTargetRole(e.target.value)}>
          {roles.map((r) => <option key={r} value={r}>{r}</option>)}
        </select>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {roadmap && (
        <>
          <div className="card">
            <h3>Weekly Learning Plan</h3>
            <p className="muted" style={{ marginTop: -4 }}>
              Each week ends with a short exam on that week's skills, so you confirm the fundamentals
              landed before moving on.
            </p>
            {roadmap.weekly_plan.map((w) => {
              const exam = exams[w.week];
              return (
                <div key={w.week} style={{ marginBottom: 20, paddingBottom: 16, borderBottom: "1px solid #eee" }}>
                  <strong>Week {w.week}</strong>
                  {w.focus_skills.length > 0 && (
                    <div>{w.focus_skills.map((s) => <span key={s} className="skill-chip">{s}</span>)}</div>
                  )}
                  <p className="muted">{w.goal}</p>

                  {w.focus_skills.length > 0 && (
                    <>
                      {!exam && (
                        <button onClick={() => startExam(w.week, w.focus_skills)}>
                          Take Week {w.week} Exam
                        </button>
                      )}
                      {exam?.loading && <p className="muted">Loading exam...</p>}
                      {exam?.error && <div className="error-banner">{exam.error}</div>}

                      {exam?.questions && !exam.submitted && (
                        <div style={{ marginTop: 12 }}>
                          {exam.questions.map((q, qi) => (
                            <div key={qi} style={{ marginBottom: 14 }}>
                              <p style={{ fontWeight: 600, marginBottom: 6 }}>{qi + 1}. {q.question}</p>
                              {q.options.map((opt, oi) => (
                                <label key={oi} style={{ display: "block", fontWeight: 400, marginTop: 2, cursor: "pointer" }}>
                                  <input
                                    type="radio"
                                    name={`week-${w.week}-q-${qi}`}
                                    checked={exam.answers[qi] === oi}
                                    onChange={() => selectAnswer(w.week, qi, oi)}
                                    style={{ width: "auto", marginRight: 8 }}
                                  />
                                  {opt}
                                </label>
                              ))}
                            </div>
                          ))}
                          <button
                            onClick={() => submitExam(w.week)}
                            disabled={exam.answers.some((a) => a === null)}
                          >
                            Submit Week {w.week} Exam
                          </button>
                        </div>
                      )}

                      {exam?.submitted && (
                        <div style={{ marginTop: 12, padding: 14, background: "var(--accent-light)", borderRadius: 8 }}>
                          <p style={{ margin: 0, fontWeight: 700 }}>
                            Score: {exam.score}% ({exam.correctCount}/{exam.questions.length} correct) —{" "}
                            {exam.score >= 60 ? "Passed ✓" : "Needs Review"}
                          </p>
                          {exam.questions.map((q, qi) => (
                            <div key={qi} style={{ marginTop: 10, fontSize: 13 }}>
                              <strong>{qi + 1}. {q.question}</strong>
                              <p style={{ margin: "2px 0", color: exam.answers[qi] === q.correct_index ? "var(--good)" : "var(--bad)" }}>
                                Your answer: {q.options[exam.answers[qi]]}
                                {exam.answers[qi] !== q.correct_index && ` — Correct: ${q.options[q.correct_index]}`}
                              </p>
                              {q.explanation && <p className="muted" style={{ margin: 0 }}>{q.explanation}</p>}
                            </div>
                          ))}
                          <button onClick={() => startExam(w.week, w.focus_skills)} style={{ marginTop: 10 }}>
                            Retake Exam
                          </button>
                        </div>
                      )}
                    </>
                  )}
                </div>
              );
            })}
          </div>

          <div className="card">
            <h3>Recommended Courses</h3>
            <table>
              <thead><tr><th>Skill</th><th>Course</th><th>Provider</th></tr></thead>
              <tbody>
                {roadmap.recommended_courses.map((c, i) => (
                  <tr key={i}><td>{c.skill}</td><td>{c.title}</td><td>{c.provider}</td></tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="card">
            <h3>Certification Roadmap</h3>
            <ul>{roadmap.certification_roadmap.map((c) => <li key={c}>{c}</li>)}</ul>

            <h3>Project Recommendations</h3>
            <ul>{roadmap.project_recommendations.map((p) => <li key={p}>{p}</li>)}</ul>

            <h3>Interview Preparation Schedule</h3>
            <ul>{roadmap.interview_prep_schedule.map((s, i) => <li key={i}>{s}</li>)}</ul>
          </div>
        </>
      )}
    </div>
  );
}

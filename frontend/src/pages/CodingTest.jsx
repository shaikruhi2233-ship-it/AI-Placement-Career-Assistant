import React, { useEffect, useState } from "react";
import api from "../api";
import { useStudent } from "../AuthContext";
import NoStudentBanner from "../components/NoStudentBanner";

export default function CodingTest() {
  const { studentId } = useStudent();
  const [problems, setProblems] = useState([]);
  const [difficulty, setDifficulty] = useState("");
  const [selected, setSelected] = useState(null);
  const [code, setCode] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  const loadProblems = (diff) => {
    api.listCodingProblems(diff || undefined).then(setProblems);
  };

  useEffect(() => { loadProblems(); }, []);
  useEffect(() => { loadProblems(difficulty); }, [difficulty]);

  useEffect(() => {
    if (studentId) api.codingHistory(studentId).then(setHistory).catch(() => {});
  }, [studentId, result]);

  const selectProblem = (p) => {
    api.getCodingProblem(p.id).then((full) => {
      setSelected(full);
      setCode(full.starter_code);
      setResult(null);
      setError("");
    });
  };

  const submit = async () => {
    setLoading(true); setError("");
    try {
      const res = await api.submitCode({ student_id: studentId, problem_id: selected.id, code });
      setResult(res);
    } catch (err) {
      setError(err.response?.data?.detail || "Submission failed.");
    } finally {
      setLoading(false);
    }
  };

  if (!studentId) return <div><h2>Coding Tests</h2><NoStudentBanner /></div>;

  return (
    <div>
      <h2>Coding Tests</h2>

      <div className="card">
        <label>Filter by Difficulty</label>
        <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
          <option value="">All</option>
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
        </select>
        <table style={{ marginTop: 12 }}>
          <thead><tr><th>Problem</th><th>Difficulty</th><th></th></tr></thead>
          <tbody>
            {problems.map((p) => (
              <tr key={p.id}>
                <td>{p.title}</td>
                <td>{p.difficulty}</td>
                <td><button style={{ marginTop: 0 }} onClick={() => selectProblem(p)}>Solve</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selected && (
        <div className="card">
          <h3>{selected.title} <span className="muted">({selected.difficulty})</span></h3>
          <p>{selected.description}</p>
          <label>Your Python Code</label>
          <textarea rows={10} style={{ fontFamily: "monospace" }} value={code} onChange={(e) => setCode(e.target.value)} />
          {error && <div className="error-banner">{error}</div>}
          <button onClick={submit} disabled={loading}>{loading ? "Running..." : "Run & Submit"}</button>

          {result && (
            <div style={{ marginTop: 16 }}>
              <span className={`badge ${result.passed ? "ready" : "needs-work"}`}>
                {result.passed ? "All Tests Passed" : "Some Tests Failed"}
              </span>
              <p style={{ marginTop: 10 }}>
                Passed {result.passed_test_cases} / {result.total_test_cases} test cases — Score: {result.score}%
              </p>
              {result.error_message && <div className="error-banner">{result.error_message}</div>}
            </div>
          )}
        </div>
      )}

      {history.length > 0 && (
        <div className="card">
          <h3>Submission History</h3>
          <table>
            <thead><tr><th>Problem</th><th>Difficulty</th><th>Score</th><th>Result</th><th>Date</th></tr></thead>
            <tbody>
              {history.map((h) => (
                <tr key={h.id}>
                  <td>{h.problem_id}</td>
                  <td>{h.difficulty}</td>
                  <td>{h.score}%</td>
                  <td>{h.passed ? "Passed" : "Failed"}</td>
                  <td>{new Date(h.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

import React, { useEffect, useState } from "react";
import api from "../api";
import { useStudent } from "../AuthContext";
import NoStudentBanner from "../components/NoStudentBanner";

export default function SkillGap() {
  const { studentId } = useStudent();
  const [roles, setRoles] = useState([]);
  const [targetRole, setTargetRole] = useState("");
  const [gap, setGap] = useState(null);
  const [error, setError] = useState("");
  const [activeSkill, setActiveSkill] = useState(null);
  const [resources, setResources] = useState(null);
  const [resourcesLoading, setResourcesLoading] = useState(false);

  useEffect(() => {
    api.listRoles().then((r) => { setRoles(r); if (r.length) setTargetRole(r[0]); });
  }, []);

  const fetchGap = () => {
    setError("");
    setActiveSkill(null);
    setResources(null);
    api.getSkillGap(studentId, targetRole).then(setGap)
      .catch((err) => setError(err.response?.data?.detail || "Could not compute skill gap."));
  };

  useEffect(() => { if (studentId && targetRole) fetchGap(); }, [studentId, targetRole]);

  const handleSkillClick = async (skill) => {
    if (activeSkill === skill) {
      setActiveSkill(null);
      return;
    }
    setActiveSkill(skill);
    setResourcesLoading(true);
    try {
      const res = await api.getSkillResources(skill);
      setResources(res);
    } catch {
      setResources(null);
    } finally {
      setResourcesLoading(false);
    }
  };

  if (!studentId) return <div><h2>Skill Gap Analysis</h2><NoStudentBanner /></div>;

  return (
    <div>
      <h2>Skill Gap Analysis</h2>
      <div className="card">
        <label>Target Job Role</label>
        <select value={targetRole} onChange={(e) => setTargetRole(e.target.value)}>
          {roles.map((r) => <option key={r} value={r}>{r}</option>)}
        </select>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {gap && (
        <div className="card">
          <div className="score-row">
            <div className="score-box">
              <div className="value">{gap.match_percentage}%</div>
              <div className="label">Skill Match</div>
            </div>
          </div>

          <h3>Matched Skills</h3>
          {gap.matched_skills.length
            ? gap.matched_skills.map((s) => <span key={s} className="skill-chip">{s}</span>)
            : <p className="muted">No overlapping technical skills yet.</p>}

          <h3>Missing Technical Skills</h3>
          <p className="muted" style={{ marginTop: -4 }}>
            Click a skill to see its learning resources — video, notes, docs, course, practice, and
            project — then pick whichever one you want to open.
          </p>
          {gap.missing_technical_skills.length
            ? gap.missing_technical_skills.map((s) => (
                <span
                  key={s}
                  className="skill-chip missing"
                  style={{ cursor: "pointer", textDecoration: activeSkill === s ? "underline" : "none" }}
                  onClick={() => handleSkillClick(s)}
                >
                  {s}
                </span>
              ))
            : <p className="muted">No technical gaps — you're covered!</p>}

          {activeSkill && (
            <div style={{ marginTop: 14, borderTop: "1px solid #eee", paddingTop: 14 }}>
              <h4 style={{ marginBottom: 8 }}>Learning resources: {activeSkill}</h4>
              {resourcesLoading && <p className="muted">Loading resources...</p>}
              {!resourcesLoading && resources && (
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                  {Object.entries(resources.resources).map(([key, r]) => (
                    <a
                      key={key}
                      href={r.url}
                      target="_blank"
                      rel="noreferrer"
                      style={{
                        display: "block", padding: "10px 12px", borderRadius: 8,
                        background: "var(--accent-light)", color: "#1f4e79", textDecoration: "none",
                      }}
                    >
                      <div style={{ fontWeight: 700 }}>{r.label}</div>
                      <div className="muted" style={{ fontSize: 13 }}>{r.title}</div>
                    </a>
                  ))}
                </div>
              )}
            </div>
          )}

          <h3>Missing Soft Skills</h3>
          {gap.missing_soft_skills.length
            ? gap.missing_soft_skills.map((s) => <span key={s} className="skill-chip missing">{s}</span>)
            : <p className="muted">No soft-skill gaps detected.</p>}

          <h3>Recommended Certifications</h3>
          <ul>{gap.recommended_certifications.map((c) => <li key={c}>{c}</li>)}</ul>

          <h3>Recommended Projects</h3>
          <ul>{gap.recommended_projects.map((p) => <li key={p}>{p}</li>)}</ul>
        </div>
      )}
    </div>
  );
}

import React, { useCallback, useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import api from "../api";
import { useAuth } from "../AuthContext";

const REFRESH_INTERVAL_MS = 30000; // keeps the panel current without a manual refresh

function ratingColor(label) {
  if (label === "Ready") return "#1e7e34";
  if (label === "Moderate") return "#d9822b";
  if (label === "Needs Work") return "#c0392b";
  return "var(--muted)";
}

export default function StudentSnapshot() {
  const { student } = useAuth();
  const [data, setData] = useState(null);
  const [updatedAt, setUpdatedAt] = useState(null);
  const location = useLocation();

  const load = useCallback(() => {
    if (!student?.id) return;
    api.getDashboard(student.id)
      .then((d) => { setData(d); setUpdatedAt(new Date()); })
      .catch(() => {});
  }, [student?.id]);

  // Shown the moment a student logs in (mount), refreshed every time they
  // navigate to a different page (so it reflects whatever they just did -
  // uploaded a resume, ran a prediction, updated their profile), and on a
  // timer so it stays current even while sitting on one page.
  useEffect(load, [load]);
  useEffect(load, [location.pathname, load]);
  useEffect(() => {
    const id = setInterval(load, REFRESH_INTERVAL_MS);
    return () => clearInterval(id);
  }, [load]);

  if (!student) return null;

  const resume = data?.latest_resume;
  const prediction = data?.latest_prediction;

  return (
    <div className="right-panel">
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
        <div className="avatar" style={{ background: "var(--accent)" }}>
          {student.name.split(" ").filter(Boolean).slice(0, 2).map((p) => p[0].toUpperCase()).join("")}
        </div>
        <div style={{ minWidth: 0 }}>
          <h3 style={{ marginBottom: 2 }}>{student.name}</h3>
          <p className="muted" style={{ margin: 0, fontSize: 12, overflow: "hidden", textOverflow: "ellipsis" }}>{student.email}</p>
        </div>
      </div>

      <div className="snap-row"><span className="snap-label">Branch</span><span>{student.branch || "—"}</span></div>
      <div className="snap-row"><span className="snap-label">CGPA</span><span>{student.cgpa ?? "—"}</span></div>
      <div className="snap-row">
        <span className="snap-label">Attendance</span>
        <span>{student.attendance != null ? `${student.attendance}%` : "—"}</span>
      </div>
      <div className="snap-row">
        <span className="snap-label">Technical Skills</span><span>{student.technical_skills?.length ?? 0}</span>
      </div>
      <div className="snap-row">
        <span className="snap-label">Certifications</span><span>{student.certifications?.length ?? 0}</span>
      </div>
      <div className="snap-row">
        <span className="snap-label">Projects</span><span>{student.projects?.length ?? 0}</span>
      </div>

      <h4 style={{ marginTop: 18, marginBottom: 6 }}>Resume</h4>
      {resume ? (
        <>
          <div className="snap-row"><span className="snap-label">ATS Score</span><span>{resume.ats_score}%</span></div>
          <div className="snap-row">
            <span className="snap-label">Semantic Match</span><span>{resume.semantic_score}%</span>
          </div>
        </>
      ) : <p className="muted" style={{ fontSize: 13 }}>No resume uploaded yet.</p>}

      <h4 style={{ marginTop: 18, marginBottom: 6 }}>Placement Readiness</h4>
      {prediction ? (
        <>
          <div className="snap-row"><span className="snap-label">Score</span><span>{prediction.readiness_score}%</span></div>
          <div className="snap-row">
            <span className="snap-label">Status</span>
            <span style={{ color: ratingColor(prediction.readiness_label), fontWeight: 700 }}>
              {prediction.readiness_label}
            </span>
          </div>
        </>
      ) : <p className="muted" style={{ fontSize: 13 }}>No prediction run yet.</p>}

      {updatedAt && <p className="snap-updated">Updated {updatedAt.toLocaleTimeString()}</p>}
    </div>
  );
}

import React, { useEffect, useState } from "react";
import api from "../api";
import { useStudent } from "../AuthContext";
import NoStudentBanner from "../components/NoStudentBanner";

export default function ExternalJobs() {
  const { studentId } = useStudent();
  const [opportunities, setOpportunities] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!studentId) return;
    api.getExternalOpportunities(studentId).then(setOpportunities)
      .catch((err) => setError(err.response?.data?.detail || "Could not load opportunities."));
  }, [studentId]);

  if (!studentId) return <div><h2>LinkedIn & GitHub Opportunities</h2><NoStudentBanner /></div>;

  return (
    <div>
      <h2>LinkedIn & GitHub Job and Internship Recommendations</h2>
      <p className="muted">
        Ranked by skill match against your profile. Ships with a curated sample dataset — see
        backend/app/services/external_jobs.py for wiring up live LinkedIn/GitHub API access.
      </p>

      {error && <div className="error-banner">{error}</div>}

      {opportunities.map((o, i) => (
        <div className="card" key={i}>
          <span className="skill-chip">{o.source}</span>
          <span className="skill-chip">{o.type}</span>
          <h3 style={{ marginBottom: 4 }}>{o.title}</h3>
          <p className="muted" style={{ margin: 0 }}>{o.company_or_org} · {o.location}</p>
          <p style={{ margin: "8px 0" }}><strong>Match score:</strong> {o.match_score}%</p>
          <a href={o.url} target="_blank" rel="noreferrer"><button style={{ marginTop: 0 }}>View on {o.source}</button></a>
        </div>
      ))}
    </div>
  );
}

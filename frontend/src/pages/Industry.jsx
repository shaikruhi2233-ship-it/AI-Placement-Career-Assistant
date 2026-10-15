import React, { useEffect, useState } from "react";
import api from "../api";

export default function Industry() {
  const [demand, setDemand] = useState(null);

  useEffect(() => { api.getIndustryDemand().then(setDemand); }, []);

  if (!demand) return <div><h2>Industry Demand Analyzer</h2><p className="muted">Loading...</p></div>;

  return (
    <div>
      <h2>Industry Demand Analyzer</h2>
      <p className="muted">Novel contribution: highlights current market trends independent of any single student profile.</p>

      <div className="card">
        <h3>Trending Technologies</h3>
        <table>
          <thead><tr><th>Technology</th><th>Demand Index</th><th>Growth</th></tr></thead>
          <tbody>
            {demand.trending_technologies.map((t) => (
              <tr key={t.name}><td>{t.name}</td><td>{t.demand_index}</td><td>{t.growth}</td></tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3>Trending Job Roles</h3>
        <table>
          <thead><tr><th>Role</th><th>Openings Index</th></tr></thead>
          <tbody>
            {demand.trending_roles.map((r) => (
              <tr key={r.role}><td>{r.role}</td><td>{r.openings_index}</td></tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3>Emerging Programming Languages</h3>
        {demand.emerging_languages.map((l) => <span key={l} className="skill-chip">{l}</span>)}
      </div>

      <div className="card">
        <h3>Computed Skill Demand (live from current job postings)</h3>
        <p className="muted" style={{ marginTop: -4 }}>
          Technology frequency → skill demand, computed directly from the current job-postings dataset
          (see Real Job Opportunities under Job Recommendations) rather than a static list.
        </p>
        <table>
          <thead><tr><th>Skill</th><th>Postings Mentioning</th><th>Demand Share</th></tr></thead>
          <tbody>
            {demand.computed_skill_demand.map((s) => (
              <tr key={s.skill}><td>{s.skill}</td><td>{s.postings_mentioning}</td><td>{s.demand_share}%</td></tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3>Computed Trending Roles (open postings)</h3>
        <table>
          <thead><tr><th>Role</th><th>Open Postings</th></tr></thead>
          <tbody>
            {demand.computed_role_demand.map((r) => (
              <tr key={r.role}><td>{r.role}</td><td>{r.open_postings}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

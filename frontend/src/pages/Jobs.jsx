import React, { useEffect, useState } from "react";
import api from "../api";
import { useStudent } from "../AuthContext";
import NoStudentBanner from "../components/NoStudentBanner";

export default function Jobs() {
  const { studentId } = useStudent();
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState("");
  const [applications, setApplications] = useState([]);
  const [expandedRole, setExpandedRole] = useState(null);
  const [guidance, setGuidance] = useState({}); // role -> { skillGap, roadmap, careerGuidance, opportunities, loading, error }

  const loadJobs = () => {
    if (!studentId) return;
    api.recommendJobs(studentId).then(setJobs)
      .catch((err) => setError(err.response?.data?.detail || "Could not load recommendations."));
  };

  const loadApplications = () => {
    api.listApplications().then(setApplications).catch(() => {});
  };

  useEffect(loadJobs, [studentId]);
  useEffect(loadApplications, [studentId]);

  // The core connective flow: selecting a role loads its Skill Gap
  // (missing skills for THIS exact role), an AI Career Guidance narrative,
  // Career Roadmap (weekly plan/courses/certs), and Real Job Opportunities
  // (company/location/job type/apply link) inline, right under the job card.
  const handleSelectRole = async (role) => {
    if (expandedRole === role) {
      setExpandedRole(null);
      return;
    }
    setExpandedRole(role);
    if (guidance[role]) return; // already fetched

    setGuidance((g) => ({ ...g, [role]: { loading: true } }));
    try {
      const [skillGap, roadmap, careerGuidance, opportunities, internships] = await Promise.all([
        api.getSkillGap(studentId, role),
        api.getRoadmap(studentId, role),
        api.getCareerGuidance(studentId, role),
        api.getJobOpportunities(role, studentId),
        api.getInternships(role, studentId),
      ]);
      setGuidance((g) => ({
        ...g,
        [role]: { loading: false, skillGap, roadmap, careerGuidance, opportunities, internships },
      }));
    } catch (err) {
      setGuidance((g) => ({
        ...g,
        [role]: { loading: false, error: err.response?.data?.detail || "Could not load guidance for this role." },
      }));
    }
  };

  if (!studentId) return <div><h2>Job Recommendations</h2><NoStudentBanner /></div>;

  return (
    <div>
      <h2>Intelligent Job Recommendation</h2>
      <p className="muted">
        Ranked by a blend of skill overlap and an AI semantic match against your resume text.
        Select a role to see your readiness, exactly what to learn next, and real postings to apply to.
      </p>

      {error && <div className="error-banner">{error}</div>}

      {jobs.map((j) => {
        const isExpanded = expandedRole === j.role;
        const g = guidance[j.role];

        return (
          <div className="card" key={j.role}>
            <h3>{j.role} — {j.match_score}% match</h3>
            <p className="muted" style={{ marginTop: -6 }}>
              Skill overlap: {j.skill_match}% · AI semantic match: {j.semantic_match}%
            </p>
            <p><strong>Companies hiring:</strong> {j.companies.join(", ")}</p>
            <p><strong>Required skills:</strong></p>
            {j.required_skills.map((s) => <span key={s} className="skill-chip">{s}</span>)}

            <div style={{ marginTop: 14, display: "flex", gap: 10, flexWrap: "wrap" }}>
              <button onClick={() => handleSelectRole(j.role)}>
                {isExpanded ? "Hide guidance" : "What should I learn for this role?"}
              </button>
              <a
                href={`https://www.linkedin.com/jobs/search/?keywords=${encodeURIComponent(j.role)}`}
                target="_blank"
                rel="noreferrer"
                style={{
                  padding: "8px 14px", borderRadius: 6, background: "#0a66c2", color: "#fff",
                  textDecoration: "none", fontWeight: 600, display: "inline-flex", alignItems: "center",
                }}
              >
                Search all {j.role} jobs on LinkedIn →
              </a>
            </div>

            {isExpanded && (
              <div style={{ marginTop: 16, borderTop: "1px solid #eee", paddingTop: 16 }}>
                {g?.loading && <p className="muted">Loading AI guidance for {j.role}...</p>}
                {g?.error && <div className="error-banner">{g.error}</div>}

                {g?.careerGuidance && (
                  <div style={{ padding: 14, background: "var(--accent-light)", borderRadius: 8, marginBottom: 16 }}>
                    <p style={{ margin: 0, fontWeight: 600 }}>{g.careerGuidance.narrative}</p>
                    <p className="muted" style={{ margin: "4px 0 0" }}>{g.careerGuidance.stage}</p>
                  </div>
                )}

                {g?.skillGap && (
                  <>
                    <h4 style={{ marginBottom: 4 }}>Skill Gap for {j.role}</h4>
                    <div className="score-row" style={{ marginBottom: 10 }}>
                      <div className="score-box">
                        <div className="value">{g.skillGap.match_percentage}%</div>
                        <div className="label">Skill Match</div>
                      </div>
                    </div>
                    <p style={{ marginBottom: 4 }}><strong>Missing technical skills:</strong></p>
                    {g.skillGap.missing_technical_skills.length
                      ? g.skillGap.missing_technical_skills.map((s) => <span key={s} className="skill-chip missing">{s}</span>)
                      : <p className="muted">No technical gaps — you're covered!</p>}
                    <p style={{ marginTop: 10, marginBottom: 4 }}><strong>Missing soft skills:</strong></p>
                    {g.skillGap.missing_soft_skills.length
                      ? g.skillGap.missing_soft_skills.map((s) => <span key={s} className="skill-chip missing">{s}</span>)
                      : <p className="muted">No soft-skill gaps detected.</p>}
                  </>
                )}

                {g?.roadmap && (
                  <>
                    <h4 style={{ marginTop: 18, marginBottom: 4 }}>AI-Guided Learning Roadmap</h4>
                    {g.roadmap.weekly_plan.map((w) => (
                      <div key={w.week} style={{ marginBottom: 8 }}>
                        <strong>Week {w.week}:</strong>{" "}
                        {w.focus_skills.length > 0 ? w.focus_skills.join(", ") : "Advanced practice"}
                        <p className="muted" style={{ margin: "2px 0 0" }}>{w.goal}</p>
                      </div>
                    ))}
                    <p style={{ marginTop: 10, marginBottom: 4 }}><strong>Recommended certifications:</strong></p>
                    <ul>{g.roadmap.certification_roadmap.map((c) => <li key={c}>{c}</li>)}</ul>
                    <p style={{ marginBottom: 4 }}><strong>Recommended projects:</strong></p>
                    <ul>{g.roadmap.project_recommendations.map((p) => <li key={p}>{p}</li>)}</ul>
                  </>
                )}

                {g?.opportunities && g.opportunities.length > 0 && (
                  <>
                    <h4 style={{ marginTop: 18, marginBottom: 4 }}>Real Job Opportunities</h4>
                    <p className="muted" style={{ marginTop: -2, marginBottom: 8 }}>
                      {g.opportunities[0]?.source === "Live"
                        ? "Fetched live from a job board just now."
                        : "Live fetch unavailable right now — showing curated sample postings."}
                    </p>
                    <table>
                      <thead>
                        <tr>
                          <th>Company</th><th>Location</th><th>Job Type</th>
                          <th>Required Skills</th><th>Match %</th><th>Posted</th><th>Apply</th><th>LinkedIn</th>
                        </tr>
                      </thead>
                      <tbody>
                        {g.opportunities.map((o, i) => (
                          <tr key={i}>
                            <td>{o.company}</td>
                            <td>{o.location}</td>
                            <td>{o.job_type}</td>
                            <td>{o.required_skills.join(", ")}</td>
                            <td>{o.match_score}%</td>
                            <td>{o.posted_date || "—"}</td>
                            <td><a href={o.apply_link} target="_blank" rel="noreferrer">Apply →</a></td>
                            <td><a href={o.linkedin_link} target="_blank" rel="noreferrer">View on LinkedIn →</a></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </>
                )}

                {g?.internships && g.internships.length > 0 && (
                  <>
                    <h4 style={{ marginTop: 18, marginBottom: 4 }}>Real Internships</h4>
                    <p className="muted" style={{ marginTop: -2, marginBottom: 8 }}>
                      {g.internships[0]?.source === "Live"
                        ? "Fetched live from a job board just now."
                        : "Live fetch unavailable right now — showing curated sample postings."}
                    </p>
                    <table>
                      <thead>
                        <tr>
                          <th>Company</th><th>Location</th><th>Required Skills</th>
                          <th>Match %</th><th>Posted</th><th>Apply</th><th>LinkedIn</th>
                        </tr>
                      </thead>
                      <tbody>
                        {g.internships.map((o, i) => (
                          <tr key={i}>
                            <td>{o.company}</td>
                            <td>{o.location}</td>
                            <td>{o.required_skills.join(", ")}</td>
                            <td>{o.match_score}%</td>
                            <td>{o.posted_date || "—"}</td>
                            <td><a href={o.apply_link} target="_blank" rel="noreferrer">Apply →</a></td>
                            <td><a href={o.linkedin_link} target="_blank" rel="noreferrer">View on LinkedIn →</a></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </>
                )}
                {g?.internships && g.internships.length === 0 && (
                  <p className="muted" style={{ marginTop: 18 }}>No open internships found for {j.role} right now.</p>
                )}
              </div>
            )}
          </div>
        );
      })}

      {applications.length > 0 && (
        <div className="card">
          <h3>My Applications</h3>
          <table>
            <thead><tr><th>Role</th><th>Company</th><th>Match</th><th>Status</th><th>Applied On</th></tr></thead>
            <tbody>
              {applications.map((a) => (
                <tr key={a.id}>
                  <td>{a.role}</td>
                  <td>{a.company || "—"}</td>
                  <td>{a.match_score}%</td>
                  <td>{a.status}</td>
                  <td>{new Date(a.applied_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

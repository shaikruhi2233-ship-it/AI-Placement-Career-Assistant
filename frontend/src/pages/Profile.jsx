import React, { useEffect, useState } from "react";
import api from "../api";
import { useAuth } from "../AuthContext";

function toList(str) {
  return str.split(",").map((s) => s.trim()).filter(Boolean);
}

export default function Profile() {
  const { student, refreshStudent } = useAuth();
  const [form, setForm] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!student) return;
    setForm({
      name: student.name,
      branch: student.branch,
      cgpa: student.cgpa,
      attendance: student.attendance,
      aptitude_score: student.aptitude_score,
      coding_score: student.coding_score,
      communication_score: student.communication_score,
      internship_months: student.internship_months,
      technical_skills: student.technical_skills.join(", "),
      soft_skills: student.soft_skills.join(", "),
      certifications: student.certifications.join(", "),
      projects: student.projects.join(", "),
      career_interest: student.career_interest,
    });
  }, [student]);

  if (!student || !form) return <div><h2>Student Profile</h2><p className="muted">Loading...</p></div>;

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); setSuccess(""); setLoading(true);
    try {
      const payload = {
        name: form.name,
        branch: form.branch,
        cgpa: Number(form.cgpa) || 0,
        attendance: Number(form.attendance) || 0,
        aptitude_score: Number(form.aptitude_score) || 0,
        coding_score: Number(form.coding_score) || 0,
        communication_score: Number(form.communication_score) || 0,
        internship_months: Number(form.internship_months) || 0,
        technical_skills: toList(form.technical_skills),
        soft_skills: toList(form.soft_skills),
        certifications: toList(form.certifications),
        projects: toList(form.projects),
        career_interest: form.career_interest,
      };
      const updated = await api.updateStudent(student.id, payload);
      refreshStudent(updated);
      setSuccess("Profile updated.");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update profile.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Student Profile</h2>
      <div className="card">
        <p className="muted" style={{ marginBottom: 4 }}>Logged in as <strong>{student.email}</strong></p>
      </div>

      <div className="card">
        <h3>Your Details</h3>
        <div className="grid">
          <div className="snap-row"><span className="snap-label">Full Name</span><span>{student.name}</span></div>
          <div className="snap-row"><span className="snap-label">Branch</span><span>{student.branch || "—"}</span></div>
          <div className="snap-row"><span className="snap-label">Career Interest</span><span>{student.career_interest || "—"}</span></div>
          <div className="snap-row"><span className="snap-label">CGPA</span><span>{student.cgpa}</span></div>
          <div className="snap-row"><span className="snap-label">Attendance</span><span>{student.attendance}%</span></div>
          <div className="snap-row"><span className="snap-label">Aptitude Score</span><span>{student.aptitude_score}</span></div>
          <div className="snap-row"><span className="snap-label">Coding Score</span><span>{student.coding_score}</span></div>
          <div className="snap-row"><span className="snap-label">Communication Score</span><span>{student.communication_score}</span></div>
          <div className="snap-row"><span className="snap-label">Internship</span><span>{student.internship_months} months</span></div>
        </div>

        <p style={{ marginTop: 16, marginBottom: 4 }}><strong>Technical Skills</strong></p>
        {student.technical_skills.length
          ? student.technical_skills.map((s) => <span key={s} className="skill-chip">{s}</span>)
          : <p className="muted">Not added yet.</p>}

        <p style={{ marginTop: 12, marginBottom: 4 }}><strong>Soft Skills</strong></p>
        {student.soft_skills.length
          ? student.soft_skills.map((s) => <span key={s} className="skill-chip">{s}</span>)
          : <p className="muted">Not added yet.</p>}

        <p style={{ marginTop: 12, marginBottom: 4 }}><strong>Certifications</strong></p>
        {student.certifications.length
          ? <ul>{student.certifications.map((c) => <li key={c}>{c}</li>)}</ul>
          : <p className="muted">Not added yet.</p>}

        <p style={{ marginTop: 12, marginBottom: 4 }}><strong>Projects</strong></p>
        {student.projects.length
          ? <ul>{student.projects.map((p) => <li key={p}>{p}</li>)}</ul>
          : <p className="muted">Not added yet.</p>}
      </div>

      {error && <div className="error-banner">{error}</div>}
      {success && <div className="card" style={{ color: "#1e8e3e" }}>{success}</div>}

      <form className="card" onSubmit={handleSubmit}>
        <h3>Edit Profile</h3>
        <div className="grid">
          <div>
            <label>Full Name</label>
            <input name="name" value={form.name} onChange={handleChange} required />
          </div>
          <div>
            <label>Branch</label>
            <input name="branch" value={form.branch} onChange={handleChange} placeholder="e.g. CSE" />
          </div>
          <div>
            <label>Career Interest / Target Role</label>
            <input name="career_interest" value={form.career_interest} onChange={handleChange}
                   placeholder="e.g. Data Analyst" />
          </div>
          <div>
            <label>CGPA (0-10)</label>
            <input name="cgpa" type="number" step="0.1" value={form.cgpa} onChange={handleChange} />
          </div>
          <div>
            <label>Attendance (%)</label>
            <input name="attendance" type="number" value={form.attendance} onChange={handleChange} />
          </div>
          <div>
            <label>Aptitude Score (0-100)</label>
            <input name="aptitude_score" type="number" value={form.aptitude_score} onChange={handleChange} />
          </div>
          <div>
            <label>Coding Score (0-100)</label>
            <input name="coding_score" type="number" value={form.coding_score} onChange={handleChange} />
          </div>
          <div>
            <label>Communication Score (0-100)</label>
            <input name="communication_score" type="number" value={form.communication_score} onChange={handleChange} />
          </div>
          <div>
            <label>Internship Duration (months)</label>
            <input name="internship_months" type="number" value={form.internship_months} onChange={handleChange} />
          </div>
        </div>

        <label>Technical Skills (comma separated)</label>
        <input name="technical_skills" value={form.technical_skills} onChange={handleChange}
               placeholder="python, sql, react" />

        <label>Soft Skills (comma separated)</label>
        <input name="soft_skills" value={form.soft_skills} onChange={handleChange}
               placeholder="communication, teamwork" />

        <label>Certifications (comma separated)</label>
        <input name="certifications" value={form.certifications} onChange={handleChange} />

        <label>Projects (comma separated)</label>
        <input name="projects" value={form.projects} onChange={handleChange} />

        <button type="submit" disabled={loading}>{loading ? "Saving..." : "Update Profile"}</button>
      </form>
    </div>
  );
}

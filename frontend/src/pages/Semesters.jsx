import React, { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import api from "../api";
import { useStudent } from "../AuthContext";
import NoStudentBanner from "../components/NoStudentBanner";

const emptyForm = { semester_number: "", sgpa: "", attendance: "", backlogs: "0", skills_gained: "", remarks: "" };

export default function Semesters() {
  const { studentId } = useStudent();
  const [trend, setTrend] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const load = () => {
    if (!studentId) return;
    api.getSemesterTrend(studentId).then(setTrend).catch(() => {});
  };

  useEffect(load, [studentId]);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      await api.addSemesterRecord(studentId, {
        semester_number: Number(form.semester_number),
        sgpa: Number(form.sgpa),
        attendance: Number(form.attendance),
        backlogs: Number(form.backlogs) || 0,
        skills_gained: form.skills_gained.split(",").map((s) => s.trim()).filter(Boolean),
        remarks: form.remarks,
      });
      setForm(emptyForm);
      load();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not save semester record.");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (recordId) => {
    await api.deleteSemesterRecord(studentId, recordId);
    load();
  };

  if (!studentId) return <div><h2>Semester-wise Improvement Tracking</h2><NoStudentBanner /></div>;

  const chartData = (trend?.records || []).map((r) => ({
    name: `Sem ${r.semester_number}`, sgpa: r.sgpa, attendance: r.attendance,
  }));

  return (
    <div>
      <h2>Semester-wise Improvement Tracking</h2>

      <form className="card" onSubmit={handleSubmit}>
        <h3>Log a Semester</h3>
        <div className="grid">
          <div><label>Semester Number</label>
            <input name="semester_number" type="number" value={form.semester_number} onChange={handleChange} required /></div>
          <div><label>SGPA (0-10)</label>
            <input name="sgpa" type="number" step="0.01" value={form.sgpa} onChange={handleChange} required /></div>
          <div><label>Attendance (%)</label>
            <input name="attendance" type="number" value={form.attendance} onChange={handleChange} required /></div>
          <div><label>Active Backlogs</label>
            <input name="backlogs" type="number" value={form.backlogs} onChange={handleChange} /></div>
        </div>
        <label>Skills Gained This Semester (comma separated)</label>
        <input name="skills_gained" value={form.skills_gained} onChange={handleChange} />
        <label>Remarks</label>
        <input name="remarks" value={form.remarks} onChange={handleChange} />
        {error && <div className="error-banner">{error}</div>}
        <button type="submit" disabled={loading}>{loading ? "Saving..." : "Add Semester Record"}</button>
      </form>

      {trend && trend.records.length > 0 && (
        <>
          <div className="card">
            <h3>SGPA & Attendance Trend</h3>
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="sgpa" stroke="#1f4e79" strokeWidth={2} name="SGPA (x10 scale)" />
                <Line type="monotone" dataKey="attendance" stroke="#d9822b" strokeWidth={2} name="Attendance %" />
              </LineChart>
            </ResponsiveContainer>
            <p className="muted" style={{ marginTop: 10 }}>
              SGPA change: <strong>{trend.sgpa_change >= 0 ? "+" : ""}{trend.sgpa_change}</strong> ·
              {" "}Attendance change: <strong>{trend.attendance_change >= 0 ? "+" : ""}{trend.attendance_change}%</strong>
            </p>
            <p>{trend.improvement_summary}</p>
          </div>

          <div className="card">
            <h3>Semester History</h3>
            <table>
              <thead><tr><th>Sem</th><th>SGPA</th><th>Attendance</th><th>Backlogs</th><th>Skills Gained</th><th></th></tr></thead>
              <tbody>
                {trend.records.map((r) => (
                  <tr key={r.id}>
                    <td>{r.semester_number}</td>
                    <td>{r.sgpa}</td>
                    <td>{r.attendance}%</td>
                    <td>{r.backlogs}</td>
                    <td>{r.skills_gained.join(", ") || "—"}</td>
                    <td><button style={{ marginTop: 0, background: "#c0392b" }} onClick={() => handleDelete(r.id)}>Delete</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

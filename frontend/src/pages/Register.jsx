import React, { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import api from "../api";
import AuthLayout, { Alert, Field } from "../components/AuthLayout";

function passwordStrength(pw) {
  let score = 0;
  if (pw.length >= 6) score++;
  if (pw.length >= 10) score++;
  if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++;
  if (/\d/.test(pw) || /[^A-Za-z0-9]/.test(pw)) score++;
  const labels = ["Too short", "Weak", "Fair", "Good", "Strong"];
  return { score, label: labels[score] };
}

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "", confirmPassword: "", branch: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });
  const strength = passwordStrength(form.password);
  const mismatch = form.confirmPassword && form.password !== form.confirmPassword;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (form.password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }
    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      // Register only — do NOT log the student in automatically. They land
      // on the Log In tab next and sign in explicitly with their new
      // credentials, matching Register -> Log In -> Dashboard.
      await api.register({ name: form.name, email: form.email, password: form.password, branch: form.branch });
      navigate("/login", { state: { justRegistered: true } });
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <div className="auth-tabs" role="tablist">
        <NavLink to="/login" className={({ isActive }) => (isActive ? "active" : "")}>Log in</NavLink>
        <NavLink to="/register" className={({ isActive }) => (isActive ? "active" : "")}>Register</NavLink>
      </div>

      <h2 className="auth-title">Create your account</h2>
      <p className="auth-sub">Start tracking and improving your placement readiness today.</p>

      {error && <Alert>{error}</Alert>}

      <form onSubmit={handleSubmit} className="auth-form">
        <div className="field-grid">
          <Field label="Full name" icon="user" name="name" value={form.name} onChange={handleChange}
            placeholder="Your full name" autoComplete="name" required autoFocus />
          <Field label={<>Branch <span className="optional">(optional)</span></>} icon="building" name="branch"
            value={form.branch} onChange={handleChange} placeholder="e.g. MCA, CSE" />
        </div>

        <Field label="Email address" icon="mail" name="email" type="email" value={form.email} onChange={handleChange}
          placeholder="you@college.edu" autoComplete="email" required />

        <Field label="Password" icon="lock" name="password" type="password" value={form.password} onChange={handleChange}
          placeholder="At least 6 characters" autoComplete="new-password" required
          hint={form.password && (
            <div className={`strength s-${strength.score}`}>
              <div className="strength-bars">{[1, 2, 3, 4].map((i) => <span key={i} />)}</div>
              <span className="strength-label">{strength.label}</span>
            </div>
          )} />

        <Field label="Confirm password" icon="lock" name="confirmPassword" type="password" value={form.confirmPassword}
          onChange={handleChange} placeholder="Re-enter your password" autoComplete="new-password" required
          aria-invalid={mismatch || undefined}
          hint={mismatch && <span className="field-error">Passwords do not match</span>} />

        <button type="submit" className="auth-submit" disabled={loading}>
          {loading ? <><span className="spinner" /> Creating account…</> : "Create account"}
        </button>
      </form>

      <p className="auth-switch">
        Already have an account? <Link to="/login" className="auth-link">Log in</Link>
      </p>
    </AuthLayout>
  );
}

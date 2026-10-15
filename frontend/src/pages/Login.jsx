import React, { useState } from "react";
import { Link, NavLink, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";
import AuthLayout, { Alert, Field } from "../components/AuthLayout";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const justRegistered = Boolean(location.state?.justRegistered);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Check your email and password.");
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

      <h2 className="auth-title">Welcome back</h2>
      <p className="auth-sub">Log in to continue tracking your placement readiness.</p>

      {justRegistered && <Alert tone="success">Account created. Log in below to continue.</Alert>}
      {error && <Alert>{error}</Alert>}

      <form onSubmit={handleSubmit} className="auth-form" noValidate={false}>
        <Field label="Email address" icon="mail" name="email" type="email" value={email}
          onChange={(e) => setEmail(e.target.value)} placeholder="you@college.edu" autoComplete="email" required autoFocus />

        <Field label="Password" icon="lock" name="password" type="password" value={password}
          onChange={(e) => setPassword(e.target.value)} placeholder="Enter your password" autoComplete="current-password" required />

        <div className="auth-row-end">
          <Link to="/forgot-password" className="auth-link">Forgot password?</Link>
        </div>

        <button type="submit" className="auth-submit" disabled={loading}>
          {loading ? <><span className="spinner" /> Logging in…</> : "Log in"}
        </button>
      </form>

      <p className="auth-switch">
        Don't have an account? <Link to="/register" className="auth-link">Create one</Link>
      </p>
    </AuthLayout>
  );
}

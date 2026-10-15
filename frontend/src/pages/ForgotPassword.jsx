import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";
import AuthLayout, { Alert, Field } from "../components/AuthLayout";
import Icon from "../components/Icon";

export default function ForgotPassword() {
  const { resetPassword } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", newPassword: "", confirmPassword: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (form.newPassword.length < 6) {
      setError("New password must be at least 6 characters.");
      return;
    }
    if (form.newPassword !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      await resetPassword({ email: form.email, new_password: form.newPassword });
      setSuccess(true);
      setTimeout(() => navigate("/"), 1200);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not reset password for that email.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <Link to="/login" className="auth-back"><Icon name="arrowLeft" size={16} /> Back to log in</Link>

      <div className="auth-icon-badge"><Icon name="lock" size={22} /></div>
      <h2 className="auth-title">Reset your password</h2>
      <p className="auth-sub">Enter the email on your account and choose a new password.</p>

      {success ? (
        <Alert tone="success">Password updated. Logging you in…</Alert>
      ) : (
        <>
          {error && <Alert>{error}</Alert>}
          <form onSubmit={handleSubmit} className="auth-form">
            <Field label="Email address" icon="mail" name="email" type="email" value={form.email} onChange={handleChange}
              placeholder="you@college.edu" autoComplete="email" required autoFocus />
            <Field label="New password" icon="lock" name="newPassword" type="password" value={form.newPassword}
              onChange={handleChange} placeholder="At least 6 characters" autoComplete="new-password" required />
            <Field label="Confirm new password" icon="lock" name="confirmPassword" type="password" value={form.confirmPassword}
              onChange={handleChange} placeholder="Re-enter new password" autoComplete="new-password" required />
            <button type="submit" className="auth-submit" disabled={loading}>
              {loading ? <><span className="spinner" /> Resetting…</> : "Reset password"}
            </button>
          </form>
        </>
      )}

      <p className="auth-switch">
        Remembered it? <Link to="/login" className="auth-link">Log in</Link>
      </p>
    </AuthLayout>
  );
}

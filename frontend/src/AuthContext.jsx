import React, { createContext, useContext, useEffect, useState } from "react";
import api from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("authToken"));
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);

  // On load (or whenever the token changes), fetch the current profile.
  useEffect(() => {
    if (!token) {
      setStudent(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    api.me()
      .then(setStudent)
      .catch(() => {
        // Token invalid/expired
        localStorage.removeItem("authToken");
        setToken(null);
        setStudent(null);
      })
      .finally(() => setLoading(false));
  }, [token]);

  const login = async (email, password) => {
    const res = await api.login({ email, password });
    localStorage.setItem("authToken", res.access_token);
    setToken(res.access_token);
    setStudent(res.student);
    return res.student;
  };

  const register = async (data) => {
    const res = await api.register(data);
    localStorage.setItem("authToken", res.access_token);
    setToken(res.access_token);
    setStudent(res.student);
    return res.student;
  };

  const resetPassword = async (data) => {
    const res = await api.resetPassword(data);
    localStorage.setItem("authToken", res.access_token);
    setToken(res.access_token);
    setStudent(res.student);
    return res.student;
  };

  const logout = () => {
    localStorage.removeItem("authToken");
    setToken(null);
    setStudent(null);
  };

  // Call after PUT /students/{id} succeeds, so the UI reflects new data
  // without a full re-fetch.
  const refreshStudent = (updated) => setStudent(updated);

  return (
    <AuthContext.Provider value={{ token, student, loading, login, register, resetPassword, logout, refreshStudent }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}

/**
 * Backward-compatible helper for pages that only need the active
 * student's id (most module pages were written against this shape).
 */
export function useStudent() {
  const { student } = useAuth();
  return { studentId: student?.id ?? null };
}

import React from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import StudentSnapshot from "./components/StudentSnapshot";
import { AuthProvider, useAuth } from "./AuthContext";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import Landing from "./pages/Landing";
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";
import Resume from "./pages/Resume";
import SkillGap from "./pages/SkillGap";
import Industry from "./pages/Industry";
import Roadmap from "./pages/Roadmap";
import Interview from "./pages/Interview";
import Prediction from "./pages/Prediction";
import Jobs from "./pages/Jobs";
import LearningPortals from "./pages/LearningPortals";
import Semesters from "./pages/Semesters";
import CodingTest from "./pages/CodingTest";
import Chatbot from "./pages/Chatbot";
import ExternalJobs from "./pages/ExternalJobs";

function ProtectedLayout() {
  const { student, loading } = useAuth();
  const location = useLocation();
  // The dashboard already shows these numbers as KPI cards, so the
  // snapshot panel is only shown on the individual tool pages.
  const showSnapshot = location.pathname !== "/";

  if (loading) {
    return <div style={{ padding: 40 }}>Loading...</div>;
  }
  if (!student) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="layout">
      <Sidebar />
      <div className="main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/resume" element={<Resume />} />
          <Route path="/skill-gap" element={<SkillGap />} />
          <Route path="/industry" element={<Industry />} />
          <Route path="/roadmap" element={<Roadmap />} />
          <Route path="/learning" element={<LearningPortals />} />
          <Route path="/semesters" element={<Semesters />} />
          <Route path="/coding" element={<CodingTest />} />
          <Route path="/interview" element={<Interview />} />
          <Route path="/prediction" element={<Prediction />} />
          <Route path="/jobs" element={<Jobs />} />
          <Route path="/external-jobs" element={<ExternalJobs />} />
          <Route path="/chatbot" element={<Chatbot />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
      {showSnapshot && <StudentSnapshot />}
    </div>
  );
}

function AppRoutes() {
  const { student, loading } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={!loading && student ? <Navigate to="/" replace /> : <Login />}
      />
      <Route
        path="/register"
        element={!loading && student ? <Navigate to="/" replace /> : <Register />}
      />
      <Route
        path="/forgot-password"
        element={!loading && student ? <Navigate to="/" replace /> : <ForgotPassword />}
      />
      <Route
        path="/*"
        element={
          loading ? (
            <div style={{ padding: 40 }}>Loading...</div>
          ) : student ? (
            <ProtectedLayout />
          ) : (
            <Landing />
          )
        }
      />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}

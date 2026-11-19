import React, { useEffect, useState } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";
import Icon from "./Icon";

// Grouped navigation - related tools sit together so the 14 modules are
// scannable at a glance instead of one long flat list.
const GROUPS = [
  {
    title: "Overview",
    links: [{ to: "/", label: "Dashboard", icon: "dashboard" }],
  },
  {
    title: "My Profile",
    links: [
      { to: "/profile", label: "Student Profile", icon: "user" },
      { to: "/resume", label: "Resume & ATS", icon: "file" },
      { to: "/semesters", label: "Semester Progress", icon: "calendar" },
    ],
  },
  {
    title: "Skills & Learning",
    links: [
      { to: "/skill-gap", label: "Skill Gap Analysis", icon: "target" },
      { to: "/roadmap", label: "Career Roadmap", icon: "map" },
      { to: "/learning", label: "Learning Portals", icon: "book" },
      { to: "/industry", label: "Industry Demand", icon: "trending" },
    ],
  },
  {
    title: "Practice",
    links: [
      { to: "/coding", label: "Coding Tests", icon: "code" },
      { to: "/interview", label: "AI Mock Interview", icon: "mic" },
    ],
  },
  {
    title: "Career",
    links: [
      { to: "/prediction", label: "Readiness Prediction", icon: "gauge" },
      { to: "/jobs", label: "Job Recommendations", icon: "briefcase" },
      { to: "/external-jobs", label: "LinkedIn & GitHub", icon: "link" },
      { to: "/chatbot", label: "AI Career Chatbot", icon: "chat" },
    ],
  },
];

export function initials(name = "") {
  return name.split(" ").filter(Boolean).slice(0, 2).map((p) => p[0].toUpperCase()).join("") || "S";
}

export default function Sidebar() {
  const { student, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [open, setOpen] = useState(false);

  // Close the mobile drawer whenever the route changes.
  useEffect(() => setOpen(false), [location.pathname]);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <>
      <header className="mobile-topbar">
        <button className="icon-btn" onClick={() => setOpen(true)} aria-label="Open menu">
          <Icon name="menu" size={20} />
        </button>
        <span className="mobile-brand">AI Placement &amp; Career Assistant</span>
      </header>

      {open && <div className="sidebar-scrim" onClick={() => setOpen(false)} />}

      <aside className={`sidebar ${open ? "open" : ""}`}>
        <div className="sidebar-brand">
          <div className="brand-mark"><Icon name="sparkles" size={18} /></div>
          <div>
            <div className="brand-name">AI Placement</div>
            <div className="brand-sub">&amp; Career Assistant</div>
          </div>
          <button className="icon-btn sidebar-close" onClick={() => setOpen(false)} aria-label="Close menu">
            <Icon name="close" size={18} />
          </button>
        </div>

        <nav className="sidebar-nav">
          {GROUPS.map((g) => (
            <div key={g.title} className="nav-group">
              <div className="nav-group-title">{g.title}</div>
              {g.links.map((l) => (
                <NavLink
                  key={l.to}
                  to={l.to}
                  end={l.to === "/"}
                  className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
                >
                  <Icon name={l.icon} size={17} />
                  <span>{l.label}</span>
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        {student && (
          <div className="sidebar-footer">
            <div className="sidebar-user">
              <div className="avatar">{initials(student.name)}</div>
              <div className="sidebar-user-text">
                <div className="sidebar-user-name">{student.name}</div>
                <div className="sidebar-user-email">{student.email}</div>
              </div>
            </div>
            <button className="sidebar-logout" onClick={handleLogout}>
              <Icon name="logout" size={16} /> Log out
            </button>
          </div>
        )}
      </aside>
    </>
  );
}

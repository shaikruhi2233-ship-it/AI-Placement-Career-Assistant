import React, { useState } from "react";
import { Link } from "react-router-dom";
import Icon from "./Icon";

const POINTS = [
  { icon: "file", title: "AI resume & ATS analysis", text: "Semantic scoring against real role requirements." },
  { icon: "gauge", title: "Explainable readiness score", text: "See exactly which factors raise or lower it." },
  { icon: "map", title: "Personalised roadmap", text: "Week-by-week plan to close your skill gaps." },
  { icon: "briefcase", title: "Role & job matching", text: "Ranked roles plus live openings to apply to." },
];

export function BrandMark({ light = false }) {
  return (
    <Link to="/" className={`brand ${light ? "brand-light" : ""}`}>
      <span className="brand-mark"><Icon name="sparkles" size={18} /></span>
      <span className="brand-text">
        <span className="brand-name">AI Placement</span>
        <span className="brand-sub">&amp; Career Assistant</span>
      </span>
    </Link>
  );
}

/** Labelled input with a leading icon and optional show/hide toggle for passwords. */
export function Field({ label, icon, type = "text", hint, ...props }) {
  const [show, setShow] = useState(false);
  const isPassword = type === "password";
  return (
    <div className="field">
      <label htmlFor={props.name}>{label}</label>
      <div className="field-control">
        {icon && <Icon name={icon} size={17} className="field-icon" />}
        <input id={props.name} type={isPassword && show ? "text" : type} {...props} />
        {isPassword && (
          <button
            type="button"
            className="field-toggle"
            onClick={() => setShow((v) => !v)}
            aria-label={show ? "Hide password" : "Show password"}
          >
            <Icon name={show ? "eyeOff" : "eye"} size={17} />
          </button>
        )}
      </div>
      {hint}
    </div>
  );
}

export function Alert({ tone = "error", children }) {
  return (
    <div className={`alert alert-${tone}`} role={tone === "error" ? "alert" : "status"}>
      <Icon name={tone === "error" ? "alert" : "checkCircle"} size={17} />
      <span>{children}</span>
    </div>
  );
}

export default function AuthLayout({ children }) {
  return (
    <div className="auth">
      <aside className="auth-aside">
        <BrandMark light />
        <div className="auth-aside-body">
          <span className="auth-kicker">Placement readiness, explained</span>
          <h1 className="auth-headline">Know where you stand. Know what to do next.</h1>
          <p className="auth-lede">
            An Intelligent AI-Based Placement Readiness Prediction and Career Guidance System
            with Explainable Recommendations.
          </p>
          <div className="auth-showcase" aria-hidden="true">
            <div className="glass-card gc-1">
              <div className="gc-label">Placement readiness</div>
              <div className="gc-row">
                <svg width="52" height="52" viewBox="0 0 52 52">
                  <circle cx="26" cy="26" r="21" fill="none" stroke="rgba(255,255,255,.15)" strokeWidth="6" />
                  <circle cx="26" cy="26" r="21" fill="none" stroke="#34d399" strokeWidth="6" strokeLinecap="round"
                    strokeDasharray="132" strokeDashoffset="29" transform="rotate(-90 26 26)" />
                </svg>
                <div><div className="gc-num">78%</div><div className="gc-tag">● Ready</div></div>
              </div>
            </div>
            <div className="glass-card gc-2">
              <div className="gc-label">Resume ATS score</div>
              <div className="gc-num">82<small>/100</small> <span className="gc-up">▲ 9</span></div>
              <div className="gc-bar"><i /></div>
            </div>
            <div className="glass-card gc-3">
              <div className="gc-label"><Icon name="sparkles" size={12} /> Next step</div>
              <div className="gc-text">Learn Node.js &amp; REST API</div>
            </div>
          </div>
          <ul className="auth-points">
            {POINTS.map((p) => (
              <li key={p.title}>
                <span className="auth-point-icon"><Icon name={p.icon} size={17} /></span>
                <span>
                  <strong>{p.title}</strong>
                  <span>{p.text}</span>
                </span>
              </li>
            ))}
          </ul>
        </div>
        <p className="auth-aside-foot"><Icon name="shield" size={14} /> Runs on your own machine. No paid AI APIs.</p>
      </aside>

      <main className="auth-main">
        <div className="auth-mobile-brand"><BrandMark /></div>
        <div className="auth-card">{children}</div>
      </main>
    </div>
  );
}

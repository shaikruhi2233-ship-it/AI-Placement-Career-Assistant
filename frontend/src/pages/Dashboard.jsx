import React, { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
} from "recharts";
import api from "../api";
import { useAuth, useStudent } from "../AuthContext";
import NoStudentBanner from "../components/NoStudentBanner";
import Icon from "../components/Icon";

/* ---------- helpers ---------- */

function greeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  return "Good evening";
}

function statusOf(label) {
  if (label === "Ready") return "good";
  if (label === "Moderate") return "warn";
  return "bad";
}

function scoreTone(v) {
  if (v == null) return "neutral";
  if (v >= 75) return "good";
  if (v >= 50) return "warn";
  return "bad";
}

const fmtDate = (iso) => new Date(iso).toLocaleDateString(undefined, { day: "numeric", month: "short" });
const SKILL_DISPLAY = {
  sql: "SQL", html: "HTML", css: "CSS", javascript: "JavaScript", typescript: "TypeScript",
  "node.js": "Node.js", "rest api": "REST API", aws: "AWS", gcp: "GCP", "ci/cd": "CI/CD",
  "power bi": "Power BI", mongodb: "MongoDB", mysql: "MySQL", postgresql: "PostgreSQL",
  nlp: "NLP", github: "GitHub", api: "API", hr: "HR", oop: "OOP",
};
const title = (s = "") => SKILL_DISPLAY[s.toLowerCase()] || s.replace(/\b\w/g, (c) => c.toUpperCase());

/** Animated count-up for headline numbers (respects reduced motion). */
function useCountUp(target, duration = 900) {
  const [v, setV] = useState(0);
  const raf = useRef();
  useEffect(() => {
    if (target == null) return undefined;
    if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) { setV(target); return undefined; }
    const start = performance.now();
    const tick = (now) => {
      const t = Math.min(1, (now - start) / duration);
      setV(Math.round(target * (1 - Math.pow(1 - t, 3))));
      if (t < 1) raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf.current);
  }, [target, duration]);
  return v;
}

function Num({ value }) {
  const v = useCountUp(value == null ? null : Math.round(value));
  return <>{value == null ? "—" : v}</>;
}

/* ---------- small building blocks ---------- */

function Delta({ value, suffix = "", light = false }) {
  if (value == null || value === 0) return null;
  const up = value > 0;
  return (
    <span className={`delta ${up ? "up" : "down"} ${light ? "delta-light" : ""}`}>
      <Icon name={up ? "arrowUp" : "arrowDown"} size={12} strokeWidth={2.5} />
      {Math.abs(value)}{suffix}
    </span>
  );
}

/** Semi-circular gauge used in the hero. */
function Gauge({ value, tone }) {
  const pct = Math.max(0, Math.min(100, value ?? 0));
  const r = 80, c = Math.PI * r;
  const shown = useCountUp(value == null ? null : Math.round(value), 1100);
  return (
    <div className="gauge">
      <svg viewBox="0 0 200 116" className="gauge-svg" role="img" aria-label={`Readiness ${pct}%`}>
        <defs>
          <linearGradient id="gaugeGrad" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#f87171" />
            <stop offset="50%" stopColor="#fbbf24" />
            <stop offset="100%" stopColor="#34d399" />
          </linearGradient>
        </defs>
        <path d="M20 100 A80 80 0 0 1 180 100" fill="none" stroke="rgba(255,255,255,0.14)" strokeWidth="14" strokeLinecap="round" />
        {value != null && (
          <path d="M20 100 A80 80 0 0 1 180 100" fill="none" stroke="url(#gaugeGrad)" strokeWidth="14" strokeLinecap="round"
            strokeDasharray={c} strokeDashoffset={c * (1 - pct / 100)} className="gauge-arc" />
        )}
      </svg>
      <div className="gauge-center">
        <div className="gauge-value">{value == null ? "—" : shown}<span>{value == null ? "" : "%"}</span></div>
        <div className="gauge-label">{value == null ? "Not predicted yet" : "Placement readiness"}</div>
      </div>
    </div>
  );
}

function Bar({ value = 0, tone = "accent" }) {
  return (
    <div className="bar" role="progressbar" aria-valuenow={value} aria-valuemin={0} aria-valuemax={100}>
      <div className={`bar-fill bar-${tone}`} style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
    </div>
  );
}

function EmptyState({ icon, text, cta, to }) {
  return (
    <div className="empty">
      <div className="empty-icon"><Icon name={icon} size={20} /></div>
      <p>{text}</p>
      {cta && <Link to={to} className="btn btn-secondary btn-sm">{cta} <Icon name="arrowRight" size={14} /></Link>}
    </div>
  );
}

function ChartTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const p = payload[0].payload;
  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip-label">{p.full || p.axis}</div>
      <div className="chart-tooltip-value">{p.score ?? p.value}% <span>{p.full ? "readiness" : ""}</span></div>
    </div>
  );
}

function Skeleton() {
  return (
    <div className="dash">
      <div className="sk sk-hero" />
      <div className="kpi-grid">{[0, 1, 2, 3].map((i) => <div key={i} className="sk sk-kpi" />)}</div>
      <div className="dash-row"><div className="sk sk-panel" /><div className="sk sk-panel" /></div>
    </div>
  );
}

const QUICK = [
  { to: "/resume", icon: "upload", label: "Analyse resume", desc: "NLP & ATS breakdown" },
  { to: "/interview", icon: "mic", label: "Mock interview", desc: "Technical, HR & coding" },
  { to: "/coding", icon: "code", label: "Coding test", desc: "Timed problem solving" },
  { to: "/chatbot", icon: "chat", label: "Ask AI mentor", desc: "Career questions, answered" },
];

/* ---------- page ---------- */

export default function Dashboard() {
  const { student } = useAuth();
  const { studentId } = useStudent();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!studentId) return;
    api.getDashboard(studentId).then(setData)
      .catch((err) => setError(err.response?.data?.detail || "Could not load dashboard."));
  }, [studentId]);

  if (!studentId) return <div><h2>Dashboard</h2><NoStudentBanner /></div>;
  if (error) return <div className="dash"><div className="error-banner">{error}</div></div>;
  if (!data) return <Skeleton />;

  const s = data.student;
  const ins = data.insights || {};
  const pred = data.latest_prediction;
  const resume = data.latest_resume;
  const profile = ins.profile || { percentage: 0, missing_fields: [] };
  const gap = ins.skill_gap;
  const iv = ins.interview_stats || { count: 0 };
  const cs = ins.coding_stats || { count: 0, solved: 0 };
  const steps = ins.next_steps || [];
  const matches = ins.top_matches || [];
  // "T.Anitha" / "T Anitha" / "Anitha Thayyuru" -> "Anitha" (skip initials)
  const fullName = student?.name || s.name || "";
  const firstName = fullName.split(/[\s.]+/).find((t) => t.length > 2) || fullName;

  const trend = data.readiness_trend.map((t) => ({
    name: fmtDate(t.date),
    full: new Date(t.date).toLocaleString(undefined, { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }),
    score: Math.round(t.readiness_score),
  }));

  // Profile balance radar - every axis normalised to 0-100.
  const radar = [
    { axis: "Academics", value: Math.round((s.cgpa || 0) * 10) },
    { axis: "Aptitude", value: Math.round(s.aptitude_score || 0) },
    { axis: "Coding", value: Math.round(s.coding_score || 0) },
    { axis: "Communication", value: Math.round(s.communication_score || 0) },
    { axis: "Resume", value: Math.round(resume?.ats_score || 0) },
    { axis: "Interviews", value: Math.round(iv.average || 0) },
    { axis: "Skill match", value: Math.round(gap?.match_percentage || 0) },
  ];
  const radarHasData = radar.some((r) => r.value > 0);
  const strongest = radarHasData ? [...radar].sort((a, b) => b.value - a.value)[0] : null;
  const weakest = radarHasData ? [...radar].sort((a, b) => a.value - b.value)[0] : null;

  const today = new Date().toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long" });
  const readinessTone = pred ? statusOf(pred.readiness_label) : "neutral";

  return (
    <div className="dash">
      {/* ---- Hero ---- */}
      <header className="hero">
        <div className="hero-glow" aria-hidden="true" />
        <div className="hero-main">
          <p className="hero-date">{today}</p>
          <h1 className="hero-title">{greeting()}, {firstName}</h1>
          <p className="hero-sub">
            {pred
              ? <>You are <strong>{Math.round(pred.readiness_score)}% placement-ready</strong>{gap ? <> and match <strong>{Math.round(gap.match_percentage)}%</strong> of the skills for {gap.target_role}</> : null}. {steps[0] ? <>Next best move: <strong>{steps[0].title.toLowerCase()}</strong>.</> : "Keep it up!"}</>
              : <>Complete your profile, upload your resume and run your first AI prediction to see where you stand.</>}
          </p>
          <div className="hero-meta">
            {s.branch && <span className="hero-chip">{s.branch}</span>}
            {gap && <span className="hero-chip"><Icon name="target" size={13} /> {gap.target_role}</span>}
            {s.cgpa > 0 && <span className="hero-chip">CGPA {s.cgpa}</span>}
          </div>
          <div className="hero-actions">
            <Link to="/prediction" className="btn btn-white"><Icon name="sparkles" size={16} /> Run AI prediction</Link>
            <Link to="/resume" className="btn btn-glass"><Icon name="upload" size={16} /> Upload resume</Link>
          </div>
        </div>
        <Link to="/prediction" className="hero-gauge">
          <Gauge value={pred ? pred.readiness_score : null} tone={readinessTone} />
          {pred && (
            <div className="hero-gauge-foot">
              <span className={`status status-${readinessTone} status-on-dark`}><span className="status-dot" />{pred.readiness_label}</span>
              <Delta value={ins.readiness_delta} suffix=" pts" light />
              <span className="hero-conf">{Math.round(pred.confidence_score)}% confidence</span>
            </div>
          )}
        </Link>
      </header>

      {/* ---- KPI row ---- */}
      <section className="kpi-grid">
        <Link to="/resume" className="kpi">
          <div className="kpi-head"><span className="kpi-icon ki-blue"><Icon name="file" size={16} /></span><span className="kpi-label">Resume ATS score</span></div>
          <div className="kpi-value"><Num value={resume?.ats_score} />{resume && <span className="kpi-unit">/100</span>} <Delta value={ins.ats_delta} /></div>
          {resume ? <Bar value={resume.ats_score} tone={scoreTone(resume.ats_score)} /> : <Bar value={0} />}
          <div className="kpi-foot">{resume ? `Quality ${Math.round(resume.resume_quality_score)} · Semantic ${Math.round(resume.semantic_score)}%` : "No resume uploaded"}</div>
        </Link>

        <Link to="/skill-gap" className="kpi">
          <div className="kpi-head"><span className="kpi-icon ki-violet"><Icon name="target" size={16} /></span><span className="kpi-label">Skill match</span></div>
          <div className="kpi-value"><Num value={gap?.match_percentage} />{gap && <span className="kpi-unit">%</span>}</div>
          <Bar value={gap?.match_percentage || 0} tone={scoreTone(gap?.match_percentage)} />
          <div className="kpi-foot">{gap ? `${gap.matched_skills.length}/${gap.required_count} skills · ${gap.target_role}` : "Set a career interest"}</div>
        </Link>

        <Link to="/profile" className="kpi">
          <div className="kpi-head"><span className="kpi-icon ki-green"><Icon name="user" size={16} /></span><span className="kpi-label">Profile strength</span></div>
          <div className="kpi-value"><Num value={profile.percentage} /><span className="kpi-unit">%</span></div>
          <Bar value={profile.percentage} tone={scoreTone(profile.percentage)} />
          <div className="kpi-foot">
            {profile.missing_fields.length ? `${profile.missing_fields.length} section${profile.missing_fields.length > 1 ? "s" : ""} to complete` : "All sections complete"}
          </div>
        </Link>

        <Link to="/interview" className="kpi">
          <div className="kpi-head"><span className="kpi-icon ki-amber"><Icon name="mic" size={16} /></span><span className="kpi-label">Practice</span></div>
          <div className="kpi-split">
            <div><div className="kpi-value"><Num value={iv.count} /></div><div className="kpi-foot">Interviews{iv.average != null && ` · avg ${Math.round(iv.average)}%`}</div></div>
            <div className="kpi-divider" />
            <div><div className="kpi-value"><Num value={cs.solved} /><span className="kpi-unit">/{cs.count}</span></div><div className="kpi-foot">Problems solved</div></div>
          </div>
        </Link>
      </section>

      {/* ---- Trend + Next steps ---- */}
      <section className="dash-row">
        <div className="panel panel-wide">
          <div className="panel-head">
            <div><h3>Readiness trend</h3><p className="panel-sub">Your placement-readiness score across predictions</p></div>
            {trend.length > 0 && <span className="panel-badge">{trend.length} run{trend.length > 1 ? "s" : ""}</span>}
          </div>
          {trend.length === 0 ? (
            <EmptyState icon="trending" text="Run your first readiness prediction to start tracking progress." cta="Run prediction" to="/prediction" />
          ) : (
            <div className="chart-box">
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={trend} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                  <defs>
                    <linearGradient id="readinessFill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#3b82c4" stopOpacity={0.28} />
                      <stop offset="100%" stopColor="#3b82c4" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid vertical={false} stroke="var(--grid)" />
                  <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fill: "var(--text-3)", fontSize: 12 }} />
                  <YAxis domain={[0, 100]} ticks={[0, 25, 50, 75, 100]} tickLine={false} axisLine={false} tick={{ fill: "var(--text-3)", fontSize: 12 }} />
                  <Tooltip content={<ChartTooltip />} cursor={{ stroke: "var(--border-strong)", strokeWidth: 1 }} />
                  <Area type="monotone" dataKey="score" stroke="#1f4e79" strokeWidth={2.5} fill="url(#readinessFill)"
                    dot={{ r: 4, fill: "var(--surface)", stroke: "#1f4e79", strokeWidth: 2 }}
                    activeDot={{ r: 6, fill: "#1f4e79", stroke: "var(--surface)", strokeWidth: 2 }} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        <div className="panel panel-steps">
          <div className="panel-head">
            <div><h3><Icon name="sparkles" size={16} className="title-icon" /> Your next steps</h3><p className="panel-sub">AI-prioritised from your data</p></div>
          </div>
          {steps.length === 0 ? (
            <EmptyState icon="check" text="You're all caught up. Keep practising to stay sharp!" />
          ) : (
            <ol className="steps">
              {steps.map((st, i) => (
                <li key={i}>
                  <Link to={st.to} className="step">
                    <span className={`step-num prio-${st.priority}`}>{i + 1}</span>
                    <span className="step-body">
                      <span className="step-title">{st.title}</span>
                      <span className="step-detail">{st.detail}</span>
                    </span>
                    <Icon name="arrowRight" size={16} className="step-arrow" />
                  </Link>
                </li>
              ))}
            </ol>
          )}
        </div>
      </section>

      {/* ---- Radar + Skill gap + Job matches ---- */}
      <section className="dash-row dash-row-3">
        <div className="panel">
          <div className="panel-head">
            <div><h3>Profile balance</h3><p className="panel-sub">Seven readiness dimensions, 0-100</p></div>
          </div>
          {radarHasData ? (
            <>
              <div className="radar-box">
                <ResponsiveContainer width="100%" height={240}>
                  <RadarChart data={radar} outerRadius="72%" margin={{ top: 4, right: 24, bottom: 4, left: 24 }}>
                    <PolarGrid stroke="var(--grid)" />
                    <PolarAngleAxis dataKey="axis" tick={{ fill: "var(--text-2)", fontSize: 11 }} />
                    <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
                    <Tooltip content={<ChartTooltip />} />
                    <Radar dataKey="value" stroke="#1f4e79" strokeWidth={2} fill="#3b82c4" fillOpacity={0.25}
                      dot={{ r: 3, fill: "#1f4e79" }} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
              <div className="radar-legend">
                <span><span className="dot dot-good" /> Strongest: <strong>{strongest.axis}</strong> ({strongest.value})</span>
                <span><span className="dot dot-bad" /> Focus: <strong>{weakest.axis}</strong> ({weakest.value})</span>
              </div>
            </>
          ) : (
            <EmptyState icon="layers" text="Fill in your academic scores to see your profile balance." cta="Update profile" to="/profile" />
          )}
        </div>

        <div className="panel">
          <div className="panel-head">
            <div><h3>Skill readiness</h3><p className="panel-sub">{gap ? `For ${gap.target_role}` : "Set a career interest to see this"}</p></div>
            <Link to="/skill-gap" className="link-sm">Details <Icon name="arrowRight" size={14} /></Link>
          </div>
          {gap ? (
            <>
              <div className="gap-summary">
                <div className="gap-number"><Num value={gap.match_percentage} /><span>%</span></div>
                <div className="gap-text">
                  <span><strong>{gap.matched_skills.length} of {gap.required_count}</strong> required skills matched</span>
                  <Bar value={gap.match_percentage} tone={scoreTone(gap.match_percentage)} />
                </div>
              </div>
              {gap.matched_skills.length > 0 && (
                <div className="tag-block">
                  <div className="tag-label">You have</div>
                  {gap.matched_skills.map((k) => <span key={k} className="tag tag-have"><Icon name="check" size={12} strokeWidth={3} />{title(k)}</span>)}
                </div>
              )}
              {gap.missing_skills.length > 0 && (
                <div className="tag-block">
                  <div className="tag-label">Learn next</div>
                  {gap.missing_skills.slice(0, 8).map((k) => <span key={k} className="tag tag-missing">{title(k)}</span>)}
                </div>
              )}
            </>
          ) : (
            <EmptyState icon="target" text="Add your skills and career interest to analyse your gap." cta="Update profile" to="/profile" />
          )}
        </div>

        <div className="panel">
          <div className="panel-head">
            <div><h3>Top role matches</h3><p className="panel-sub">Based on your skills & resume</p></div>
            <Link to="/jobs" className="link-sm">All jobs <Icon name="arrowRight" size={14} /></Link>
          </div>
          {matches.length === 0 || matches.every((m) => m.match_score === 0) ? (
            <EmptyState icon="briefcase" text="Add skills or upload a resume to get matched with roles." cta="Upload resume" to="/resume" />
          ) : (
            <ul className="match-list">
              {matches.map((m, i) => (
                <li key={m.role} className="match">
                  <span className={`match-rank rank-${i + 1}`}>{i + 1}</span>
                  <div className="match-body">
                    <div className="match-top">
                      <span className="match-role">{m.role}</span>
                      <span className="match-score">{Math.round(m.match_score)}%</span>
                    </div>
                    <Bar value={m.match_score} tone={scoreTone(m.match_score)} />
                    {m.companies?.length > 0 && <div className="match-co">{m.companies.join(" · ")}</div>}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>

      {/* ---- Interview history ---- */}
      {data.interview_history.length > 0 && (
        <section className="panel">
          <div className="panel-head">
            <div><h3>Recent mock interviews</h3><p className="panel-sub">Scores out of 100</p></div>
            <Link to="/interview" className="link-sm">Practise again <Icon name="arrowRight" size={14} /></Link>
          </div>
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Type</th><th className="num">Technical</th><th className="num">Communication</th><th className="num">Confidence</th><th className="num">Date</th></tr></thead>
              <tbody>
                {data.interview_history.slice(0, 5).map((h) => (
                  <tr key={h.id}>
                    <td><span className="chip">{title(h.interview_type)}</span></td>
                    {[h.technical_score, h.communication_score, h.confidence_score].map((v, i) => (
                      <td key={i} className="num"><span className={`score-pill tone-${scoreTone(v)}`}>{Math.round(v)}</span></td>
                    ))}
                    <td className="num text-3">{fmtDate(h.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* ---- Quick actions ---- */}
      <section>
        <h3 className="section-title">Quick actions</h3>
        <div className="quick-grid">
          {QUICK.map((q) => (
            <Link key={q.to} to={q.to} className="quick">
              <span className="quick-icon"><Icon name={q.icon} size={18} /></span>
              <span><span className="quick-label">{q.label}</span><span className="quick-desc">{q.desc}</span></span>
              <Icon name="arrowRight" size={16} className="quick-arrow" />
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}

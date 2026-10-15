import React, { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";
import { useStudent } from "../AuthContext";
import NoStudentBanner from "../components/NoStudentBanner";
import Icon from "../components/Icon";

const SKILL_DISPLAY = {
  sql: "SQL", html: "HTML", css: "CSS", javascript: "JavaScript", typescript: "TypeScript", "node.js": "Node.js",
  "rest api": "REST API", aws: "AWS", gcp: "GCP", "ci/cd": "CI/CD", "power bi": "Power BI", mongodb: "MongoDB",
  mysql: "MySQL", postgresql: "PostgreSQL", nlp: "NLP", github: "GitHub", "c++": "C++", "c#": "C#", c: "C",
  "next.js": "Next.js", jmeter: "JMeter", testng: "TestNG", junit: "JUnit", php: "PHP", fastapi: "FastAPI",
};
const pretty = (s = "") => SKILL_DISPLAY[s.toLowerCase()] || s.replace(/\b\w/g, (c) => c.toUpperCase());
const tone = (v) => (v >= 75 ? "good" : v >= 50 ? "warn" : "bad");

const ENTITY_META = {
  EMAIL: { label: "Email", icon: "mail" },
  PHONE: { label: "Phone", icon: "chat" },
  LINK: { label: "Links", icon: "link" },
  DEGREE: { label: "Degree", icon: "award" },
  SCORE: { label: "Score / CGPA", icon: "gauge" },
  YEAR: { label: "Dates", icon: "calendar" },
  ORG: { label: "Organisation", icon: "building" },
};

function ScoreCard({ label, value, hint }) {
  return (
    <div className="score-card">
      <div className="score-card-label">{label}</div>
      <div className="score-card-value">{Math.round(value)}<span>/100</span></div>
      <div className="bar"><div className={`bar-fill bar-${tone(value)}`} style={{ width: `${Math.min(100, value)}%` }} /></div>
      <div className="score-card-hint">{hint}</div>
    </div>
  );
}

function Pipeline({ nlp }) {
  const stages = [
    { n: 1, title: "Preprocessing", stat: `${nlp.preprocessing.tokens} tokens`, sub: `${nlp.preprocessing.sentences} sentences · ${nlp.preprocessing.stopwords_removed} stop words removed` },
    { n: 2, title: "Section segmentation", stat: `${nlp.sections.detected.length} sections`, sub: nlp.sections.detected.slice(0, 3).join(", ") || "None detected" },
    { n: 3, title: "Named entities", stat: `${Object.values(nlp.entities).reduce((a, v) => a + v.length, 0)} entities`, sub: "Email, phone, degree, CGPA, org…" },
    { n: 4, title: "Skill linking", stat: `${nlp.skills.technical.length + nlp.skills.soft.length} skills`, sub: "Alias-aware canonical matching" },
    { n: 5, title: "TF-IDF keywords", stat: `${nlp.keywords.length} keywords`, sub: "Uni + bi-grams vs role corpus" },
    { n: 6, title: "Writing analysis", stat: `${nlp.writing.action_verb_count} action verbs`, sub: `${nlp.writing.quantified_achievements} quantified achievements` },
    { n: 7, title: "Semantic similarity", stat: `${nlp.role_similarity[0]?.similarity ?? 0}% top match`, sub: nlp.role_similarity[0]?.role || "" },
  ];
  return (
    <ol className="pipeline">
      {stages.map((s) => (
        <li key={s.n} className="pipe-step">
          <span className="pipe-n">{s.n}</span>
          <div className="pipe-title">{s.title}</div>
          <div className="pipe-stat">{s.stat}</div>
          <div className="pipe-sub">{s.sub}</div>
        </li>
      ))}
    </ol>
  );
}

export default function Resume() {
  const { studentId } = useStudent();
  const [roles, setRoles] = useState([]);
  const [targetRole, setTargetRole] = useState("");
  const [file, setFile] = useState(null);
  const [drag, setDrag] = useState(false);
  const [resume, setResume] = useState(null);
  const [nlp, setNlp] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    api.listRoles().then((r) => { setRoles(r); if (r.length) setTargetRole((t) => t || r[0]); });
  }, []);

  const loadNlp = (role) => {
    if (!studentId) return;
    api.getResumeNLP(studentId, role).then(setNlp).catch(() => setNlp(null));
  };

  useEffect(() => {
    if (!studentId) return;
    api.latestResume(studentId).then((r) => { setResume(r); loadNlp(targetRole); }).catch(() => setResume(null));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [studentId]);

  useEffect(() => { if (resume) loadNlp(targetRole); /* re-target analysis */ // eslint-disable-next-line
  }, [targetRole]);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file || !targetRole) return;
    setError(""); setLoading(true);
    try {
      const result = await api.uploadResume(studentId, targetRole, file);
      setResume(result);
      loadNlp(targetRole);
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed.");
    } finally {
      setLoading(false);
    }
  };

  const onDrop = (e) => {
    e.preventDefault(); setDrag(false);
    const f = e.dataTransfer.files?.[0];
    if (f) setFile(f);
  };

  if (!studentId) return <div><h2>Resume & ATS Analyzer</h2><NoStudentBanner /></div>;

  const maxKw = nlp?.keywords?.[0]?.weight || 1;

  return (
    <div className="page">
      <header className="page-head">
        <div>
          <span className="page-eyebrow"><Icon name="file" size={14} /> Resume intelligence</span>
          <h1 className="page-title">Resume & ATS Analyzer</h1>
          <p className="page-sub">Upload your resume to run a 7-stage NLP pipeline: preprocessing, section segmentation, named-entity recognition, skill linking, TF-IDF keyword extraction, writing analysis and semantic role matching.</p>
        </div>
      </header>

      <form className="panel upload-panel" onSubmit={handleUpload}>
        <div className="upload-grid">
          <div>
            <label htmlFor="role">Target job role</label>
            <select id="role" value={targetRole} onChange={(e) => setTargetRole(e.target.value)}>
              {roles.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
            <p className="field-help">Used for ATS keyword matching and the targeted NLP report.</p>
          </div>
          <div
            className={`dropzone ${drag ? "drag" : ""} ${file ? "has-file" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
            onDragLeave={() => setDrag(false)}
            onDrop={onDrop}
            onClick={() => inputRef.current?.click()}
            role="button" tabIndex={0}
            onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && inputRef.current?.click()}
          >
            <input ref={inputRef} type="file" accept=".pdf,.docx,.txt" hidden onChange={(e) => setFile(e.target.files[0])} />
            <span className="dz-icon"><Icon name={file ? "checkCircle" : "upload"} size={22} /></span>
            {file ? (
              <><strong>{file.name}</strong><span>{(file.size / 1024).toFixed(0)} KB · click to change</span></>
            ) : (
              <><strong>Drop your resume here or click to browse</strong><span>PDF, DOCX or TXT</span></>
            )}
          </div>
        </div>
        {error && <div className="error-banner" style={{ marginTop: 16 }}>{error}</div>}
        <div className="upload-actions">
          <button type="submit" className="btn-primary-lg" disabled={loading || !file}>
            {loading ? <><span className="spinner" /> Analysing…</> : <><Icon name="sparkles" size={16} /> Upload & analyse</>}
          </button>
        </div>
      </form>

      {resume && (
        <>
          <section className="score-grid">
            <ScoreCard label="ATS compatibility" value={resume.ats_score} hint="Keywords 40% · Semantic 25% · Sections 20% · Length 15%" />
            <ScoreCard label="Resume quality" value={resume.resume_quality_score} hint="Structure, length and content balance" />
            <ScoreCard label="Semantic match" value={resume.semantic_score} hint={`TF-IDF cosine similarity to ${targetRole}`} />
          </section>

          {nlp && (
            <>
              <section className="panel">
                <div className="panel-head">
                  <div><h3><Icon name="layers" size={16} className="title-icon" /> NLP pipeline</h3><p className="panel-sub">How <strong>{nlp.filename}</strong> was processed, stage by stage</p></div>
                </div>
                <Pipeline nlp={nlp} />
              </section>

              {nlp.suggestions.length > 0 && (
                <section className="panel panel-tips">
                  <div className="panel-head"><div><h3><Icon name="sparkles" size={16} className="title-icon" /> Recommendations</h3><p className="panel-sub">Generated from the analysis below, most important first</p></div></div>
                  <ol className="tips">{nlp.suggestions.map((t, i) => <li key={i}><span className="step-num prio-medium">{i + 1}</span>{t}</li>)}</ol>
                </section>
              )}

              <section className="dash-row">
                <div className="panel">
                  <div className="panel-head"><div><h3>Named entities</h3><p className="panel-sub">Rule-based NER over the resume text</p></div></div>
                  <table className="table ner-table">
                    <tbody>
                      {Object.entries(nlp.entities).map(([k, vals]) => (
                        <tr key={k}>
                          <td className="ner-type"><span className={`ent ent-${k.toLowerCase()}`}><Icon name={ENTITY_META[k].icon} size={13} /> {ENTITY_META[k].label}</span></td>
                          <td>{vals.length ? vals.map((v) => <span key={v} className="ner-val">{v}</span>) : <span className="text-3">Not found</span>}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="panel">
                  <div className="panel-head"><div><h3>Linked skills</h3><p className="panel-sub">Canonical skills grouped by category; hover to see where each was found</p></div></div>
                  {Object.keys(nlp.skills.categorized).length === 0 && <p className="muted">No technical skills detected.</p>}
                  {Object.entries(nlp.skills.categorized).map(([cat, list]) => (
                    <div key={cat} className="tag-block">
                      <div className="tag-label">{cat}</div>
                      {list.map((sk) => (
                        <span key={sk} className="tag tag-skill" title={`Found in: ${(nlp.skills.evidence[sk] || []).join(", ") || "inferred"}`}>{pretty(sk)}</span>
                      ))}
                    </div>
                  ))}
                  {nlp.skills.soft.length > 0 && (
                    <div className="tag-block"><div className="tag-label">Soft skills</div>{nlp.skills.soft.map((sk) => <span key={sk} className="tag tag-have">{pretty(sk)}</span>)}</div>
                  )}
                  {nlp.target && nlp.target.missing.length > 0 && (
                    <div className="tag-block"><div className="tag-label">Missing for {nlp.target.role}</div>{nlp.target.missing.map((sk) => <span key={sk} className="tag tag-missing">{pretty(sk)}</span>)}</div>
                  )}
                </div>
              </section>

              <section className="dash-row">
                <div className="panel">
                  <div className="panel-head"><div><h3>TF-IDF keywords</h3><p className="panel-sub">Terms most distinctive to your resume vs. the role corpus</p></div></div>
                  <ul className="kw-list">
                    {nlp.keywords.map((k) => (
                      <li key={k.term}>
                        <span className="kw-term">{k.term}</span>
                        <span className="kw-bar"><i style={{ width: `${(k.weight / maxKw) * 100}%` }} /></span>
                        <span className="kw-w">{k.weight.toFixed(3)}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="panel">
                  <div className="panel-head"><div><h3>Semantic role similarity</h3><p className="panel-sub">Cosine similarity of TF-IDF vectors, resume vs. each role</p></div></div>
                  <ul className="match-list">
                    {nlp.role_similarity.map((r, i) => (
                      <li key={r.role} className="match">
                        <span className={`match-rank rank-${i + 1}`}>{i + 1}</span>
                        <div className="match-body">
                          <div className="match-top"><span className="match-role">{r.role}</span><span className="match-score">{r.similarity}%</span></div>
                          <div className="bar"><div className="bar-fill bar-accent" style={{ width: `${Math.min(100, (r.similarity / (nlp.role_similarity[0].similarity || 1)) * 100)}%` }} /></div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              </section>

              <section className="dash-row">
                <div className="panel">
                  <div className="panel-head"><div><h3>Writing quality</h3><p className="panel-sub">Signals recruiters and ATS systems reward</p></div></div>
                  <div className="wq-grid">
                    <div className="wq"><div className={`wq-v tone-text-${nlp.writing.action_verb_count >= 5 ? "good" : "warn"}`}>{nlp.writing.action_verb_count}</div><div className="wq-l">Action verbs</div></div>
                    <div className="wq"><div className={`wq-v tone-text-${nlp.writing.quantified_achievements >= 2 ? "good" : "warn"}`}>{nlp.writing.quantified_achievements}</div><div className="wq-l">Quantified results</div></div>
                    <div className="wq"><div className={`wq-v tone-text-${nlp.writing.weak_phrases.length ? "bad" : "good"}`}>{nlp.writing.weak_phrases.length}</div><div className="wq-l">Weak phrases</div></div>
                    <div className="wq"><div className="wq-v">{nlp.writing.avg_sentence_length}</div><div className="wq-l">Avg words / sentence</div></div>
                  </div>
                  {nlp.writing.action_verbs.length > 0 && <div className="tag-block"><div className="tag-label">Action verbs used</div>{nlp.writing.action_verbs.map((v) => <span key={v} className="tag tag-have">{v}</span>)}</div>}
                  {nlp.writing.weak_phrases.length > 0 && <div className="tag-block"><div className="tag-label">Replace these phrases</div>{nlp.writing.weak_phrases.map((v) => <span key={v} className="tag tag-weak">“{v}”</span>)}</div>}
                  {nlp.writing.quantified_examples[0] && <blockquote className="quote"><Icon name="check" size={14} /> {nlp.writing.quantified_examples[0]}</blockquote>}
                </div>

                <div className="panel">
                  <div className="panel-head"><div><h3>Preprocessing</h3><p className="panel-sub">Tokenisation → stop-word removal → lemmatisation</p></div></div>
                  <div className="wq-grid">
                    <div className="wq"><div className="wq-v">{nlp.preprocessing.tokens}</div><div className="wq-l">Tokens</div></div>
                    <div className="wq"><div className="wq-v">{nlp.preprocessing.content_tokens}</div><div className="wq-l">Content tokens</div></div>
                    <div className="wq"><div className="wq-v">{nlp.preprocessing.unique_lemmas}</div><div className="wq-l">Unique lemmas</div></div>
                    <div className="wq"><div className="wq-v">{nlp.preprocessing.lexical_diversity}</div><div className="wq-l">Lexical diversity</div></div>
                  </div>
                  <div className="token-flow">
                    {nlp.preprocessing.sample_tokens.slice(0, 8).map((t, i) => (
                      <span key={i} className="tok-pair"><span className="tok">{t}</span><Icon name="arrowRight" size={12} /><span className="tok tok-lemma">{nlp.preprocessing.sample_lemmas[i]}</span></span>
                    ))}
                  </div>
                  <div className="tag-block">
                    <div className="tag-label">Sections detected</div>
                    {nlp.sections.detected.map((s) => <span key={s} className="tag tag-have"><Icon name="check" size={12} strokeWidth={3} />{s} · {nlp.sections.word_counts[s]}w</span>)}
                    {nlp.sections.missing.map((s) => <span key={s} className="tag tag-missing">{s} missing</span>)}
                  </div>
                </div>
              </section>
            </>
          )}

          <div className="cta-strip">
            <div><strong>Your extracted skills are now part of your profile.</strong><span>See which roles you match best and what to learn next.</span></div>
            <Link to="/jobs" className="btn btn-primary">See matching jobs <Icon name="arrowRight" size={16} /></Link>
          </div>
        </>
      )}
    </div>
  );
}

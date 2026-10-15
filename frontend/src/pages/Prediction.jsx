import React, { useEffect, useState } from "react";
import api from "../api";
import { useStudent } from "../AuthContext";
import NoStudentBanner from "../components/NoStudentBanner";
import Icon from "../components/Icon";

const LABEL_TONE = { Ready: "good", Moderate: "warn", "Needs Work": "bad" };
const RATING_TONE = { High: "good", Medium: "good", Average: "warn", "Below Average": "bad", Low: "bad" };

const nice = (f) => f.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())
  .replace(/^Num /, "No. of ").replace("Ats", "ATS").replace("Cgpa", "CGPA");

function ShapChart({ importance, breakdown }) {
  const names = Object.fromEntries((breakdown || []).map((b) => [b.feature, b.display_name]));
  const rows = Object.entries(importance || {})
    .map(([k, v]) => ({ k, v, name: names[k] || nice(k) }))
    .sort((a, b) => Math.abs(b.v) - Math.abs(a.v))
    .slice(0, 10);
  const max = Math.max(...rows.map((r) => Math.abs(r.v)), 0.0001);
  return (
    <div className="shap">
      <div className="shap-legend"><span><i className="sw sw-neg" /> Lowers readiness</span><span><i className="sw sw-pos" /> Raises readiness</span></div>
      {rows.map((r) => (
        <div key={r.k} className="shap-row">
          <span className="shap-name">{r.name}</span>
          <span className="shap-track">
            <span className="shap-axis" />
            <span className={`shap-bar ${r.v >= 0 ? "pos" : "neg"}`}
              style={{ width: `${(Math.abs(r.v) / max) * 50}%`, [r.v >= 0 ? "left" : "right"]: "50%" }} />
          </span>
          <span className={`shap-val ${r.v >= 0 ? "pos" : "neg"}`}>{r.v >= 0 ? "+" : ""}{r.v.toFixed(3)}</span>
        </div>
      ))}
    </div>
  );
}

function ModelReport({ m }) {
  const cm = m.confusion_matrix;
  const total = cm.tn + cm.fp + cm.fn + cm.tp;
  const cell = (v, good) => (
    <div className={`cm-cell ${good ? "cm-good" : "cm-bad"}`} style={{ "--a": 0.12 + (v / total) * 1.6 }}>
      <strong>{v}</strong><span>{((v / total) * 100).toFixed(1)}%</span>
    </div>
  );
  const metricCards = [
    ["Accuracy", m.metrics.accuracy, "Correct predictions on unseen test data"],
    ["Precision", m.metrics.precision, "Of students predicted 'placed', how many were"],
    ["Recall", m.metrics.recall, "Of placed students, how many the model found"],
    ["F1-score", m.metrics.f1, "Harmonic mean of precision and recall"],
    ["ROC-AUC", m.metrics.roc_auc, "Ranking quality across all thresholds"],
  ];
  const maxImp = m.feature_importance[0]?.importance || 1;
  return (
    <>
      <section className="metric-grid">
        {metricCards.map(([k, v, h]) => (
          <div key={k} className="metric"><div className="metric-k">{k}</div><div className="metric-v">{v}<span>%</span></div><div className="metric-h">{h}</div></div>
        ))}
      </section>

      <section className="dash-row">
        <div className="panel">
          <div className="panel-head"><div><h3>Confusion matrix</h3><p className="panel-sub">{m.dataset.test} held-out students the model never saw during training</p></div></div>
          <div className="cm">
            <div />
            <div className="cm-h">Predicted: Not placed</div>
            <div className="cm-h">Predicted: Placed</div>
            <div className="cm-h cm-side">Actual: Not placed</div>
            {cell(cm.tn, true)}{cell(cm.fp, false)}
            <div className="cm-h cm-side">Actual: Placed</div>
            {cell(cm.fn, false)}{cell(cm.tp, true)}
          </div>
          <div className="model-facts">
            <span><Icon name="layers" size={14} /> {m.algorithm} · {m.hyperparameters.n_estimators} trees · max depth {m.hyperparameters.max_depth}</span>
            <span><Icon name="calendar" size={14} /> {m.dataset.total} records · {m.dataset.features} features · 80/20 stratified split</span>
            {m.cross_validation && <span><Icon name="check" size={14} /> 5-fold CV accuracy {m.cross_validation.mean}% ± {m.cross_validation.std}%</span>}
          </div>
        </div>

        <div className="panel">
          <div className="panel-head"><div><h3>Algorithm comparison</h3><p className="panel-sub">Same data, same split</p></div></div>
          <div className="table-wrap" style={{ margin: "0 -24px" }}>
            <table className="table">
              <thead><tr><th>Model</th><th className="num">Accuracy</th><th className="num">F1</th><th className="num">ROC-AUC</th><th>Explainability</th></tr></thead>
              <tbody>
                {(m.comparison || []).map((c) => (
                  <tr key={c.model} className={c.model.includes("deployed") ? "row-highlight" : ""}>
                    <td><strong>{c.model}</strong></td>
                    <td className="num">{c.accuracy}%</td><td className="num">{c.f1}%</td><td className="num">{c.roc_auc}%</td>
                    <td><span className="chip">{c.explainable}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="note">
            Random Forest is deployed because it models non-linear interactions between factors and supports
            exact TreeSHAP explanations for every individual prediction, which is the core of this project's
            explainable-AI goal.
          </p>
        </div>
      </section>

      <section className="panel">
        <div className="panel-head"><div><h3>Global feature importance</h3><p className="panel-sub">Mean impurity decrease across all trees</p></div></div>
        <ul className="kw-list imp-list">
          {m.feature_importance.map((f) => (
            <li key={f.feature}>
              <span className="kw-term">{nice(f.feature)}</span>
              <span className="kw-bar"><i style={{ width: `${(f.importance / maxImp) * 100}%` }} /></span>
              <span className="kw-w">{f.importance}%</span>
            </li>
          ))}
        </ul>
        <p className="note">Training data: {m.dataset.source}.</p>
      </section>
    </>
  );
}

export default function Prediction() {
  const { studentId } = useStudent();
  const [result, setResult] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [metricsErr, setMetricsErr] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [tab, setTab] = useState("result");

  useEffect(() => {
    if (!studentId) return;
    api.latestPrediction(studentId).then(setResult).catch(() => {});
  }, [studentId]);

  useEffect(() => {
    if (tab !== "model" || metrics) return;
    api.getModelMetrics().then(setMetrics).catch((e) => setMetricsErr(e.response?.data?.detail || "Could not load model metrics."));
  }, [tab, metrics]);

  const runPrediction = async () => {
    setLoading(true); setError("");
    try {
      setResult(await api.runPrediction(studentId));
      setTab("result");
    } catch (err) {
      setError(err.response?.data?.detail || "Prediction failed. Make sure the model is trained (see backend README).");
    } finally {
      setLoading(false);
    }
  };

  if (!studentId) return <div><h2>Placement Readiness Prediction</h2><NoStudentBanner /></div>;
  const t = result ? LABEL_TONE[result.readiness_label] || "warn" : "neutral";

  return (
    <div className="page">
      <header className="page-head">
        <div>
          <span className="page-eyebrow"><Icon name="gauge" size={14} /> Explainable AI</span>
          <h1 className="page-title">Placement Readiness Prediction</h1>
          <p className="page-sub">A Random Forest model scores your readiness from 14 academic, skill, resume and interview features. SHAP (SHapley Additive exPlanations) then shows exactly how much each factor pushed your score up or down.</p>
        </div>
        <button className="btn-primary-lg" onClick={runPrediction} disabled={loading}>
          {loading ? <><span className="spinner" /> Predicting…</> : <><Icon name="sparkles" size={16} /> {result ? "Run again" : "Run prediction"}</>}
        </button>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <div className="seg">
        <button className={tab === "result" ? "on" : ""} onClick={() => setTab("result")}>My prediction</button>
        <button className={tab === "model" ? "on" : ""} onClick={() => setTab("model")}>Model performance</button>
      </div>

      {tab === "result" && !result && (
        <div className="panel"><div className="empty"><div className="empty-icon"><Icon name="gauge" size={20} /></div><p>No prediction yet. Click <strong>Run prediction</strong> to get your readiness score and its explanation.</p></div></div>
      )}

      {tab === "result" && result && (
        <>
          <section className={`result-hero rh-${t}`}>
            <div className="rh-main">
              <span className={`status status-${t}`}><span className="status-dot" />{result.readiness_label}</span>
              <div className="rh-score">{Math.round(result.readiness_score)}<span>%</span></div>
              <div className="rh-label">Placement readiness score</div>
            </div>
            <div className="rh-stats">
              <div><strong>{result.placement_probability}%</strong><span>Placement probability</span></div>
              <div><strong>{result.confidence_score}%</strong><span>Model confidence</span></div>
              <div><strong>{new Date(result.created_at).toLocaleDateString(undefined, { day: "numeric", month: "short" })}</strong><span>Last run</span></div>
            </div>
          </section>

          <section className="perf-grid">
            {(result.performance_status || []).map((p) => (
              <div key={p.category} className="perf">
                <div className="perf-k">{p.category}</div>
                <div className={`perf-r tone-text-${RATING_TONE[p.rating] || "warn"}`}>{p.rating}</div>
                <div className="bar"><div className={`bar-fill bar-${RATING_TONE[p.rating] || "warn"}`} style={{ width: `${p.score_percent}%` }} /></div>
                <div className="perf-p">{Math.round(p.score_percent)}%</div>
              </div>
            ))}
          </section>

          <section className="dash-row">
            <div className="panel panel-wide">
              <div className="panel-head"><div><h3>Why this score? (SHAP)</h3><p className="panel-sub">Contribution of each factor to your prediction</p></div></div>
              <ShapChart importance={result.feature_importance} breakdown={result.feature_breakdown} />
            </div>
            <div className="panel">
              <div className="panel-head"><div><h3>Key factors</h3><p className="panel-sub">Strongest influences, from SHAP</p></div></div>
              <div className="tag-label">Helping you</div>
              <ul className="factor-list">{result.top_positive_factors.map((f) => <li key={f} className="pos"><Icon name="arrowUp" size={14} />{f.replace(/\s*\([^)]*\)$/, "")}</li>)}</ul>
              <div className="tag-label" style={{ marginTop: 16 }}>Holding you back</div>
              <ul className="factor-list">{result.top_negative_factors.map((f) => <li key={f} className="neg"><Icon name="arrowDown" size={14} />{f.replace(/\s*\([^)]*\)$/, "")}</li>)}</ul>
            </div>
          </section>

          {result.feature_breakdown?.length > 0 && (
            <section className="panel">
              <div className="panel-head"><div><h3>Your values, feature by feature</h3><p className="panel-sub">Each value normalised to 0-100% and rated</p></div></div>
              <div className="table-wrap">
                <table className="table">
                  <thead><tr><th>Feature</th><th className="num">Your value</th><th style={{ width: "35%" }}>Score</th><th>Rating</th></tr></thead>
                  <tbody>
                    {result.feature_breakdown.map((f) => (
                      <tr key={f.feature}>
                        <td>{f.display_name}</td>
                        <td className="num">{f.value}</td>
                        <td><div className="cell-bar"><div className="bar"><div className={`bar-fill bar-${RATING_TONE[f.rating] || "warn"}`} style={{ width: `${f.score_percent}%` }} /></div><span>{Math.round(f.score_percent)}%</span></div></td>
                        <td><span className={`score-pill tone-${RATING_TONE[f.rating] || "warn"}`}>{f.rating}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}
        </>
      )}

      {tab === "model" && (
        metrics ? <ModelReport m={metrics} />
          : metricsErr ? <div className="error-banner">{metricsErr}</div>
            : <div className="panel"><div className="empty"><span className="spinner spinner-dark" /><p>Evaluating the model on held-out data (first time takes ~10 seconds)…</p></div></div>
      )}
    </div>
  );
}

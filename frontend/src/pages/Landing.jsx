import React from "react";
import { Link } from "react-router-dom";
import { BrandMark } from "../components/AuthLayout";
import Icon from "../components/Icon";

const FEATURES = [
  { icon: "file", title: "Resume & ATS analysis", text: "Upload a PDF or DOCX. Skills are extracted automatically and scored with keyword coverage plus TF-IDF semantic similarity." },
  { icon: "gauge", title: "Explainable readiness score", text: "A Random Forest model predicts placement readiness, and SHAP shows how much each factor pushed your score up or down." },
  { icon: "target", title: "Skill gap analysis", text: "Compare your skills against six industry roles and see exactly what is missing, with curated resources for each skill." },
  { icon: "map", title: "Personalised roadmap", text: "A week-by-week learning plan for your target role, with a short exam at the end of every week." },
  { icon: "mic", title: "AI mock interviews", text: "Practise technical, HR and coding rounds by typing or speaking, with instant scores and feedback." },
  { icon: "briefcase", title: "Job & role matching", text: "Roles ranked by how well you match, plus live job and internship openings with LinkedIn search links." },
];

const STEPS = [
  { n: "01", title: "Build your profile", text: "Add academics and skills, or let your resume fill them in." },
  { n: "02", title: "Get your score", text: "See your readiness score and the reasons behind it." },
  { n: "03", title: "Close the gaps", text: "Follow your roadmap, practise interviews and coding." },
  { n: "04", title: "Apply with confidence", text: "Track progress and apply to roles you match best." },
];

function PreviewCard() {
  // Illustrative product preview (static sample values, clearly labelled).
  const r = 34, c = 2 * Math.PI * r;
  return (
    <div className="lp-preview" aria-hidden="true">
      <div className="lp-preview-bar"><span /><span /><span /><em>Sample dashboard</em></div>
      <div className="lp-preview-body">
        <div className="lp-pv-row">
          <div className="lp-pv-card">
            <div className="lp-pv-label">Placement readiness</div>
            <div className="lp-pv-ring">
              <svg width="84" height="84">
                <circle cx="42" cy="42" r={r} fill="none" stroke="#eef1f5" strokeWidth="8" />
                <circle cx="42" cy="42" r={r} fill="none" stroke="#16a34a" strokeWidth="8" strokeLinecap="round"
                  strokeDasharray={c} strokeDashoffset={c * 0.22} transform="rotate(-90 42 42)" />
              </svg>
              <span>78</span>
            </div>
            <div className="lp-pv-status">● Ready</div>
          </div>
          <div className="lp-pv-col">
            <div className="lp-pv-card lp-pv-mini">
              <div className="lp-pv-label">ATS score</div>
              <div className="lp-pv-num">82<small>/100</small></div>
              <div className="lp-pv-bar"><i style={{ width: "82%" }} /></div>
            </div>
            <div className="lp-pv-card lp-pv-mini">
              <div className="lp-pv-label">Skill match</div>
              <div className="lp-pv-num">75<small>%</small></div>
              <div className="lp-pv-bar"><i style={{ width: "75%" }} /></div>
            </div>
          </div>
        </div>
        <div className="lp-pv-card">
          <div className="lp-pv-label"><Icon name="sparkles" size={13} /> Next steps</div>
          <ul className="lp-pv-steps">
            <li><b>1</b> Learn Node.js &amp; REST API</li>
            <li><b>2</b> Take an HR mock interview</li>
            <li><b>3</b> Apply for Full Stack roles</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default function Landing() {
  return (
    <div className="lp">
      <header className="lp-nav">
        <div className="lp-container lp-nav-inner">
          <BrandMark />
          <nav className="lp-nav-links">
            <a href="#features">Features</a>
            <a href="#how">How it works</a>
          </nav>
          <div className="lp-nav-cta">
            <Link to="/login" className="btn btn-ghost">Log in</Link>
            <Link to="/register" className="btn btn-primary">Get started</Link>
          </div>
        </div>
      </header>

      <section className="lp-hero">
        <div className="lp-container lp-hero-inner">
          <div className="lp-hero-text">
            <span className="lp-pill"><Icon name="sparkles" size={14} /> Explainable AI for campus placements</span>
            <h1>Know how <span className="lp-hl">placement-ready</span> you are, and exactly what to do next.</h1>
            <p className="lp-lede">
              An Intelligent AI-Based Placement Readiness Prediction and Career Guidance System with
              Explainable Recommendations. Analyse your resume, close skill gaps, practise interviews
              and track your progress in one place.
            </p>
            <div className="lp-hero-cta">
              <Link to="/register" className="btn btn-primary btn-lg">Create free account <Icon name="arrowRight" size={18} /></Link>
              <Link to="/login" className="btn btn-secondary btn-lg">Log in</Link>
            </div>
            <ul className="lp-proof">
              <li><Icon name="check" size={16} strokeWidth={2.5} /> 14 career tools</li>
              <li><Icon name="check" size={16} strokeWidth={2.5} /> SHAP-explained predictions</li>
              <li><Icon name="check" size={16} strokeWidth={2.5} /> No paid APIs needed</li>
            </ul>
          </div>
          <PreviewCard />
        </div>
      </section>

      <section id="features" className="lp-section">
        <div className="lp-container">
          <div className="lp-section-head">
            <span className="lp-eyebrow">Features</span>
            <h2>Everything you need to get placement-ready</h2>
            <p>Each tool feeds the others: your resume updates your skills, your skills drive your roadmap, and everything rolls up into one explainable score.</p>
          </div>
          <div className="lp-features">
            {FEATURES.map((f) => (
              <article key={f.title} className="lp-feature">
                <span className="lp-feature-icon"><Icon name={f.icon} size={20} /></span>
                <h3>{f.title}</h3>
                <p>{f.text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="how" className="lp-section lp-section-alt">
        <div className="lp-container">
          <div className="lp-section-head">
            <span className="lp-eyebrow">How it works</span>
            <h2>From profile to placement in four steps</h2>
          </div>
          <ol className="lp-steps">
            {STEPS.map((s) => (
              <li key={s.n} className="lp-step">
                <span className="lp-step-n">{s.n}</span>
                <h3>{s.title}</h3>
                <p>{s.text}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="lp-section">
        <div className="lp-container">
          <div className="lp-cta">
            <div>
              <h2>Start your placement journey today</h2>
              <p>Create an account in under a minute and get your first readiness score.</p>
            </div>
            <Link to="/register" className="btn btn-white btn-lg">Get started <Icon name="arrowRight" size={18} /></Link>
          </div>
        </div>
      </section>

      <footer className="lp-footer">
        <div className="lp-container lp-footer-inner">
          <BrandMark />
          <p>React · FastAPI · scikit-learn · SHAP</p>
          <p>© {new Date().getFullYear()} AI Placement &amp; Career Assistant</p>
        </div>
      </footer>
    </div>
  );
}

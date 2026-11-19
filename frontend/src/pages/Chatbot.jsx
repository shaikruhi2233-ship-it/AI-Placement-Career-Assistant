import React, { useEffect, useRef, useState } from "react";
import api from "../api";
import { useAuth, useStudent } from "../AuthContext";
import Icon from "../components/Icon";

const SUGGESTIONS = [
  "What is my readiness score?",
  "Which skills am I missing for Full Stack Developer?",
  "How can I improve my resume?",
  "Find internships for me",
  "Tips for HR interview",
  "Where can I learn React?",
];

const INTENT_LABEL = {
  greeting: "Greeting", resume_help: "Resume", skill_gap: "Skill gap", interview_prep: "Interview prep",
  placement_prediction: "Readiness", job_search: "Jobs", learning_resources: "Learning",
  semester_progress: "Semester", thanks: "Thanks", fallback: "Not sure",
};

export default function Chatbot() {
  const { student } = useAuth();
  const { studentId } = useStudent();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const initials = (student?.name || "S").split(/[\s.]+/).filter(Boolean).slice(0, 2).map((p) => p[0].toUpperCase()).join("");

  useEffect(() => {
    if (studentId) {
      api.getChatHistory(studentId).then((h) => setMessages(h.map((m) => ({ role: m.role, text: m.message }))));
    }
  }, [studentId]);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" }); }, [messages, loading]);

  const send = async (text) => {
    const msg = (text ?? input).trim();
    if (!msg || loading) return;
    setMessages((m) => [...m, { role: "user", text: msg }]);
    setInput("");
    setLoading(true);
    try {
      const res = await api.sendChatMessage({ student_id: studentId, message: msg });
      setMessages((m) => [...m, { role: "bot", text: res.reply, intent: res.intent, confidence: res.confidence, grounded: res.grounded }]);
    } catch {
      setMessages((m) => [...m, { role: "bot", text: "Sorry, something went wrong. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  const onKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
  };

  return (
    <div className="page">
      <header className="page-head">
        <div>
          <span className="page-eyebrow"><Icon name="chat" size={14} /> NLP assistant</span>
          <h1 className="page-title">AI Career Chatbot</h1>
          <p className="page-sub">Your question is preprocessed (normalisation, stop-word removal, lemmatisation), embedded with TF-IDF word and character n-grams, and matched to an intent by cosine similarity. Answers use your own scores and skills whenever possible.</p>
        </div>
      </header>

      <div className="chat">
        <div className="chat-scroll">
          {messages.length === 0 && (
            <div className="chat-welcome">
              <div className="chat-bot-avatar lg"><Icon name="sparkles" size={22} /></div>
              <h3>Hi{student?.name ? `, ${student.name.split(/[\s.]+/).find((t) => t.length > 2) || student.name}` : ""}! How can I help?</h3>
              <p>Ask about your readiness score, skill gaps, resume, interviews, jobs or learning resources.</p>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`msg ${m.role === "user" ? "msg-user" : "msg-bot"}`}>
              {m.role === "user" ? <div className="avatar msg-avatar">{initials}</div> : <div className="chat-bot-avatar"><Icon name="sparkles" size={15} /></div>}
              <div className="msg-col">
                <div className="bubble">{m.text}</div>
                {m.role === "bot" && m.intent && (
                  <div className="msg-meta">
                    <span className="chip">{INTENT_LABEL[m.intent] || m.intent}</span>
                    {m.confidence != null && <span className="text-3">{Math.round(m.confidence)}% confidence</span>}
                    {m.grounded && <span className="grounded"><Icon name="check" size={12} strokeWidth={3} /> Uses your data</span>}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="msg msg-bot">
              <div className="chat-bot-avatar"><Icon name="sparkles" size={15} /></div>
              <div className="bubble typing"><span /><span /><span /></div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="chat-suggest">
          {SUGGESTIONS.map((s) => <button key={s} type="button" className="suggest" onClick={() => send(s)} disabled={loading}>{s}</button>)}
        </div>

        <div className="chat-input">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKey}
            placeholder="Ask about resumes, interviews, skill gaps…"
            aria-label="Message"
          />
          <button type="button" className="send" onClick={() => send()} disabled={loading || !input.trim()} aria-label="Send">
            <Icon name="arrowUp" size={18} strokeWidth={2.5} />
          </button>
        </div>
      </div>
    </div>
  );
}

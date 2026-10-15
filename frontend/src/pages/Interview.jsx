import React, { useEffect, useRef, useState } from "react";
import api from "../api";
import { useStudent } from "../AuthContext";
import NoStudentBanner from "../components/NoStudentBanner";

const TYPES = [
  { value: "technical", label: "Technical Interview" },
  { value: "hr", label: "HR Interview" },
  { value: "coding", label: "Coding Assessment" },
];

// Chrome/Edge expose this as webkitSpeechRecognition; other browsers may not
// support it at all, so every voice control below checks this first and
// falls back to typing silently when it's unavailable.
const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
const speechSupported = !!SpeechRecognitionAPI;

export default function Interview() {
  const { studentId } = useStudent();
  const [type, setType] = useState("technical");
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [listeningIndex, setListeningIndex] = useState(null);
  const [voiceMode, setVoiceMode] = useState(speechSupported);
  const recognitionRef = useRef(null);

  useEffect(() => {
    if (!speechSupported) return;
    const recognition = new SpeechRecognitionAPI();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";
    recognitionRef.current = recognition;
    return () => recognition.stop();
  }, []);

  const startInterview = async () => {
    setError(""); setResult(null);
    try {
      const qs = await api.getInterviewQuestions(type, 3);
      setQuestions(qs);
      setAnswers(new Array(qs.length).fill(""));
    } catch (err) {
      setError(err.response?.data?.detail || "Could not load questions.");
    }
  };

  const handleAnswerChange = (i, value) => {
    const next = [...answers];
    next[i] = value;
    setAnswers(next);
  };

  // Reads a question aloud using the browser's built-in text-to-speech.
  const speakQuestion = (text) => {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    window.speechSynthesis.speak(utterance);
  };

  // Toggles voice dictation into the answer box at index i using the Web
  // Speech API — transcribed speech is appended to whatever's already typed,
  // so voice and typing can be mixed freely.
  const toggleListening = (i) => {
    const recognition = recognitionRef.current;
    if (!recognition) return;

    if (listeningIndex === i) {
      recognition.stop();
      setListeningIndex(null);
      return;
    }

    if (listeningIndex !== null) recognition.stop();

    let baseText = answers[i] ? answers[i] + " " : "";
    recognition.onresult = (event) => {
      let transcript = "";
      for (let r = 0; r < event.results.length; r++) {
        transcript += event.results[r][0].transcript;
      }
      handleAnswerChange(i, (baseText + transcript).trim());
    };
    recognition.onerror = () => setListeningIndex(null);
    recognition.onend = () => setListeningIndex((cur) => (cur === i ? null : cur));

    setListeningIndex(i);
    recognition.start();
  };

  const submit = async () => {
    if (listeningIndex !== null) recognitionRef.current?.stop();
    setLoading(true); setError("");
    try {
      const res = await api.submitInterview({ student_id: studentId, interview_type: type, answers });
      setResult(res);
      setQuestions([]);
    } catch (err) {
      setError(err.response?.data?.detail || "Submission failed.");
    } finally {
      setLoading(false);
    }
  };

  if (!studentId) return <div><h2>AI Mock Interview</h2><NoStudentBanner /></div>;

  return (
    <div>
      <h2>AI Mock Interview</h2>

      <div className="card">
        <label>Interview Type</label>
        <select value={type} onChange={(e) => setType(e.target.value)}>
          {TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
        </select>

        {speechSupported ? (
          <label style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 12, fontWeight: 400 }}>
            <input
              type="checkbox"
              checked={voiceMode}
              onChange={(e) => setVoiceMode(e.target.checked)}
              style={{ width: "auto" }}
            />
            🎤 Voice mode — hear questions read aloud and answer by speaking
          </label>
        ) : (
          <p className="muted" style={{ marginTop: 12 }}>
            🎤 Voice mode isn't supported in this browser — try Chrome or Edge for voice-based interviews.
          </p>
        )}

        <button onClick={startInterview}>Start Interview</button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {questions.length > 0 && (
        <div className="card">
          <h3>Answer the following questions</h3>
          {questions.map((q, i) => (
            <div key={i} style={{ marginBottom: 20 }}>
              <label>{i + 1}. {q.question}</label>
              <div style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
                <textarea rows={3} value={answers[i]} onChange={(e) => handleAnswerChange(i, e.target.value)}
                          style={{ flex: 1 }} />
                {voiceMode && speechSupported && (
                  <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 12 }}>
                    <button
                      type="button"
                      onClick={() => speakQuestion(q.question)}
                      style={{ padding: "6px 10px", fontSize: 12 }}
                    >
                      🔊 Hear
                    </button>
                    <button
                      type="button"
                      onClick={() => toggleListening(i)}
                      style={{
                        padding: "6px 10px", fontSize: 12,
                        background: listeningIndex === i ? "var(--bad)" : undefined,
                      }}
                    >
                      {listeningIndex === i ? "⏹ Stop" : "🎤 Speak"}
                    </button>
                  </div>
                )}
              </div>
              {listeningIndex === i && <p className="muted" style={{ marginTop: 4 }}>Listening...</p>}
            </div>
          ))}
          <button onClick={submit} disabled={loading || answers.some((a) => !a.trim())}>
            {loading ? "Evaluating..." : "Submit Answers"}
          </button>
        </div>
      )}

      {result && (
        <div className="card">
          <h3>Result: {result.interview_type} interview</h3>
          <div className="score-row">
            <div className="score-box"><div className="value">{result.technical_score}</div><div className="label">Technical</div></div>
            <div className="score-box"><div className="value">{result.communication_score}</div><div className="label">Communication</div></div>
            <div className="score-box"><div className="value">{result.confidence_score}</div><div className="label">Confidence</div></div>
          </div>
          <p style={{ marginTop: 16 }}>{result.feedback}</p>
        </div>
      )}
    </div>
  );
}

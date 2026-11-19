import axios from "axios";

// Vite dev server proxies /api -> http://localhost:8000 (see vite.config.js).
const client = axios.create({ baseURL: "/api" });

// Attach the JWT (if present) to every request.
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("authToken");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const api = {
  // Authentication
  register: (data) => client.post("/auth/register", data).then((r) => r.data),
  login: (data) => client.post("/auth/login", data).then((r) => r.data),
  resetPassword: (data) => client.post("/auth/reset-password", data).then((r) => r.data),
  me: () => client.get("/auth/me").then((r) => r.data),

  // Module 1 - Student Profile
  listStudents: () => client.get("/students/").then((r) => r.data),
  getStudent: (id) => client.get(`/students/${id}`).then((r) => r.data),
  updateStudent: (id, data) => client.put(`/students/${id}`, data).then((r) => r.data),

  // Module 2 & 3 - Resume + ATS
  uploadResume: (studentId, targetRole, file) => {
    const form = new FormData();
    form.append("file", file);
    return client
      .post(`/resume/upload/${studentId}?target_role=${encodeURIComponent(targetRole)}`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },
  latestResume: (studentId) => client.get(`/resume/${studentId}/latest`).then((r) => r.data),
  // Full NLP pipeline breakdown of the latest resume
  getResumeNLP: (studentId, targetRole) =>
    client.get(`/resume/${studentId}/nlp-analysis${targetRole ? `?target_role=${encodeURIComponent(targetRole)}` : ""}`).then((r) => r.data),

  // Module 4 - Skill Gap
  listRoles: () => client.get("/skills/roles").then((r) => r.data),
  getSkillGap: (studentId, targetRole) =>
    client.get(`/skills/gap/${studentId}?target_role=${encodeURIComponent(targetRole)}`).then((r) => r.data),

  // Module 5 - Industry Demand
  getIndustryDemand: () => client.get("/industry/demand").then((r) => r.data),

  // Module 6 - Roadmap
  getRoadmap: (studentId, targetRole) =>
    client.get(`/roadmap/${studentId}?target_role=${encodeURIComponent(targetRole)}`).then((r) => r.data),

  // End-of-week exam for the roadmap: pass that week's focus skills (array)
  getWeekQuiz: (skills) =>
    client.get(`/roadmap/week-quiz?skills=${encodeURIComponent(skills.join(","))}`).then((r) => r.data),

  // AI Career Guidance ("You are 58% ready for this role...")
  getCareerGuidance: (studentId, targetRole) =>
    client.get(`/roadmap/guidance/${studentId}?target_role=${encodeURIComponent(targetRole)}`).then((r) => r.data),

  // Module 7 - Mock Interview
  getInterviewQuestions: (type, count = 3) =>
    client.get(`/interview/questions?interview_type=${type}&count=${count}`).then((r) => r.data),
  submitInterview: (payload) => client.post("/interview/submit", payload).then((r) => r.data),
  interviewHistory: (studentId) => client.get(`/interview/history/${studentId}`).then((r) => r.data),

  // Module 8 & 9 - Prediction + Explainable AI
  runPrediction: (studentId) => client.post(`/prediction/${studentId}`).then((r) => r.data),
  latestPrediction: (studentId) => client.get(`/prediction/${studentId}/latest`).then((r) => r.data),
  // Held-out model evaluation (accuracy, precision, recall, F1, ROC-AUC, confusion matrix, CV)
  getModelMetrics: () => client.get("/prediction/model/metrics").then((r) => r.data),

  // Module 10 - Job Recommendation
  recommendJobs: (studentId) => client.get(`/jobs/recommend/${studentId}`).then((r) => r.data),

  // Real Job Opportunities for a role (live-fetched, company, location, job type, apply link)
  getJobOpportunities: (role, studentId) =>
    client
      .get(`/jobs/opportunities/${encodeURIComponent(role)}${studentId ? `?student_id=${studentId}` : ""}`)
      .then((r) => r.data),

  // Real internships for a role (same live-fetch + fallback behaviour)
  getInternships: (role, studentId) =>
    client
      .get(`/jobs/internships/${encodeURIComponent(role)}${studentId ? `?student_id=${studentId}` : ""}`)
      .then((r) => r.data),

  // Module 11 - Dashboard
  getDashboard: (studentId) => client.get(`/dashboard/${studentId}`).then((r) => r.data),

  // Learning Portals
  getLearningPortals: () => client.get("/learning/portals").then((r) => r.data),

  // Skill-specific Learning Resources (YouTube / Notes / Docs / Course / Practice / Project)
  getSkillResources: (skill) => client.get(`/learning/resources/${encodeURIComponent(skill)}`).then((r) => r.data),

  // Semester-wise Improvement Tracking
  addSemesterRecord: (studentId, data) => client.post(`/semesters/${studentId}`, data).then((r) => r.data),
  getSemesterTrend: (studentId) => client.get(`/semesters/${studentId}`).then((r) => r.data),
  deleteSemesterRecord: (studentId, recordId) =>
    client.delete(`/semesters/${studentId}/${recordId}`).then((r) => r.data),

  // Coding Tests
  listCodingProblems: (difficulty) =>
    client.get(`/coding/problems${difficulty ? `?difficulty=${difficulty}` : ""}`).then((r) => r.data),
  getCodingProblem: (problemId) => client.get(`/coding/problems/${problemId}`).then((r) => r.data),
  submitCode: (payload) => client.post("/coding/submit", payload).then((r) => r.data),
  codingHistory: (studentId) => client.get(`/coding/history/${studentId}`).then((r) => r.data),

  // AI Career Chatbot
  sendChatMessage: (payload) => client.post("/chatbot/message", payload).then((r) => r.data),
  getChatHistory: (studentId) => client.get(`/chatbot/history/${studentId}`).then((r) => r.data),

  // LinkedIn & GitHub Opportunities
  getExternalOpportunities: (studentId) => client.get(`/external-jobs/${studentId}`).then((r) => r.data),

  // Job Applications (Tracker)
  listApplications: () => client.get("/applications/").then((r) => r.data),
  applyToJob: (payload) => client.post("/applications/", payload).then((r) => r.data),
  updateApplicationStatus: (id, status) => client.put(`/applications/${id}`, { status }).then((r) => r.data),
  withdrawApplication: (id) => client.delete(`/applications/${id}`).then((r) => r.data),
};

export default api;

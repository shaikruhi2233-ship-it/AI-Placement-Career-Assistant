"""
Master vocabulary used for keyword-based skill/entity extraction.
A production system would swap this for a trained spaCy NER pipeline
(see services/resume_parser.py for the extension point).
"""

TECHNICAL_SKILLS = [
    "python", "java", "c++", "c", "javascript", "typescript", "react", "angular", "vue",
    "node.js", "express", "django", "flask", "fastapi", "spring boot", "html", "css",
    "sql", "mysql", "postgresql", "mongodb", "redis", "aws", "azure", "gcp", "docker",
    "kubernetes", "terraform", "ci/cd", "git", "github", "linux", "bash",
    "data structures", "algorithms", "system design", "rest api", "graphql",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "opencv",
    "power bi", "tableau", "excel", "statistics", "machine learning", "deep learning",
    "nlp", "computer vision", "spark", "hadoop", "kafka", "jenkins", "jira", "postman",
    # Testing & QA
    "manual testing", "automation testing", "selenium", "pytest", "junit", "testng", "jest",
    "cypress", "playwright", "jmeter",
    # More languages / web stack
    "c#", "php", "kotlin", "next.js", "bootstrap", "tailwind", "firebase",
]

SOFT_SKILLS = [
    "communication", "teamwork", "leadership", "problem solving", "time management",
    "adaptability", "critical thinking", "collaboration", "creativity", "attention to detail",
    "stakeholder management", "business acumen", "research mindset",
]

EDUCATION_KEYWORDS = [
    "b.tech", "btech", "b.e", "be ", "bachelor", "m.tech", "mtech", "master",
    "mca", "bca", "msc", "bsc", "phd", "diploma", "12th", "10th", "cgpa", "gpa",
]

EXPERIENCE_KEYWORDS = [
    "intern", "internship", "experience", "worked at", "employed", "trainee", "freelance",
]

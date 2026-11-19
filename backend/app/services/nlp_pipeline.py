"""
Resume NLP Pipeline.

A complete, explainable natural-language-processing pipeline over the raw
resume text. Every stage is implemented here (no black-box API) so each
step can be shown and justified:

  1. Text preprocessing   - unicode/bullet cleaning, sentence segmentation,
                             tokenisation, stop-word removal, light
                             suffix-stripping lemmatisation, corpus statistics
  2. Section segmentation - detects resume section headers (Education,
                             Experience, Projects, Skills, ...) and splits the
                             document into labelled sections
  3. Named-entity recognition (rule-based) - EMAIL, PHONE, URL / LinkedIn /
                             GitHub, DEGREE, SCORE (CGPA / %), YEAR, ORG
  4. Skill entity linking - alias-aware matching of surface forms ("JS",
                             "React.js", "K8s", "Amazon Web Services") to a
                             canonical skill vocabulary, with token-boundary
                             rules that avoid false positives ("CV" is not
                             Computer Vision, "React.js" is not JavaScript)
  5. Keyword extraction   - TF-IDF (uni+bi-grams) using the industry role
                             descriptions as the background corpus, so the
                             IDF weights are meaningful
  6. Writing-quality analysis - action verbs, quantified achievements,
                             weak phrases, first-person pronouns, sentence
                             length
  7. Semantic role similarity - TF-IDF vectors + cosine similarity between
                             the resume and every role in the dataset
"""
import re
import unicodedata
from collections import Counter, OrderedDict
from typing import Dict, List, Optional, Tuple

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.data.skill_vocabulary import SOFT_SKILLS, TECHNICAL_SKILLS

# --------------------------------------------------------------------------
# 4. Skill entity linking: surface form -> canonical vocabulary term
# --------------------------------------------------------------------------

SKILL_ALIASES: Dict[str, str] = {
    "js": "javascript", "es6": "javascript", "ecmascript": "javascript",
    "ts": "typescript",
    "reactjs": "react", "react.js": "react", "react js": "react",
    "nodejs": "node.js", "node js": "node.js", "node": "node.js",
    "expressjs": "express", "express.js": "express",
    "vuejs": "vue", "vue.js": "vue", "angularjs": "angular",
    "k8s": "kubernetes",
    "amazon web services": "aws",
    "google cloud platform": "gcp", "google cloud": "gcp",
    "microsoft azure": "azure",
    "natural language processing": "nlp",
    "ml": "machine learning", "dl": "deep learning",
    "postgres": "postgresql", "my sql": "mysql",
    "sklearn": "scikit-learn", "scikit learn": "scikit-learn",
    "powerbi": "power bi", "ms excel": "excel", "microsoft excel": "excel",
    "cpp": "c++",
    "dsa": "data structures", "data structure": "data structures",
    "restful": "rest api", "rest apis": "rest api", "restful api": "rest api", "restful apis": "rest api",
    "ci cd": "ci/cd", "cicd": "ci/cd",
    "springboot": "spring boot", "github actions": "ci/cd",
    "shell scripting": "bash",
    "nextjs": "next.js", "next js": "next.js", "tailwindcss": "tailwind", "tailwind css": "tailwind",
    "selenium webdriver": "selenium", "test automation": "automation testing",
    "functional testing": "manual testing", "qa testing": "manual testing", "software testing": "manual testing",
}

SKILL_IMPLIES: Dict[str, str] = {"mysql": "sql", "postgresql": "sql", "selenium": "automation testing",
                                  "pytest": "automation testing", "playwright": "automation testing",
                                  "cypress": "automation testing"}

# Characters that may appear *inside* a skill token (c++, c#, node.js, ci/cd)
_TOKEN_CHARS = r"a-z0-9+#"


def _term_pattern(term: str) -> re.Pattern:
    """Whole-token match for a (possibly multi-word / symbol-bearing) term.
    Not preceded by a token character or '.', and not followed by a token
    character or '.<letter>' - so 'node' does not match inside 'node.js',
    'js' does not match inside 'react.js', and 'c' does not match 'c++'."""
    body = re.escape(term.lower()).replace(r"\ ", r"[\s\-]+")
    return re.compile(rf"(?<![{_TOKEN_CHARS}.]){body}(?![{_TOKEN_CHARS}])(?!\.[a-z])")


# The single-letter language "C" needs context, otherwise "Grade C" or an
# initial like "T. C. Rao" would be read as a programming language.
_C_LANGUAGE = re.compile(
    r"(?<![a-z0-9+#.])c(?![a-z0-9+#])(?=\s*(?:,|/|\||&|and\b|programming|language))"
    r"|(?:[,/|:]\s*)c(?![a-z0-9+#.])"
)

_VOCAB_PATTERNS = {t: _term_pattern(t) for t in TECHNICAL_SKILLS + SOFT_SKILLS if t != "c"}
_ALIAS_PATTERNS = {a: _term_pattern(a) for a in SKILL_ALIASES}

SKILL_CATEGORIES: Dict[str, List[str]] = OrderedDict([
    ("Programming languages", ["python", "java", "c++", "c", "c#", "javascript", "typescript", "php", "kotlin", "bash"]),
    ("Web development", ["next.js", "bootstrap", "tailwind", "react", "angular", "vue", "node.js", "express", "django", "flask", "fastapi",
                         "spring boot", "html", "css", "rest api", "graphql"]),
    ("Data & AI", ["pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "opencv",
                   "machine learning", "deep learning", "nlp", "computer vision", "statistics",
                   "power bi", "tableau", "excel", "spark", "hadoop"]),
    ("Databases", ["sql", "mysql", "postgresql", "mongodb", "redis", "firebase"]),
    ("Cloud & DevOps", ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd", "jenkins",
                        "linux", "kafka"]),
    ("Testing & QA", ["manual testing", "automation testing", "selenium", "pytest", "junit", "testng",
                      "jest", "cypress", "playwright", "jmeter", "postman"]),
    ("Tools & practices", ["git", "github", "jira", "data structures", "algorithms",
                           "system design"]),
])


def link_skills(text: str) -> Tuple[List[str], List[str]]:
    """Return (technical, soft) canonical skills found in `text`."""
    low = text.lower()
    found = set()
    for term, pat in _VOCAB_PATTERNS.items():
        if pat.search(low):
            found.add(term)
    for alias, canonical in SKILL_ALIASES.items():
        if _ALIAS_PATTERNS[alias].search(low):
            found.add(canonical)
    if _C_LANGUAGE.search(low):
        found.add("c")
    # Implied skills: using a SQL database implies SQL.
    for skill, implied in SKILL_IMPLIES.items():
        if skill in found:
            found.add(implied)
    technical = [t for t in TECHNICAL_SKILLS if t in found]
    soft = [s for s in SOFT_SKILLS if s in found]
    return technical, soft


def normalize_for_matching(text: str) -> str:
    """Single-pass alias canonicalisation (no cascading rewrites) used before
    TF-IDF so 'Amazon Web Services' and 'AWS' share one token."""
    low = (text or "").lower()
    if not low:
        return ""
    aliases = sorted(SKILL_ALIASES, key=len, reverse=True)
    body = "|".join(re.escape(a).replace(r"\ ", r"[\s\-]+") for a in aliases)
    pattern = re.compile(rf"(?<![{_TOKEN_CHARS}.])({body})(?![{_TOKEN_CHARS}])(?!\.[a-z])")

    def repl(m: re.Match) -> str:
        key = re.sub(r"[\s\-]+", " ", m.group(1))
        return SKILL_ALIASES.get(key, m.group(1))

    return pattern.sub(repl, low)


# --------------------------------------------------------------------------
# 1. Preprocessing
# --------------------------------------------------------------------------

_BULLETS = re.compile(r"[•●▪■‣⁃∙➢►–—]")
_WORD = re.compile(r"[a-z][a-z0-9+#]*(?:\.[a-z0-9]+)*")


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = _BULLETS.sub("\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n", text)
    return [p.strip() for p in parts if len(p.strip().split()) >= 3]


def tokenize(text: str) -> List[str]:
    return _WORD.findall(text.lower())


def strip_contact(text: str) -> str:
    """Remove emails, URLs and phone numbers so they don't pollute tokens/keywords."""
    text = _EMAIL.sub(" ", text)
    text = _URL.sub(" ", text)
    return _PHONE.sub(" ", text)


_E_ENDINGS = ("at", "iz", "is", "bl", "ur", "uc", "ag", "iv", "ov", "ut", "os", "rc", "dg", "nc", "ir", "ys")


def lemmatize(token: str) -> str:
    """Light rule-based lemmatiser (suffix stripping) - enough to merge
    'projects'/'project', 'developed'/'develop', 'technologies'/'technology'."""
    if len(token) <= 4 or not token.isalpha():
        return token
    for suffix, repl in (("ies", "y"), ("sses", "ss"), ("ing", ""), ("ed", ""), ("es", "e"), ("s", "")):
        if token.endswith(suffix) and len(token) - len(suffix) >= 3:
            if suffix == "s" and token.endswith(("ss", "us", "is")):
                continue
            stem = token[: -len(suffix)] + repl
            # restore the silent 'e' dropped by -ed / -ing (motivated -> motivate)
            if suffix in ("ed", "ing") and stem.endswith(_E_ENDINGS):
                stem += "e"
            if suffix in ("ed", "ing") and len(stem) > 3 and stem[-1] == stem[-2] and stem[-1] not in "lsz":
                stem = stem[:-1]  # doubled consonant: planned -> plan
            return stem
    return token


# --------------------------------------------------------------------------
# 2. Section segmentation
# --------------------------------------------------------------------------

SECTION_HEADERS: Dict[str, List[str]] = OrderedDict([
    ("Summary", ["summary", "profile", "objective", "career objective", "about me", "professional summary"]),
    ("Education", ["education", "academic", "academics", "qualification", "qualifications", "educational qualification"]),
    ("Experience", ["experience", "work experience", "internship", "internships", "employment", "professional experience"]),
    ("Projects", ["projects", "project", "academic projects", "personal projects", "key projects"]),
    ("Skills", ["skills", "technical skills", "key skills", "core competencies", "technologies", "tech stack", "skill set"]),
    ("Certifications", ["certifications", "certification", "certificates", "courses", "licenses"]),
    ("Achievements", ["achievements", "awards", "honors", "honours", "accomplishments"]),
    ("Activities", ["activities", "extracurricular", "extra curricular", "volunteering", "leadership", "positions of responsibility"]),
])
RECOMMENDED_SECTIONS = ["Summary", "Education", "Skills", "Projects", "Experience", "Certifications"]

_HEADER_LOOKUP = {h: name for name, hs in SECTION_HEADERS.items() for h in hs}


def segment_sections(text: str) -> "OrderedDict[str, str]":
    sections: "OrderedDict[str, List[str]]" = OrderedDict()
    current = "Header"
    sections[current] = []
    for line in text.split("\n"):
        stripped = line.strip()
        key = re.sub(r"[^a-z ]", "", stripped.lower()).strip()
        if key and len(key.split()) <= 4 and key in _HEADER_LOOKUP:
            current = _HEADER_LOOKUP[key]
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(stripped)
    return OrderedDict((k, "\n".join(v).strip()) for k, v in sections.items() if "\n".join(v).strip())


# --------------------------------------------------------------------------
# 3. Rule-based named-entity recognition
# --------------------------------------------------------------------------

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"(?:\+?91[\s-]?)?(?<!\d)[6-9]\d{4}[\s-]?\d{5}(?!\d)")
_URL = re.compile(r"(?:https?://)?(?:www\.)?(?:linkedin\.com/in/[\w-]+|github\.com/[\w-]+|[\w-]+\.(?:dev|io|me|vercel\.app|netlify\.app|github\.io)(?:/[\w-]*)?)", re.I)
_DEGREE = re.compile(r"\b(?:b\.?\s?tech|m\.?\s?tech|b\.?\s?e\.?(?=\s)|m\.?\s?e\.?(?=\s)|mca|bca|m\.?\s?sc|b\.?\s?sc|mba|bba|b\.?\s?com|ph\.?\s?d|diploma|intermediate|ssc|hsc|12th|10th)\b", re.I)
_SCORE = re.compile(r"\b(?:c?gpa|sgpa|percentage|score)\s*[:\-]?\s*(\d{1,2}(?:\.\d{1,2})?)\s*(?:/\s*10)?|\b(\d{1,2}(?:\.\d{1,2})?)\s*(?:cgpa|/\s*10)\b|\b(\d{2}(?:\.\d{1,2})?)\s*%", re.I)
_YEAR = re.compile(r"\b(?:19|20)\d{2}\b(?:\s*[-–to]+\s*(?:(?:19|20)\d{2}|present|current))?", re.I)
_ORG = re.compile(r"[^\n,]*\b(?:university|college|institute|school|academy|technologies|solutions|pvt\.?\s*ltd|limited|labs|systems|infotech|software)\b[^\n,]*", re.I)

DEGREE_DISPLAY = {"btech": "B.Tech", "mtech": "M.Tech", "be": "B.E", "me": "M.E", "mca": "MCA", "bca": "BCA",
                  "msc": "M.Sc", "bsc": "B.Sc", "mba": "MBA", "bba": "BBA", "bcom": "B.Com", "phd": "Ph.D",
                  "diploma": "Diploma", "intermediate": "Intermediate", "ssc": "SSC", "hsc": "HSC",
                  "12th": "12th", "10th": "10th"}


def extract_entities(text: str) -> Dict[str, List[str]]:
    def uniq(items):
        return list(OrderedDict.fromkeys(i.strip(" .,;:") for i in items if i and i.strip()))

    degrees = []
    for m in _DEGREE.finditer(text):
        key = re.sub(r"[^a-z0-9]", "", m.group(0).lower())
        degrees.append(DEGREE_DISPLAY.get(key, m.group(0).upper()))
    scores = []
    for m in _SCORE.finditer(text):
        val = next(g for g in m.groups() if g)
        scores.append(m.group(0).strip())
        _ = val
    orgs = [o.strip() for o in _ORG.findall(text) if 3 <= len(o.split()) <= 12]
    links = [u for u in _URL.findall(text)]
    return {
        "EMAIL": uniq(_EMAIL.findall(text))[:3],
        "PHONE": uniq(_PHONE.findall(text))[:2],
        "LINK": uniq(links)[:5],
        "DEGREE": uniq(degrees)[:6],
        "SCORE": uniq(scores)[:6],
        "YEAR": uniq(_YEAR.findall(text))[:8],
        "ORG": uniq(orgs)[:6],
    }


# --------------------------------------------------------------------------
# 6. Writing-quality analysis
# --------------------------------------------------------------------------

ACTION_VERBS = {
    "achieved", "analyzed", "analysed", "architected", "automated", "built", "collaborated", "created",
    "delivered", "deployed", "designed", "developed", "engineered", "enhanced", "established", "implemented",
    "improved", "increased", "integrated", "launched", "led", "managed", "mentored", "migrated", "optimized",
    "optimised", "organized", "organised", "reduced", "researched", "resolved", "spearheaded", "streamlined",
    "tested", "trained", "transformed", "won", "coordinated", "configured", "contributed", "published",
}
WEAK_PHRASES = ["responsible for", "worked on", "helped with", "involved in", "duties included",
                "various", "etc", "hard working", "hardworking", "team player", "go-getter"]
_QUANT = re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|\+|x\b|k\b|lakh|users|students|members|ms\b|seconds|hours|days|percent)", re.I)
_FIRST_PERSON = re.compile(r"\b(?:i|me|my|mine|myself)\b", re.I)


def writing_quality(text: str, sents: List[str], tokens: List[str]) -> Dict:
    verbs = Counter(t for t in tokens if t in ACTION_VERBS)
    low = text.lower()
    weak = [p for p in WEAK_PHRASES if re.search(rf"\b{re.escape(p)}\b", low)]
    quant = [s for s in sents if _QUANT.search(s)]
    avg_len = round(sum(len(s.split()) for s in sents) / len(sents), 1) if sents else 0.0
    return {
        "action_verbs": [v for v, _ in verbs.most_common(10)],
        "action_verb_count": sum(verbs.values()),
        "quantified_achievements": len(quant),
        "quantified_examples": quant[:3],
        "weak_phrases": weak,
        "first_person_count": len(_FIRST_PERSON.findall(text)),
        "avg_sentence_length": avg_len,
    }


# --------------------------------------------------------------------------
# 5 + 7. TF-IDF keywords and role similarity
# --------------------------------------------------------------------------

def _role_documents(industry_skills: Dict) -> Dict[str, str]:
    docs = {}
    for role, data in industry_skills.items():
        parts = (data.get("technical_skills", []) + data.get("soft_skills", []) +
                 data.get("certifications", []) + data.get("projects", []))
        docs[role] = normalize_for_matching(" ".join([role] + parts))
    return docs


def tfidf_keywords_and_similarity(text: str, industry_skills: Dict, top_n: int = 12) -> Tuple[List[Dict], List[Dict]]:
    resume_doc = normalize_for_matching(text)
    role_docs = _role_documents(industry_skills)
    corpus = [resume_doc] + list(role_docs.values())
    try:
        vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True,
                              token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9+#.]*[a-zA-Z0-9+#]\b|\b[a-zA-Z]\b")
        matrix = vec.fit_transform(corpus)
    except ValueError:
        return [], []
    terms = vec.get_feature_names_out()
    row = matrix[0].toarray()[0]
    order = row.argsort()[::-1]
    keywords = []
    for i in order:
        if row[i] <= 0 or len(keywords) >= top_n:
            break
        term = terms[i]
        if term.isdigit() or len(term) < 2:
            continue
        keywords.append({"term": term, "weight": round(float(row[i]), 3)})
    sims = cosine_similarity(matrix[0:1], matrix[1:])[0]
    roles = sorted(
        ({"role": r, "similarity": round(float(s) * 100, 1)} for r, s in zip(role_docs, sims)),
        key=lambda x: x["similarity"], reverse=True,
    )
    return keywords, roles


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------

def analyze(raw_text: str, industry_skills: Dict, target_role: Optional[str] = None) -> Dict:
    text = clean_text(raw_text)
    body = strip_contact(text)
    sents = sentences(body)
    tokens = tokenize(body)
    content_tokens = [t for t in tokens if t not in ENGLISH_STOP_WORDS and len(t) > 1]
    lemmas = [lemmatize(t) for t in content_tokens]

    sections = segment_sections(text)
    detected = [s for s in sections if s != "Header"]
    missing_sections = [s for s in RECOMMENDED_SECTIONS if s not in sections]

    technical, soft = link_skills(text)
    # Evidence: which sections mention each skill.
    evidence = {}
    for skill in technical + soft:
        pat = _C_LANGUAGE if skill == "c" else _VOCAB_PATTERNS.get(skill)
        alias_pats = [_ALIAS_PATTERNS[a] for a, c in SKILL_ALIASES.items() if c == skill]
        where = [name for name, body in sections.items()
                 if (pat and pat.search(body.lower())) or any(p.search(body.lower()) for p in alias_pats)]
        evidence[skill] = where
    categorized = OrderedDict()
    for cat, members in SKILL_CATEGORIES.items():
        hits = [s for s in technical if s in members]
        if hits:
            categorized[cat] = hits
    other = [s for s in technical if not any(s in m for m in SKILL_CATEGORIES.values())]
    if other:
        categorized["Other"] = other

    entities = extract_entities(text)
    sample = [t for t in tokenize(strip_contact("\n".join(v for k, v in sections.items() if k != "Header")))
              if t not in ENGLISH_STOP_WORDS and len(t) > 1][:12]
    impact_text = "\n".join(v for k, v in sections.items() if k in ("Projects", "Experience", "Achievements")) or body
    quality = writing_quality(body, sentences(strip_contact(impact_text)), tokens)
    no_header = "\n".join(v for k, v in sections.items() if k != "Header") or body
    keywords, role_sims = tfidf_keywords_and_similarity(strip_contact(no_header), industry_skills)

    target = None
    if target_role and target_role in industry_skills:
        required = [s.lower() for s in industry_skills[target_role]["technical_skills"]]
        target = {
            "role": target_role,
            "matched": [s for s in required if s in technical],
            "missing": [s for s in required if s not in technical],
            "similarity": next((r["similarity"] for r in role_sims if r["role"] == target_role), 0.0),
        }

    # ---- Suggestions, most important first ----
    tips: List[str] = []
    if missing_sections:
        tips.append(f"Add clearly titled section(s): {', '.join(missing_sections)}.")
    if not entities["EMAIL"] or not entities["PHONE"]:
        tips.append("Include both a professional email address and a phone number at the top.")
    if not any("linkedin" in l.lower() for l in entities["LINK"]):
        tips.append("Add your LinkedIn profile URL.")
    if not any("github" in l.lower() for l in entities["LINK"]):
        tips.append("Add a GitHub link so recruiters can see your code.")
    if quality["action_verb_count"] < 5:
        tips.append("Start bullet points with strong action verbs (developed, built, optimised, led).")
    if quality["quantified_achievements"] < 2:
        tips.append("Quantify impact with numbers, e.g. 'reduced load time by 30%' or 'used by 200+ students'.")
    if quality["weak_phrases"]:
        tips.append(f"Replace weak phrases such as '{quality['weak_phrases'][0]}' with specific achievements.")
    if quality["first_person_count"] > 3:
        tips.append("Avoid first-person pronouns (I, my); write bullets in an implied first person.")
    if target and target["missing"]:
        tips.append(f"For {target['role']}, add evidence of: {', '.join(target['missing'][:4])}.")
    if len(tokens) < 200:
        tips.append("Your resume is short; expand project and experience descriptions (aim for 350-700 words).")
    elif len(tokens) > 900:
        tips.append("Your resume is long; trim to the most relevant 1-2 pages.")

    return {
        "preprocessing": {
            "characters": len(text),
            "sentences": len(sents),
            "tokens": len(tokens),
            "content_tokens": len(content_tokens),
            "stopwords_removed": len(tokens) - len(content_tokens),
            "unique_lemmas": len(set(lemmas)),
            "lexical_diversity": round(len(set(lemmas)) / len(lemmas), 2) if lemmas else 0.0,
            "sample_tokens": sample,
            "sample_lemmas": [lemmatize(t) for t in sample],
        },
        "sections": {
            "detected": detected,
            "missing": missing_sections,
            "word_counts": {k: len(v.split()) for k, v in sections.items() if k != "Header"},
        },
        "entities": entities,
        "skills": {
            "technical": technical,
            "soft": soft,
            "categorized": categorized,
            "evidence": evidence,
        },
        "keywords": keywords,
        "writing": quality,
        "role_similarity": role_sims,
        "target": target,
        "suggestions": tips[:8],
    }

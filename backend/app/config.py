from typing import Dict

# ─── Score Weights ───────────────────────────────────────────────────────────
# These weights must sum to 1.0
SCORE_WEIGHTS: Dict[str, float] = {
    "keyword_match": 0.20,
    "skills_match": 0.25,
    "semantic_match": 0.20,
    "experience_match": 0.10,
    "education_match": 0.05,
    "section_completeness": 0.05,
    "ats_parsing_safety": 0.10,
    "resume_quality": 0.05,
}

# ─── Semantic Model ───────────────────────────────────────────────────────────
SEMANTIC_MODEL_NAME = "all-MiniLM-L6-v2"
SEMANTIC_THRESHOLD = 0.60       # cosine similarity minimum for a semantic match
SEMANTIC_TOP_K = 3              # top-k resume sentences to retrieve per requirement

# ─── Fuzzy Matching ───────────────────────────────────────────────────────────
FUZZY_THRESHOLD = 78            # RapidFuzz token_sort_ratio threshold (0–100)

# ─── File Upload ──────────────────────────────────────────────────────────────
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

# ─── Database ─────────────────────────────────────────────────────────────────
DATABASE_URL = "sqlite+aiosqlite:///./ats_checker.db"

# ─── Logging ──────────────────────────────────────────────────────────────────
# Never log PII fields
REDACTED_FIELDS = {"email", "phone", "name", "text", "raw_text", "content"}

# ─── Section Completeness ─────────────────────────────────────────────────────
EXPECTED_SECTIONS = [
    "contact",
    "summary",
    "skills",
    "experience",
    "education",
    "projects",
]
OPTIONAL_SECTIONS = [
    "certifications",
    "achievements",
    "publications",
    "languages",
    "volunteer",
    "awards",
]

# ─── Quality Analysis ─────────────────────────────────────────────────────────
ACTION_VERBS = {
    "developed", "built", "designed", "implemented", "created", "engineered",
    "architected", "deployed", "optimized", "improved", "increased", "reduced",
    "led", "managed", "mentored", "coached", "collaborated", "coordinated",
    "delivered", "shipped", "launched", "released", "migrated", "refactored",
    "automated", "integrated", "configured", "maintained", "monitored",
    "analyzed", "researched", "investigated", "evaluated", "assessed",
    "established", "introduced", "pioneered", "initiated", "spearheaded",
    "streamlined", "enhanced", "accelerated", "boosted", "grew", "scaled",
    "transformed", "revamped", "modernized", "consolidated", "standardized",
    "documented", "trained", "presented", "negotiated", "secured", "generated",
    "resolved", "diagnosed", "debugged", "fixed", "solved", "addressed",
    "contributed", "supported", "assisted", "participated", "performed",
    "wrote", "authored", "published", "tested", "validated", "verified",
}

WEAK_PHRASES = [
    "worked on",
    "helped with",
    "was responsible for",
    "responsible for",
    "assisted with",
    "involved in",
    "participated in",
    "contributed to",
    "team player",
    "hard worker",
    "go getter",
    "results driven",
    "detail oriented",
    "fast learner",
    "quick learner",
    "self motivated",
    "proactive",
    "dynamic",
    "synergy",
    "leverage",
    "utilize",
    "liaise",
]

# ─── Parsing Safety Penalties ─────────────────────────────────────────────────
# Severity weights for ATS parsing penalty
SEVERITY_PENALTIES = {
    "critical": 0.25,
    "high": 0.15,
    "medium": 0.08,
    "low": 0.03,
}

# ─── Education Keywords ───────────────────────────────────────────────────────
DEGREE_KEYWORDS = {
    "phd": 5,
    "ph.d": 5,
    "doctorate": 5,
    "doctoral": 5,
    "master": 4,
    "masters": 4,
    "m.s": 4,
    "m.sc": 4,
    "msc": 4,
    "mba": 4,
    "m.eng": 4,
    "bachelor": 3,
    "bachelors": 3,
    "b.s": 3,
    "b.sc": 3,
    "bsc": 3,
    "b.e": 3,
    "b.tech": 3,
    "btech": 3,
    "b.a": 3,
    "undergraduate": 3,
    "associate": 2,
    "diploma": 2,
    "certificate": 1,
    "high school": 0,
    "ged": 0,
}

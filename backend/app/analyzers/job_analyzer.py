"""
Job Description Analyzer.
Extracts required skills, preferred skills, tools, experience/education requirements,
responsibilities, and keyword frequency from a job description.
"""
import re
from collections import Counter
from typing import Dict, List, Set, Tuple

from app.models.schemas import JobAnalysisResponse, JobRequirement
from app.analyzers.skill_extractor import extract_skills, get_skill_category, normalize_skill_name
from app.utils.text_utils import normalize_skill, split_into_sentences, extract_years_of_experience

# ─── Signals for required vs preferred ───────────────────────────────────────
REQUIRED_SIGNALS = [
    "required", "must have", "must-have", "essential", "necessary",
    "minimum requirement", "you must", "we require", "mandatory",
    "you need", "you will need", "you should have",
    "requirements:", "required skills", "required qualifications",
]
PREFERRED_SIGNALS = [
    "preferred", "nice to have", "nice-to-have", "bonus", "plus",
    "desired", "ideal", "advantageous", "would be great", "beneficial",
    "not required but", "optional", "a plus", "an asset", "preferred skills",
    "good to have",
]

# ─── Experience-related patterns ──────────────────────────────────────────────
EXP_PATTERNS = [
    r"\d+\+?\s+years?\s+of\s+(?:professional\s+)?experience",
    r"\d+\+?\s+years?\s+experience",
    r"\d+\+?\s+yr[s]?\s+(?:of\s+)?experience",
    r"entry[\s\-]?level",
    r"junior\s+level",
    r"mid[\s\-]?level",
    r"senior\s+level",
    r"lead\s+engineer",
    r"manager",
    r"director",
]

# ─── Education keywords ────────────────────────────────────────────────────────
EDU_KEYWORDS = [
    "bachelor", "master", "phd", "ph.d", "doctoral", "degree", "b.s", "m.s",
    "b.e", "b.tech", "m.tech", "mba", "associate", "diploma",
    "computer science", "engineering", "information technology", "mathematics",
    "statistics", "data science",
]

# ─── Soft skill keywords ───────────────────────────────────────────────────────
SOFT_SKILL_KEYWORDS = [
    "communication", "leadership", "teamwork", "collaboration", "problem solving",
    "problem-solving", "critical thinking", "time management", "adaptability",
    "creativity", "attention to detail", "organizational", "interpersonal",
    "presentation", "analytical", "decision making", "mentoring", "initiative",
    "self-motivated", "detail-oriented", "fast learner", "proactive",
]


def analyze_job_description(jd_text: str) -> JobAnalysisResponse:
    """
    Full analysis of a job description.
    """
    sentences = split_into_sentences(jd_text)
    jd_lower = jd_text.lower()
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9\.\+\#\-]{1,}\b", jd_text)
    word_count = len(words)

    # ── Skill extraction ──────────────────────────────────────────────────────
    skills, _ = extract_skills(jd_text)
    all_skill_names = [s.name for s in skills]

    # ── Determine required vs preferred skills ────────────────────────────────
    required_skills: List[str] = []
    preferred_skills: List[str] = []

    # Split JD into required / preferred sections heuristically
    required_section, preferred_section = _split_required_preferred(jd_text)

    req_skills, _ = extract_skills(required_section)
    pref_skills, _ = extract_skills(preferred_section)

    required_set = {s.name for s in req_skills}
    preferred_set = {s.name for s in pref_skills} - required_set

    required_skills = list(required_set)
    preferred_skills = list(preferred_set)

    # Skills that appear in neither section but are in the JD
    other_skills = [s for s in all_skill_names if s not in required_set and s not in preferred_set]
    # If no clear separation, treat all as required
    if not required_skills and not preferred_skills:
        required_skills = all_skill_names

    # ── Tools ─────────────────────────────────────────────────────────────────
    tool_skills = [s for s in skills if get_skill_category(s.name) == "Tools"]
    tools = list({s.name for s in tool_skills})

    # ── Soft skills ───────────────────────────────────────────────────────────
    soft_skills = _extract_soft_skills(jd_lower)

    # ── Education requirements ────────────────────────────────────────────────
    education_requirements = _extract_education(jd_text)

    # ── Experience requirements ───────────────────────────────────────────────
    experience_requirements = _extract_experience(jd_text)

    # ── Responsibilities ──────────────────────────────────────────────────────
    responsibilities = _extract_responsibilities(sentences)

    # ── Keyword frequency ─────────────────────────────────────────────────────
    keywords = _build_keyword_frequency(jd_text, skills)

    # ── Build requirement objects ──────────────────────────────────────────────
    all_requirements: List[JobRequirement] = []

    for skill_name in required_skills:
        freq = sum(1 for w in jd_lower.split() if normalize_skill(w) == normalize_skill(skill_name))
        all_requirements.append(JobRequirement(
            text=skill_name,
            category="required",
            importance="critical" if freq >= 3 else "high" if freq >= 2 else "medium",
            frequency=max(1, freq),
        ))

    for skill_name in preferred_skills:
        freq = sum(1 for w in jd_lower.split() if normalize_skill(w) == normalize_skill(skill_name))
        all_requirements.append(JobRequirement(
            text=skill_name,
            category="preferred",
            importance="medium",
            frequency=max(1, freq),
        ))

    for exp in experience_requirements:
        all_requirements.append(JobRequirement(
            text=exp,
            category="experience",
            importance="high",
            frequency=1,
        ))

    for edu in education_requirements:
        all_requirements.append(JobRequirement(
            text=edu,
            category="education",
            importance="medium",
            frequency=1,
        ))

    return JobAnalysisResponse(
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        tools=tools,
        soft_skills=soft_skills,
        education_requirements=education_requirements,
        experience_requirements=experience_requirements,
        responsibilities=responsibilities[:10],
        keywords=dict(list(keywords.most_common(40))),
        all_requirements=all_requirements,
        word_count=word_count,
    )


def _split_required_preferred(jd_text: str) -> Tuple[str, str]:
    """
    Heuristically split JD into required and preferred sections.
    Returns (required_text, preferred_text).
    """
    lower = jd_text.lower()

    # Try to find explicit section boundaries
    preferred_idx = -1
    for signal in ["preferred qualifications", "preferred skills", "nice to have",
                   "bonus", "good to have", "desired qualifications"]:
        idx = lower.find(signal)
        if idx > 0:
            preferred_idx = idx
            break

    if preferred_idx > 0:
        return jd_text[:preferred_idx], jd_text[preferred_idx:]

    # Check if document contains required signals
    required_idx = -1
    for signal in ["required qualifications", "required skills", "requirements",
                   "minimum qualifications", "you must have"]:
        idx = lower.find(signal)
        if idx >= 0:
            required_idx = idx
            break

    if required_idx >= 0:
        return jd_text[required_idx:], ""

    # No clear separation — treat entire JD as required
    return jd_text, ""


def _extract_soft_skills(jd_lower: str) -> List[str]:
    found = []
    for skill in SOFT_SKILL_KEYWORDS:
        if skill in jd_lower:
            found.append(skill.replace("-", " ").title())
    return list(dict.fromkeys(found))  # deduplicate, preserve order


def _extract_education(jd_text: str) -> List[str]:
    found = []
    text_lower = jd_text.lower()
    for keyword in EDU_KEYWORDS:
        if keyword in text_lower:
            # Find surrounding context
            idx = text_lower.find(keyword)
            ctx = jd_text[max(0, idx - 10):idx + len(keyword) + 30].strip()
            if ctx not in found:
                found.append(ctx)
    return found[:5]


def _extract_experience(jd_text: str) -> List[str]:
    found = []
    for pattern in EXP_PATTERNS:
        matches = re.findall(pattern, jd_text, re.IGNORECASE)
        for m in matches:
            if m.strip() not in found:
                found.append(m.strip())
    return found[:5]


def _extract_responsibilities(sentences: List[str]) -> List[str]:
    """Extract responsibility-like sentences (action verb at start, meaningful length)."""
    action_verbs = {
        "develop", "build", "design", "implement", "create", "maintain", "write",
        "work", "collaborate", "lead", "manage", "architect", "deploy", "optimize",
        "analyze", "research", "test", "deliver", "drive", "own", "support",
        "integrate", "improve", "ensure", "review", "provide", "contribute",
        "participate", "coordinate", "establish", "monitor", "define", "plan",
    }
    responsibilities = []
    for sent in sentences:
        words = sent.strip().split()
        if not words:
            continue
        first_word = words[0].lower().rstrip(".,:")
        if first_word in action_verbs and 8 <= len(words) <= 40:
            responsibilities.append(sent.strip())
    return responsibilities


def _build_keyword_frequency(jd_text: str, skills: list) -> Counter:
    """Build keyword frequency map from meaningful JD terms."""
    # Include all skill names
    freq: Counter = Counter()
    for skill in skills:
        freq[skill.name] += skill.frequency

    # Add other technical terms
    tech_pattern = r"\b[A-Z][a-zA-Z0-9\.\+\#]{1,}\b"
    tech_terms = re.findall(tech_pattern, jd_text)
    stop_words = {
        "The", "We", "You", "Our", "Your", "This", "That", "With", "For",
        "And", "Or", "But", "In", "On", "At", "To", "Of", "A", "An",
        "Is", "Are", "Was", "Were", "Will", "Be", "Been", "Being",
        "Have", "Has", "Had", "Do", "Does", "Did", "Not", "From",
        "By", "As", "If", "So", "Up", "Us", "About", "Who",
    }
    for term in tech_terms:
        if term not in stop_words and len(term) > 2:
            freq[term] += 1

    return freq

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# Enums / Literals
# ─────────────────────────────────────────────────────────────────────────────

class MatchType:
    EXACT = "exact"
    NORMALIZED = "normalized"
    FUZZY = "fuzzy"
    SEMANTIC = "semantic"
    WEAK = "weak"
    MISSING = "missing"


class Confidence:
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class Severity:
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ─────────────────────────────────────────────────────────────────────────────
# Upload & Parse
# ─────────────────────────────────────────────────────────────────────────────

class ParsingIssue(BaseModel):
    severity: str
    category: str
    message: str
    recommendation: str


class ResumeUploadResponse(BaseModel):
    resume_id: str
    filename: str
    file_size_kb: float
    file_type: str
    page_count: Optional[int] = None
    text_length: int
    word_count: int
    parsing_status: str                  # "success" | "partial" | "failed"
    parsing_issues: List[ParsingIssue] = Field(default_factory=list)
    ats_safety_score: float              # 0.0 – 1.0
    message: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# Resume Sections & Structure
# ─────────────────────────────────────────────────────────────────────────────

class SectionStatus(BaseModel):
    name: str
    detected: bool
    heading_found: Optional[str] = None
    text_preview: Optional[str] = None
    word_count: int = 0
    issues: List[str] = Field(default_factory=list)


class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    location: Optional[str] = None


class ResumeSection(BaseModel):
    name: str
    raw_text: str
    bullets: List[str] = Field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Skills
# ─────────────────────────────────────────────────────────────────────────────

class ExtractedSkill(BaseModel):
    name: str
    normalized_name: str
    category: str
    frequency: int = 1
    context: Optional[str] = None       # brief excerpt where skill was found


class SkillCategory(BaseModel):
    category: str
    skills: List[str]
    count: int


# ─────────────────────────────────────────────────────────────────────────────
# Job Description Analysis
# ─────────────────────────────────────────────────────────────────────────────

class JobAnalysisRequest(BaseModel):
    jd_text: str = Field(..., min_length=50)


class JobRequirement(BaseModel):
    text: str
    category: str                       # "required" | "preferred" | "tool" | "soft" | "education" | "experience"
    importance: str                     # "critical" | "high" | "medium" | "low"
    frequency: int = 1                  # times mentioned in JD


class JobAnalysisResponse(BaseModel):
    required_skills: List[str]
    preferred_skills: List[str]
    tools: List[str]
    soft_skills: List[str]
    education_requirements: List[str]
    experience_requirements: List[str]
    responsibilities: List[str]
    keywords: Dict[str, int]            # keyword -> frequency map
    all_requirements: List[JobRequirement]
    word_count: int


# ─────────────────────────────────────────────────────────────────────────────
# Matching
# ─────────────────────────────────────────────────────────────────────────────

class MatchedRequirement(BaseModel):
    requirement: str
    category: str
    importance: str
    match_type: str                     # MatchType.*
    confidence: str                     # Confidence.*
    score: float                        # 0.0 – 1.0
    evidence_text: Optional[str] = None
    evidence_snippet: Optional[str] = None
    fuzzy_score: Optional[float] = None
    semantic_score: Optional[float] = None


class MissingSkill(BaseModel):
    skill: str
    category: str
    importance: str
    jd_frequency: int
    related_evidence: Optional[str] = None
    related_evidence_text: Optional[str] = None
    suggestion: str


class WeakMatch(BaseModel):
    requirement: str
    resume_evidence: str
    explanation: str
    recommendation: str


# ─────────────────────────────────────────────────────────────────────────────
# Quality Analysis
# ─────────────────────────────────────────────────────────────────────────────

class QualityIssue(BaseModel):
    issue_type: str
    severity: str
    affected_text: str
    suggestion: str


class QualityMetrics(BaseModel):
    action_verb_score: float            # 0.0 – 1.0
    quantification_score: float         # 0.0 – 1.0
    weak_phrase_count: int
    first_person_count: int
    average_bullet_length: float
    total_bullets: int
    bullets_with_metrics: int
    repeated_phrases: List[str]
    quality_issues: List[QualityIssue]
    overall_quality_score: float        # 0.0 – 1.0


# ─────────────────────────────────────────────────────────────────────────────
# Score Breakdown
# ─────────────────────────────────────────────────────────────────────────────

class ScoreBreakdown(BaseModel):
    overall_score: float                # 0 – 100
    keyword_match: float                # 0.0 – 1.0
    skills_match: float
    semantic_match: float
    experience_match: float
    education_match: float
    section_completeness: float
    ats_parsing_safety: float
    resume_quality: float
    score_explanation: str
    semantic_model_used: bool


# ─────────────────────────────────────────────────────────────────────────────
# Full Analysis Request / Response
# ─────────────────────────────────────────────────────────────────────────────

class AnalysisRequest(BaseModel):
    resume_id: str
    jd_text: str = Field(..., min_length=50)


class AnalysisResponse(BaseModel):
    analysis_id: str
    resume_id: str
    created_at: str

    # Score
    score: ScoreBreakdown

    # Resume data
    contact_info: ContactInfo
    sections: List[SectionStatus]
    resume_skills: List[ExtractedSkill]
    skill_categories: List[SkillCategory]

    # JD data
    job_analysis: JobAnalysisResponse

    # Matching
    matched_requirements: List[MatchedRequirement]
    missing_skills: List[MissingSkill]
    weak_matches: List[WeakMatch]

    # Quality
    quality_metrics: QualityMetrics
    parsing_issues: List[ParsingIssue]

    # Recommendations
    recommendations: List[str]
    strengths: List[str]
    weaknesses: List[str]

    # Meta
    semantic_model_available: bool
    processing_time_ms: float


class SavedAnalysis(BaseModel):
    analysis_id: str
    filename: str
    created_at: str
    overall_score: float
    job_title_hint: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    semantic_model_loaded: bool
    semantic_model_name: str
    version: str = "1.0.0"

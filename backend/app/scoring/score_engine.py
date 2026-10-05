"""
Score Engine: calculates the weighted ATS compatibility score.
"""
from typing import List, Optional

from app.config import SCORE_WEIGHTS, DEGREE_KEYWORDS, EXPECTED_SECTIONS
from app.models.schemas import (
    MatchedRequirement, MatchType, QualityMetrics, ScoreBreakdown,
    SectionStatus
)
from app.utils.text_utils import extract_years_of_experience


def calculate_score(
    matched_requirements: List[MatchedRequirement],
    all_requirements: List[dict],
    resume_skills: List[str],
    required_skills: List[str],
    resume_text: str,
    sections: List[SectionStatus],
    quality_metrics: QualityMetrics,
    ats_safety_score: float,
    experience_requirements: List[str],
    education_requirements: List[str],
    avg_semantic_score: float = 0.0,
    semantic_model_used: bool = False,
) -> ScoreBreakdown:
    """
    Compute all score components and the final weighted ATS score.
    """
    total_requirements = len(all_requirements)

    # ── 1. Keyword Match Score ────────────────────────────────────────────────
    exact_and_normalized = [
        r for r in matched_requirements
        if r.match_type in (MatchType.EXACT, MatchType.NORMALIZED)
    ]
    keyword_match = len(exact_and_normalized) / max(total_requirements, 1)

    # ── 2. Skills Match Score ─────────────────────────────────────────────────
    resume_skill_set = {s.lower() for s in resume_skills}
    required_skill_set = {s.lower() for s in required_skills}

    # Also count fuzzy/semantic matched required skills
    matched_req_skills = {
        r.requirement.lower() for r in matched_requirements
        if r.match_type != MatchType.MISSING
    }

    matched_required = required_skill_set & (resume_skill_set | matched_req_skills)
    skills_match = len(matched_required) / max(len(required_skill_set), 1)

    # ── 3. Semantic Match Score ───────────────────────────────────────────────
    if semantic_model_used and avg_semantic_score > 0:
        semantic_match = min(avg_semantic_score + 0.3, 1.0)  # boost base score
    elif semantic_model_used:
        # Count semantic matches
        semantic_matched = [r for r in matched_requirements if r.match_type == MatchType.SEMANTIC]
        semantic_match = len(semantic_matched) / max(total_requirements, 1)
        # Blend with avg score
        if semantic_matched:
            avg_sem = sum(r.semantic_score or 0 for r in semantic_matched) / len(semantic_matched)
            semantic_match = (semantic_match * 0.5 + avg_sem * 0.5)
    else:
        # No semantic model: use fuzzy match quality as proxy
        fuzzy_matched = [r for r in matched_requirements if r.match_type == MatchType.FUZZY]
        if fuzzy_matched:
            avg_fuzzy = sum((r.fuzzy_score or 0) / 100 for r in fuzzy_matched) / len(fuzzy_matched)
            semantic_match = avg_fuzzy * (len(fuzzy_matched) / max(total_requirements, 1))
        else:
            semantic_match = keyword_match * 0.7  # rough proxy

    semantic_match = min(semantic_match, 1.0)

    # ── 4. Experience Match Score ─────────────────────────────────────────────
    experience_match = _score_experience(experience_requirements, resume_text)

    # ── 5. Education Match Score ──────────────────────────────────────────────
    education_match = _score_education(education_requirements, resume_text)

    # ── 6. Section Completeness Score ────────────────────────────────────────
    detected_count = sum(1 for s in sections if s.detected and s.name in EXPECTED_SECTIONS)
    section_completeness = detected_count / len(EXPECTED_SECTIONS)

    # ── 7. ATS Parsing Safety ─────────────────────────────────────────────────
    # Already computed in parser; use as-is
    ats_parsing_safety = ats_safety_score

    # ── 8. Resume Quality ─────────────────────────────────────────────────────
    resume_quality = quality_metrics.overall_quality_score

    # ── Weighted Final Score ──────────────────────────────────────────────────
    w = SCORE_WEIGHTS
    overall = (
        keyword_match * w["keyword_match"]
        + skills_match * w["skills_match"]
        + semantic_match * w["semantic_match"]
        + experience_match * w["experience_match"]
        + education_match * w["education_match"]
        + section_completeness * w["section_completeness"]
        + ats_parsing_safety * w["ats_parsing_safety"]
        + resume_quality * w["resume_quality"]
    ) * 100

    overall = round(min(max(overall, 0), 100), 1)

    # ── Explanation ───────────────────────────────────────────────────────────
    explanation = _build_explanation(
        overall, matched_requirements, all_requirements,
        missing_count=total_requirements - len([r for r in matched_requirements if r.match_type != MatchType.MISSING]),
        section_completeness=section_completeness,
        quality_score=resume_quality,
        ats_safety=ats_parsing_safety,
    )

    return ScoreBreakdown(
        overall_score=overall,
        keyword_match=round(keyword_match, 3),
        skills_match=round(skills_match, 3),
        semantic_match=round(semantic_match, 3),
        experience_match=round(experience_match, 3),
        education_match=round(education_match, 3),
        section_completeness=round(section_completeness, 3),
        ats_parsing_safety=round(ats_parsing_safety, 3),
        resume_quality=round(resume_quality, 3),
        score_explanation=explanation,
        semantic_model_used=semantic_model_used,
    )


def _score_experience(experience_requirements: List[str], resume_text: str) -> float:
    """Score experience match: compare required years to years found in resume."""
    if not experience_requirements:
        return 0.85  # No experience requirement stated → neutral score

    resume_years = extract_years_of_experience(resume_text)

    # Extract required years from experience requirements
    import re
    required_years = 0.0
    for req in experience_requirements:
        nums = re.findall(r"(\d+)", req)
        if nums:
            required_years = max(required_years, float(nums[0]))

    # Check for entry-level / junior signals
    text_lower = " ".join(experience_requirements).lower()
    if any(w in text_lower for w in ["entry", "junior", "0-1", "0 to 1", "fresh"]):
        return 1.0
    if any(w in text_lower for w in ["intern", "trainee"]):
        return 1.0

    if required_years == 0:
        return 0.85

    if resume_years == 0:
        # Can't determine resume experience from text — give partial credit
        return 0.60

    if resume_years >= required_years:
        return 1.0
    else:
        return min(resume_years / required_years, 1.0)


def _score_education(education_requirements: List[str], resume_text: str) -> float:
    """Score education match."""
    if not education_requirements:
        return 0.85  # No education requirement stated

    resume_lower = resume_text.lower()
    edu_text = " ".join(education_requirements).lower()

    # Find required degree level
    required_level = 0
    for keyword, level in DEGREE_KEYWORDS.items():
        if keyword in edu_text:
            required_level = max(required_level, level)

    # Find resume degree level
    resume_level = 0
    for keyword, level in DEGREE_KEYWORDS.items():
        if keyword in resume_lower:
            resume_level = max(resume_level, level)

    if resume_level == 0:
        return 0.50  # Can't detect education in resume
    if resume_level >= required_level:
        return 1.0
    else:
        return 0.60  # Has some education but below required level


def _build_explanation(
    score: float,
    matched: List[MatchedRequirement],
    all_reqs: List[dict],
    missing_count: int,
    section_completeness: float,
    quality_score: float,
    ats_safety: float,
) -> str:
    """Generate a human-readable score explanation."""
    matched_count = len([r for r in matched if r.match_type not in (MatchType.MISSING,)])
    total = len(all_reqs)

    parts = []

    if score >= 85:
        parts.append(f"Excellent match! Your resume aligns well with the job requirements.")
    elif score >= 70:
        parts.append(f"Good match with room for improvement.")
    elif score >= 55:
        parts.append(f"Moderate match — several key requirements are missing.")
    else:
        parts.append(f"Low match — significant gaps between your resume and the job requirements.")

    parts.append(
        f"You match {matched_count} of {total} identified requirements."
    )

    if missing_count > 0:
        missing_names = [r["text"] for r in all_reqs
                         if not any(m.requirement == r["text"] and m.match_type != MatchType.MISSING
                                    for m in matched)][:4]
        if missing_names:
            parts.append(f"Key missing items include: {', '.join(missing_names[:4])}.")

    if section_completeness < 0.7:
        parts.append("Several standard resume sections were not detected.")

    if quality_score < 0.5:
        parts.append("Resume quality could be improved with stronger action verbs and measurable achievements.")

    if ats_safety < 0.8:
        parts.append("Potential ATS parsing issues detected — review the Parsing Analysis section.")

    return " ".join(parts)

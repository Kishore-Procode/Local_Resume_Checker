"""
Analysis Service: orchestrates the full resume analysis pipeline.
"""
import time
import uuid
from datetime import datetime
from typing import List, Optional

from app.analyzers.job_analyzer import analyze_job_description
from app.analyzers.quality_analyzer import analyze_quality
from app.analyzers.section_detector import detect_sections, extract_contact_info
from app.analyzers.skill_extractor import extract_skills
from app.matching.evidence_matcher import build_missing_skills, build_weak_matches
from app.matching.fuzzy_matcher import batch_fuzzy_match
from app.matching.keyword_matcher import batch_keyword_match
from app.matching.semantic_matcher import (
    compute_semantic_matches,
    compute_overall_semantic_score,
    get_resume_sentences,
)
from app.models.schemas import (
    AnalysisResponse, ContactInfo, MatchedRequirement, MatchType
)
from app.scoring.score_engine import calculate_score


def run_analysis(
    resume_id: str,
    raw_text: str,
    jd_text: str,
    parsing_issues: list,
    ats_safety_score: float,
    filename: str,
    semantic_model,
) -> AnalysisResponse:
    """
    Full analysis pipeline:
    1. Parse resume sections
    2. Extract skills
    3. Analyze JD
    4. Keyword match
    5. Fuzzy match
    6. Semantic match
    7. Build evidence / missing / weak
    8. Score
    9. Quality
    10. Recommendations
    """
    start_time = time.time()
    analysis_id = str(uuid.uuid4())

    # ── Step 1: Detect resume sections ────────────────────────────────────────
    sections_text, section_statuses = detect_sections(raw_text)

    # ── Step 2: Extract contact info ──────────────────────────────────────────
    contact_raw = extract_contact_info(raw_text)
    contact_info = ContactInfo(**contact_raw)

    # ── Step 3: Extract resume skills ─────────────────────────────────────────
    resume_skills, skill_categories = extract_skills(raw_text)
    resume_skill_names = [s.name for s in resume_skills]

    # ── Step 4: Analyze JD ────────────────────────────────────────────────────
    job_analysis = analyze_job_description(jd_text)

    # ── Step 5: Keyword matching ──────────────────────────────────────────────
    all_req_dicts = [
        {"text": r.text, "category": r.category, "importance": r.importance}
        for r in job_analysis.all_requirements
    ]

    kw_matched, kw_unmatched = batch_keyword_match(all_req_dicts, raw_text)

    # ── Step 6: Fuzzy matching ────────────────────────────────────────────────
    fuzzy_matched, still_unmatched = batch_fuzzy_match(kw_unmatched, raw_text)

    # ── Step 7: Semantic matching ──────────────────────────────────────────────
    semantic_model_available = semantic_model is not None
    avg_semantic_score = 0.0

    if semantic_model_available and still_unmatched:
        resume_sentences = get_resume_sentences(raw_text)
        sem_matched, final_unmatched, avg_semantic_score = compute_semantic_matches(
            still_unmatched, resume_sentences, semantic_model
        )
    else:
        sem_matched = []
        final_unmatched = still_unmatched

    # ── Step 8: Consolidate all matches ───────────────────────────────────────
    all_matched: List[MatchedRequirement] = kw_matched + fuzzy_matched + sem_matched

    # Separate weak matches from true missing
    weak_reqs = [r for r in final_unmatched if r.match_type == MatchType.WEAK]
    truly_missing = [r for r in final_unmatched if r.match_type == MatchType.MISSING]

    # Add weak to all_matched (for table display) but flag them
    all_results = all_matched + weak_reqs + truly_missing

    # ── Step 9: Build missing skills & weak matches ───────────────────────────
    missing_skills = build_missing_skills(
        truly_missing, raw_text, job_analysis.keywords
    )
    weak_matches = build_weak_matches(weak_reqs)

    # ── Step 10: Quality analysis ──────────────────────────────────────────────
    quality_metrics = analyze_quality(sections_text, raw_text)

    # ── Step 11: Score ────────────────────────────────────────────────────────
    score = calculate_score(
        matched_requirements=all_results,
        all_requirements=all_req_dicts,
        resume_skills=resume_skill_names,
        required_skills=job_analysis.required_skills,
        resume_text=raw_text,
        sections=section_statuses,
        quality_metrics=quality_metrics,
        ats_safety_score=ats_safety_score,
        experience_requirements=job_analysis.experience_requirements,
        education_requirements=job_analysis.education_requirements,
        avg_semantic_score=avg_semantic_score,
        semantic_model_used=semantic_model_available,
    )

    # ── Step 12: Recommendations & Strengths/Weaknesses ───────────────────────
    recommendations = _generate_recommendations(
        missing_skills=missing_skills,
        quality_metrics=quality_metrics,
        section_statuses=section_statuses,
        score=score,
        weak_matches=weak_matches,
    )
    strengths, weaknesses = _identify_strengths_weaknesses(
        score=score,
        matched_requirements=all_matched,
        missing_skills=missing_skills,
        quality_metrics=quality_metrics,
        section_statuses=section_statuses,
    )

    elapsed_ms = (time.time() - start_time) * 1000

    return AnalysisResponse(
        analysis_id=analysis_id,
        resume_id=resume_id,
        created_at=datetime.utcnow().isoformat(),
        score=score,
        contact_info=contact_info,
        sections=section_statuses,
        resume_skills=resume_skills,
        skill_categories=skill_categories,
        job_analysis=job_analysis,
        matched_requirements=all_results,
        missing_skills=missing_skills,
        weak_matches=weak_matches,
        quality_metrics=quality_metrics,
        parsing_issues=parsing_issues,
        recommendations=recommendations,
        strengths=strengths,
        weaknesses=weaknesses,
        semantic_model_available=semantic_model_available,
        processing_time_ms=round(elapsed_ms, 1),
    )


def _generate_recommendations(
    missing_skills, quality_metrics, section_statuses, score, weak_matches
) -> List[str]:
    recs = []

    # Missing critical skills
    critical_missing = [m for m in missing_skills if m.importance in ("critical", "high")]
    if critical_missing:
        skills_str = ", ".join(m.skill for m in critical_missing[:3])
        recs.append(
            f"If you have experience with {skills_str}, explicitly mention these in your resume — "
            f"they are important requirements for this role."
        )

    # Quantification
    if quality_metrics.quantification_score < 0.4:
        recs.append(
            f"Add measurable achievements to your experience bullets. Only "
            f"{quality_metrics.bullets_with_metrics} of {quality_metrics.total_bullets} "
            f"bullets currently contain numbers or metrics."
        )

    # Action verbs
    if quality_metrics.action_verb_score < 0.6:
        recs.append(
            "Start more bullet points with strong action verbs such as 'Developed', 'Built', "
            "'Optimized', or 'Led' to make your experience more impactful."
        )

    # Missing sections
    missing_sections = [s for s in section_statuses if not s.detected and s.name in
                        ["summary", "skills", "projects", "certifications"]]
    for sec in missing_sections[:2]:
        recs.append(
            f"Consider adding a '{sec.name.title()}' section. Many ATS systems look for this section explicitly."
        )

    # Weak matches
    if weak_matches:
        req_names = ", ".join(w.requirement for w in weak_matches[:2])
        recs.append(
            f"Your resume has related experience for: {req_names} — but the exact terms aren't present. "
            f"Consider using standard industry terminology."
        )

    # ATS safety
    if score.ats_parsing_safety < 0.8:
        recs.append(
            "Address the ATS parsing issues flagged in the Parsing Analysis section to improve "
            "how ATS systems read your resume."
        )

    # Weak phrases
    if quality_metrics.weak_phrase_count > 2:
        recs.append(
            f"Replace {quality_metrics.weak_phrase_count} weak phrases "
            f"(e.g., 'worked on', 'was responsible for') with specific action verbs and outcomes."
        )

    if not recs:
        recs.append("Your resume is well-optimized for this role. Continue tailoring it for each application.")

    return recs[:8]


def _identify_strengths_weaknesses(
    score, matched_requirements, missing_skills, quality_metrics, section_statuses
):
    strengths = []
    weaknesses = []

    # Strong sections
    detected_sections = [s.name for s in section_statuses if s.detected]
    if len(detected_sections) >= 5:
        strengths.append("Resume has a complete structure with all major sections present")
    if "experience" in detected_sections:
        strengths.append("Professional experience section clearly identified")
    if "projects" in detected_sections:
        strengths.append("Projects section adds strong technical evidence")

    # Strong keyword match
    exact_matches = [r for r in matched_requirements if r.match_type in ("exact", "normalized")]
    if len(exact_matches) > 5:
        strengths.append(f"{len(exact_matches)} key requirements matched directly")

    if quality_metrics.action_verb_score >= 0.7:
        strengths.append("Strong use of action verbs throughout experience section")

    if quality_metrics.quantification_score >= 0.4:
        strengths.append(f"{quality_metrics.bullets_with_metrics} bullets include measurable achievements")

    if score.ats_parsing_safety >= 0.9:
        strengths.append("Resume is highly ATS-compatible with no major parsing issues")

    # Weaknesses
    if missing_skills:
        high_missing = [m for m in missing_skills if m.importance in ("critical", "high")]
        if high_missing:
            weaknesses.append(
                f"{len(high_missing)} high-importance requirement(s) not found: "
                f"{', '.join(m.skill for m in high_missing[:3])}"
            )

    if quality_metrics.quantification_score < 0.3:
        weaknesses.append("Most bullets lack measurable impact or specific numbers")

    if quality_metrics.action_verb_score < 0.5:
        weaknesses.append("Many bullet points don't start with strong action verbs")

    if quality_metrics.weak_phrase_count > 1:
        weaknesses.append(f"{quality_metrics.weak_phrase_count} weak or generic phrases detected")

    missing_sec = [s for s in section_statuses if not s.detected and s.name in ["summary", "skills"]]
    for sec in missing_sec:
        weaknesses.append(f"'{sec.name.title()}' section not detected")

    if score.ats_parsing_safety < 0.75:
        weaknesses.append("ATS parsing issues may reduce resume readability")

    return strengths[:6], weaknesses[:6]

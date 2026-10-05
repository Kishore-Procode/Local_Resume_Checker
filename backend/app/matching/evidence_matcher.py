"""
Evidence Matcher: maps matched requirements to best-fit resume evidence text.
Consolidates results from keyword, fuzzy, and semantic matchers.
"""
from typing import List, Optional, Tuple

from app.models.schemas import (
    MatchedRequirement, MissingSkill, WeakMatch, MatchType, Confidence
)
from app.analyzers.skill_extractor import get_skill_category
from app.utils.text_utils import truncate_text


def build_missing_skills(
    unmatched_requirements: List[MatchedRequirement],
    resume_text: str,
    jd_keywords: dict,
) -> List[MissingSkill]:
    """
    Build MissingSkill objects for unmatched requirements.
    Looks for any related/partial evidence in the resume.
    """
    missing: List[MissingSkill] = []
    resume_lower = resume_text.lower()

    for req in unmatched_requirements:
        if req.match_type in (MatchType.EXACT, MatchType.NORMALIZED, MatchType.FUZZY, MatchType.SEMANTIC):
            continue

        # Check if there's any related term in the resume
        related_evidence = _find_related_evidence(req.requirement, resume_lower, resume_text)

        # Get frequency from JD keyword map
        jd_freq = jd_keywords.get(req.requirement, 1)

        # Build a helpful suggestion (NOT telling them to lie)
        if related_evidence:
            suggestion = (
                f"Your resume contains related content, but does not explicitly mention '{req.requirement}'. "
                f"If you genuinely have this experience, consider using the exact term."
            )
        else:
            suggestion = (
                f"If you genuinely have '{req.requirement}' experience, consider explicitly mentioning it. "
                f"Do not add it if you do not have real experience with it."
            )

        missing.append(MissingSkill(
            skill=req.requirement,
            category=get_skill_category(req.requirement),
            importance=req.importance,
            jd_frequency=jd_freq,
            related_evidence=related_evidence[:80] if related_evidence else None,
            related_evidence_text=related_evidence,
            suggestion=suggestion,
        ))

    # Sort by importance, then frequency
    importance_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    missing.sort(key=lambda m: (importance_order.get(m.importance, 4), -m.jd_frequency))
    return missing


def build_weak_matches(
    weak_matched: List[MatchedRequirement],
) -> List[WeakMatch]:
    """Build WeakMatch objects from requirements that had low-confidence semantic matches."""
    weak_matches = []
    for req in weak_matched:
        if req.match_type != MatchType.WEAK:
            continue
        evidence = req.evidence_text or "No direct evidence found."
        explanation = (
            f"The resume contains potentially related content, but does not explicitly mention '{req.requirement}'. "
            f"Semantic similarity: {round((req.semantic_score or 0) * 100, 1)}%."
        )
        recommendation = (
            f"If you have '{req.requirement}' experience, use this exact term in your resume for clarity."
        )
        weak_matches.append(WeakMatch(
            requirement=req.requirement,
            resume_evidence=truncate_text(evidence, 200),
            explanation=explanation,
            recommendation=recommendation,
        ))
    return weak_matches


def _find_related_evidence(requirement: str, resume_lower: str, resume_text: str) -> Optional[str]:
    """
    Look for semantically related terms in the resume as partial evidence.
    Uses a simple keyword decomposition approach.
    """
    # Split requirement into component words
    req_words = [w for w in requirement.lower().split() if len(w) > 3]

    # Related skill families
    related_terms = _get_related_terms(requirement.lower())
    all_terms = req_words + related_terms

    for term in all_terms:
        if term in resume_lower:
            idx = resume_lower.find(term)
            start = max(0, idx - 40)
            end = min(len(resume_text), idx + len(term) + 60)
            return resume_text[start:end].strip().replace("\n", " ")

    return None


def _get_related_terms(skill: str) -> List[str]:
    """Map a skill to related terms that might appear in a resume."""
    related_map = {
        "docker": ["container", "containeriz", "dockerfile", "compose"],
        "kubernetes": ["k8s", "container orchestrat", "cluster", "pod", "helm"],
        "aws": ["amazon", "cloud", "ec2", "s3", "lambda", "serverless"],
        "ci/cd": ["pipeline", "deploy", "continuous", "github actions", "jenkins", "automation"],
        "machine learning": ["model", "training", "prediction", "algorithm", "ml", "dataset"],
        "deep learning": ["neural", "cnn", "rnn", "lstm", "transformer", "pytorch", "tensorflow"],
        "agile": ["scrum", "sprint", "kanban", "standup", "jira"],
        "graphql": ["query", "api", "schema", "resolver"],
        "redis": ["cache", "caching", "in-memory", "session"],
        "elasticsearch": ["search", "index", "kibana", "elk"],
        "terraform": ["infrastructure as code", "iac", "provision", "cloud config"],
        "microservices": ["service", "api", "distributed", "scalable architecture"],
        "postgresql": ["postgres", "sql", "relational", "database"],
        "mongodb": ["nosql", "document", "mongo", "atlas"],
    }
    return related_map.get(skill.lower(), [])

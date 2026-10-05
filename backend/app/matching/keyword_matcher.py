"""
Keyword Matcher: exact and normalized keyword matching.
"""
import re
from typing import Dict, List, Tuple

from app.analyzers.skill_extractor import normalize_skill_name
from app.models.schemas import MatchedRequirement, MatchType, Confidence
from app.utils.text_utils import normalize_skill


def keyword_match(
    requirement: str,
    resume_text: str,
    resume_text_lower: str,
    requirement_category: str = "required",
    requirement_importance: str = "high",
) -> MatchedRequirement:
    """
    Try to match a single requirement against the resume using exact/normalized matching.
    Returns a MatchedRequirement with match_type=MISSING if not found.
    """
    # ── Exact match ───────────────────────────────────────────────────────────
    escaped = re.escape(requirement.lower())
    pattern = r"(?<!\w)" + escaped + r"(?!\w)"
    match = re.search(pattern, resume_text_lower)

    if match:
        # Extract evidence context
        start = max(0, match.start() - 60)
        end = min(len(resume_text), match.end() + 60)
        evidence = resume_text[start:end].strip().replace("\n", " ")
        return MatchedRequirement(
            requirement=requirement,
            category=requirement_category,
            importance=requirement_importance,
            match_type=MatchType.EXACT,
            confidence=Confidence.HIGH,
            score=1.0,
            evidence_text=evidence,
            evidence_snippet=evidence[:150],
        )

    # ── Normalized match ──────────────────────────────────────────────────────
    norm_req = normalize_skill(requirement)
    canonical = normalize_skill_name(requirement)
    norm_canonical = normalize_skill(canonical)

    # Try canonical form
    escaped_norm = re.escape(norm_canonical)
    pattern_norm = r"(?<!\w)" + escaped_norm + r"(?!\w)"
    match_norm = re.search(pattern_norm, resume_text_lower)

    if match_norm:
        start = max(0, match_norm.start() - 60)
        end = min(len(resume_text), match_norm.end() + 60)
        evidence = resume_text[start:end].strip().replace("\n", " ")
        return MatchedRequirement(
            requirement=requirement,
            category=requirement_category,
            importance=requirement_importance,
            match_type=MatchType.NORMALIZED,
            confidence=Confidence.HIGH,
            score=0.95,
            evidence_text=evidence,
            evidence_snippet=evidence[:150],
        )

    # Also try searching for aliases of the requirement
    aliases = _get_aliases_for(requirement)
    for alias in aliases:
        escaped_alias = re.escape(alias.lower())
        pat = r"(?<!\w)" + escaped_alias + r"(?!\w)"
        m = re.search(pat, resume_text_lower)
        if m:
            start = max(0, m.start() - 60)
            end = min(len(resume_text), m.end() + 60)
            evidence = resume_text[start:end].strip().replace("\n", " ")
            return MatchedRequirement(
                requirement=requirement,
                category=requirement_category,
                importance=requirement_importance,
                match_type=MatchType.NORMALIZED,
                confidence=Confidence.HIGH,
                score=0.90,
                evidence_text=evidence,
                evidence_snippet=evidence[:150],
            )

    # ── No match ──────────────────────────────────────────────────────────────
    return MatchedRequirement(
        requirement=requirement,
        category=requirement_category,
        importance=requirement_importance,
        match_type=MatchType.MISSING,
        confidence=Confidence.NONE,
        score=0.0,
        evidence_text=None,
        evidence_snippet=None,
    )


def _get_aliases_for(skill: str) -> List[str]:
    """Get all known aliases for a skill name."""
    import json
    from pathlib import Path
    try:
        aliases_path = Path(__file__).parent.parent / "data" / "aliases.json"
        with open(aliases_path, encoding="utf-8") as f:
            alias_map = json.load(f)
        canonical = normalize_skill_name(skill)
        return [alias for alias, can in alias_map.items() if can.lower() == canonical.lower()]
    except Exception:
        return []


def batch_keyword_match(
    requirements: List[dict],
    resume_text: str,
) -> Tuple[List[MatchedRequirement], List[MatchedRequirement]]:
    """
    Match all requirements against resume text.
    Returns (matched, unmatched).
    """
    resume_text_lower = resume_text.lower()
    matched = []
    unmatched = []

    for req in requirements:
        result = keyword_match(
            requirement=req["text"],
            resume_text=resume_text,
            resume_text_lower=resume_text_lower,
            requirement_category=req.get("category", "required"),
            requirement_importance=req.get("importance", "medium"),
        )
        if result.match_type in (MatchType.EXACT, MatchType.NORMALIZED):
            matched.append(result)
        else:
            unmatched.append(result)

    return matched, unmatched

"""
Fuzzy Matcher: uses RapidFuzz for approximate skill/keyword matching.
"""
import re
from typing import List, Optional, Tuple

from rapidfuzz import fuzz, process

from app.config import FUZZY_THRESHOLD
from app.models.schemas import MatchedRequirement, MatchType, Confidence
from app.utils.text_utils import normalize_skill


def fuzzy_match_requirement(
    requirement: str,
    resume_text: str,
    requirement_category: str = "required",
    requirement_importance: str = "medium",
) -> MatchedRequirement:
    """
    Try to fuzzy-match a requirement against resume sentences/words.
    Only called after exact/normalized matching has failed.
    """
    norm_req = normalize_skill(requirement)
    resume_words = _extract_meaningful_terms(resume_text)

    # Try token_sort_ratio against all extracted terms
    best_match, best_score, _ = process.extractOne(
        norm_req,
        resume_words,
        scorer=fuzz.token_sort_ratio,
    ) if resume_words else (None, 0, None)

    if best_score is not None and best_score >= FUZZY_THRESHOLD:
        # Find the context around this match
        evidence = _find_context(best_match, resume_text)
        confidence = Confidence.HIGH if best_score >= 90 else Confidence.MEDIUM if best_score >= 80 else Confidence.LOW

        return MatchedRequirement(
            requirement=requirement,
            category=requirement_category,
            importance=requirement_importance,
            match_type=MatchType.FUZZY,
            confidence=confidence,
            score=round(best_score / 100, 3),
            evidence_text=evidence,
            evidence_snippet=evidence[:150] if evidence else None,
            fuzzy_score=round(best_score, 1),
        )

    return MatchedRequirement(
        requirement=requirement,
        category=requirement_category,
        importance=requirement_importance,
        match_type=MatchType.MISSING,
        confidence=Confidence.NONE,
        score=0.0,
        evidence_text=None,
        evidence_snippet=None,
        fuzzy_score=best_score,
    )


def batch_fuzzy_match(
    unmatched: List[MatchedRequirement],
    resume_text: str,
) -> Tuple[List[MatchedRequirement], List[MatchedRequirement]]:
    """
    Run fuzzy matching on all unmatched requirements.
    Returns (newly_matched, still_unmatched).
    """
    newly_matched = []
    still_unmatched = []

    for req in unmatched:
        result = fuzzy_match_requirement(
            requirement=req.requirement,
            resume_text=resume_text,
            requirement_category=req.category,
            requirement_importance=req.importance,
        )
        if result.match_type == MatchType.FUZZY:
            newly_matched.append(result)
        else:
            # Preserve any fuzzy_score we computed for use in semantic step
            still_unmatched.append(result)

    return newly_matched, still_unmatched


def _extract_meaningful_terms(text: str) -> List[str]:
    """Extract 1-3 word terms from resume text for fuzzy comparison."""
    terms = set()
    text_lower = text.lower()

    # Single words (alphanumeric + common punctuation)
    words = re.findall(r"\b[a-z][a-z0-9\.\+\#\-]{1,}\b", text_lower)
    terms.update(w for w in words if len(w) > 2)

    # Two-word phrases
    word_list = [w for w in re.findall(r"\b[a-z][a-z0-9]{1,}\b", text_lower) if len(w) > 2]
    for i in range(len(word_list) - 1):
        phrase = f"{word_list[i]} {word_list[i+1]}"
        terms.add(phrase)

    # Three-word phrases
    for i in range(len(word_list) - 2):
        phrase = f"{word_list[i]} {word_list[i+1]} {word_list[i+2]}"
        terms.add(phrase)

    return list(terms)


def _find_context(matched_term: str, resume_text: str, context_chars: int = 120) -> Optional[str]:
    """Find the context around a matched term in the resume."""
    if not matched_term:
        return None
    pattern = re.compile(re.escape(matched_term), re.IGNORECASE)
    m = pattern.search(resume_text)
    if m:
        start = max(0, m.start() - context_chars // 2)
        end = min(len(resume_text), m.end() + context_chars // 2)
        return resume_text[start:end].strip().replace("\n", " ")
    return None

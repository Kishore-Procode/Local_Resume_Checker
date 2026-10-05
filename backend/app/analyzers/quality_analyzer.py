"""
Resume Quality Analyzer.
Analyzes action verbs, quantifiable achievements, weak phrases,
first-person language, bullet structure, and repetition.
"""
import re
from collections import Counter
from typing import List, Tuple

from app.config import ACTION_VERBS, WEAK_PHRASES
from app.models.schemas import QualityIssue, QualityMetrics
from app.utils.text_utils import (
    extract_numbers_from_text,
    remove_bullets,
    split_into_sentences,
)


def analyze_quality(sections_text: dict, raw_text: str) -> QualityMetrics:
    """
    Analyze resume quality from all sections.
    Returns QualityMetrics with scores and issues.
    """
    issues: List[QualityIssue] = []

    # Collect all bullet points from experience, projects, achievements
    all_bullets = _collect_bullets(sections_text)
    total_bullets = len(all_bullets)

    # ── Action Verb Analysis ──────────────────────────────────────────────────
    action_verb_count = 0
    no_action_verb_bullets = []

    for bullet in all_bullets:
        words = bullet.strip().split()
        if not words:
            continue
        first_word = words[0].lower().rstrip(".,:")
        if first_word in ACTION_VERBS:
            action_verb_count += 1
        else:
            no_action_verb_bullets.append(bullet)

    action_verb_score = action_verb_count / max(total_bullets, 1)

    # Issue: bullets not starting with action verbs
    for bullet in no_action_verb_bullets[:3]:
        preview = bullet[:80]
        issues.append(QualityIssue(
            issue_type="weak_verb",
            severity="medium",
            affected_text=preview,
            suggestion=f"Start with a strong action verb. Instead of '{preview[:30]}...', try 'Developed...', 'Built...', or 'Implemented...'",
        ))

    # ── Quantification Analysis ───────────────────────────────────────────────
    bullets_with_metrics = 0
    for bullet in all_bullets:
        metrics = extract_numbers_from_text(bullet)
        if metrics:
            bullets_with_metrics += 1

    quantification_score = bullets_with_metrics / max(total_bullets, 1)

    if total_bullets > 0 and quantification_score < 0.3:
        issues.append(QualityIssue(
            issue_type="low_quantification",
            severity="high",
            affected_text="",
            suggestion=f"Only {bullets_with_metrics} of {total_bullets} bullets contain measurable achievements. Add specific numbers, percentages, or impact metrics where possible.",
        ))

    # ── Weak Phrase Detection ─────────────────────────────────────────────────
    weak_phrase_count = 0
    full_text_lower = raw_text.lower()

    for phrase in WEAK_PHRASES:
        if phrase.lower() in full_text_lower:
            weak_phrase_count += 1
            # Find containing sentence
            idx = full_text_lower.find(phrase.lower())
            ctx = raw_text[max(0, idx - 20):idx + len(phrase) + 50].strip()
            issues.append(QualityIssue(
                issue_type="weak_phrase",
                severity="medium",
                affected_text=ctx[:100],
                suggestion=f"Replace '{phrase}' with a specific action verb and measurable outcome.",
            ))

    # ── First-Person Language ──────────────────────────────────────────────────
    first_person_patterns = [r"\bI\b", r"\bmy\b", r"\bme\b", r"\bI've\b", r"\bI'm\b", r"\bI'd\b"]
    first_person_count = sum(
        len(re.findall(p, raw_text)) for p in first_person_patterns
    )
    if first_person_count > 2:
        issues.append(QualityIssue(
            issue_type="first_person",
            severity="low",
            affected_text="",
            suggestion=f"Avoid first-person language in resumes. Found {first_person_count} instances of 'I/me/my'. Use action verbs directly: 'Developed...' instead of 'I developed...'",
        ))

    # ── Bullet Length ─────────────────────────────────────────────────────────
    if total_bullets > 0:
        avg_length = sum(len(b.split()) for b in all_bullets) / total_bullets
    else:
        avg_length = 0.0

    long_bullets = [b for b in all_bullets if len(b.split()) > 30]
    for bullet in long_bullets[:2]:
        issues.append(QualityIssue(
            issue_type="long_bullet",
            severity="low",
            affected_text=bullet[:100],
            suggestion="This bullet point is too long. Split into two separate achievements or trim to 15-25 words.",
        ))

    short_bullets = [b for b in all_bullets if 0 < len(b.split()) < 5]
    for bullet in short_bullets[:2]:
        issues.append(QualityIssue(
            issue_type="short_bullet",
            severity="low",
            affected_text=bullet,
            suggestion="This bullet is too short to be meaningful. Expand it with context and impact.",
        ))

    # ── Repetition Detection ──────────────────────────────────────────────────
    repeated_phrases = _detect_repetition(all_bullets)
    if repeated_phrases:
        issues.append(QualityIssue(
            issue_type="repetition",
            severity="low",
            affected_text=", ".join(repeated_phrases[:3]),
            suggestion=f"The following phrases are repeated across multiple bullets: {', '.join(repeated_phrases[:3])}. Vary your language to showcase broader expertise.",
        ))

    # ── Achievement Strength ─────────────────────────────────────────────────
    achievements_text = sections_text.get("achievements", "")
    experience_text = sections_text.get("experience", "")
    combined = achievements_text + "\n" + experience_text
    achievement_numbers = extract_numbers_from_text(combined)

    # ── Overall Quality Score ─────────────────────────────────────────────────
    # Components: action_verb (40%) + quantification (40%) + no weak phrases (20%)
    weak_penalty = min(weak_phrase_count * 0.05, 0.30)
    first_person_penalty = min(first_person_count * 0.02, 0.10)
    overall_quality_score = (
        action_verb_score * 0.40
        + quantification_score * 0.40
        + (1.0 - weak_penalty) * 0.15
        + (1.0 - first_person_penalty) * 0.05
    )

    return QualityMetrics(
        action_verb_score=round(action_verb_score, 3),
        quantification_score=round(quantification_score, 3),
        weak_phrase_count=weak_phrase_count,
        first_person_count=first_person_count,
        average_bullet_length=round(avg_length, 1),
        total_bullets=total_bullets,
        bullets_with_metrics=bullets_with_metrics,
        repeated_phrases=repeated_phrases[:5],
        quality_issues=issues[:15],
        overall_quality_score=round(overall_quality_score, 3),
    )


def _collect_bullets(sections_text: dict) -> List[str]:
    """Collect bullet points from key sections."""
    bullets = []
    for section in ["experience", "projects", "achievements", "education"]:
        text = sections_text.get(section, "")
        if not text:
            continue
        for line in text.split("\n"):
            cleaned = remove_bullets(line.strip())
            if cleaned and len(cleaned.split()) >= 3:
                bullets.append(cleaned)
    return bullets


def _detect_repetition(bullets: List[str]) -> List[str]:
    """Detect repeated 2-3 word phrases across bullets."""
    phrase_counter: Counter = Counter()
    for bullet in bullets:
        words = bullet.lower().split()
        for i in range(len(words) - 1):
            phrase = " ".join(words[i:i+2])
            if len(phrase) > 6:  # skip very short phrases
                phrase_counter[phrase] += 1
    return [phrase for phrase, count in phrase_counter.items() if count >= 3]

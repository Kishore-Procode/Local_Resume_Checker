"""
Section detector: identifies resume sections from raw text.
Uses pattern matching with flexible heading recognition.
"""
import re
from typing import Dict, List, Optional, Tuple

from app.models.schemas import SectionStatus
from app.utils.text_utils import clean_text, remove_bullets


# ─── Section Heading Patterns ─────────────────────────────────────────────────
SECTION_PATTERNS: Dict[str, List[str]] = {
    "contact": [
        "contact", "contact information", "contact details", "personal information",
        "personal details", "contact info",
    ],
    "summary": [
        "summary", "professional summary", "executive summary", "career summary",
        "objective", "career objective", "professional objective", "profile",
        "professional profile", "about me", "about", "overview", "bio",
    ],
    "skills": [
        "skills", "technical skills", "core skills", "key skills", "skill set",
        "core competencies", "competencies", "technologies", "technical expertise",
        "areas of expertise", "expertise", "proficiencies", "technical proficiencies",
        "tools & technologies", "tools and technologies", "languages & technologies",
        "programming skills", "hard skills",
    ],
    "experience": [
        "experience", "work experience", "professional experience", "employment",
        "employment history", "work history", "career history", "professional background",
        "relevant experience", "industry experience", "internships", "internship experience",
        "job experience", "positions held",
    ],
    "education": [
        "education", "academic background", "academic history", "academics",
        "qualifications", "educational background", "educational qualifications",
        "degrees", "academic credentials", "scholastic background",
    ],
    "projects": [
        "projects", "personal projects", "academic projects", "side projects",
        "portfolio projects", "key projects", "notable projects", "project work",
        "open source projects", "open-source", "portfolio",
    ],
    "certifications": [
        "certifications", "certificates", "certification", "professional certifications",
        "professional certificates", "licenses", "credentials", "accreditations",
        "professional development",
    ],
    "achievements": [
        "achievements", "accomplishments", "awards", "honors", "recognition",
        "distinctions", "honors and awards", "awards and recognition",
    ],
    "publications": [
        "publications", "research", "papers", "research papers", "journal articles",
        "conference papers", "academic publications", "patents",
    ],
    "languages": [
        "languages", "language skills", "language proficiency", "spoken languages",
    ],
    "volunteer": [
        "volunteer", "volunteering", "volunteer experience", "community service",
        "social work", "extracurricular",
    ],
    "interests": [
        "interests", "hobbies", "personal interests", "activities",
    ],
    "references": [
        "references", "referees", "professional references",
    ],
}

# Build reversed lookup: normalized heading → section name
_HEADING_TO_SECTION: Dict[str, str] = {}
for _section, _headings in SECTION_PATTERNS.items():
    for _h in _headings:
        _HEADING_TO_SECTION[_h.lower().strip()] = _section


def detect_sections(raw_text: str) -> Tuple[Dict[str, str], List[SectionStatus]]:
    """
    Parse raw text and identify sections.

    Returns:
        sections_text: dict of {section_name: section_raw_text}
        section_statuses: list of SectionStatus objects for UI display
    """
    lines = raw_text.split("\n")
    sections_text: Dict[str, str] = {}
    section_order: List[Tuple[int, str, str]] = []  # (line_idx, section_name, heading_found)

    # ── First pass: identify heading lines ───────────────────────────────────
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        detected = _match_heading(stripped)
        if detected:
            section_name, matched_heading = detected
            # Avoid duplicate detection of same section
            already_found = any(s == section_name for _, s, _ in section_order)
            if not already_found:
                section_order.append((i, section_name, matched_heading))

    # ── Second pass: extract text for each section ────────────────────────────
    for idx, (start_line, section_name, heading) in enumerate(section_order):
        if idx + 1 < len(section_order):
            end_line = section_order[idx + 1][0]
        else:
            end_line = len(lines)

        section_lines = lines[start_line + 1 : end_line]
        section_text = "\n".join(section_lines).strip()
        sections_text[section_name] = section_text

    # ── Build SectionStatus list ──────────────────────────────────────────────
    all_expected = ["contact", "summary", "skills", "experience", "education", "projects",
                    "certifications", "achievements", "publications", "languages", "volunteer"]
    section_statuses: List[SectionStatus] = []

    detected_names = {s for _, s, _ in section_order}
    heading_map = {s: h for _, s, h in section_order}

    for section_name in all_expected:
        text = sections_text.get(section_name, "")
        bullets = _extract_bullets(text)
        word_count = len(text.split()) if text else 0
        preview = text[:120].strip() if text else None

        issues = []
        if section_name in detected_names and word_count < 10:
            issues.append(f"Section '{section_name}' appears empty or very short.")

        section_statuses.append(SectionStatus(
            name=section_name,
            detected=section_name in detected_names,
            heading_found=heading_map.get(section_name),
            text_preview=preview,
            word_count=word_count,
            issues=issues,
        ))

    return sections_text, section_statuses


def _match_heading(line: str) -> Optional[Tuple[str, str]]:
    """Match a line to a known section heading. Returns (section_name, matched_heading) or None."""
    # Remove trailing punctuation and normalize
    normalized = re.sub(r"[:\-–—]+$", "", line).strip().lower()
    # Remove leading bullets
    normalized = re.sub(r"^[\u2022\u2023\*\-•]+\s*", "", normalized)

    # Direct lookup
    if normalized in _HEADING_TO_SECTION:
        return _HEADING_TO_SECTION[normalized], normalized

    # Partial match for headings with extra words
    for heading, section in _HEADING_TO_SECTION.items():
        if heading in normalized and len(normalized) < len(heading) + 20:
            return section, normalized

    # Heuristic: ALL CAPS short lines
    if line.isupper() and 2 <= len(line.split()) <= 5:
        normalized_upper = line.lower().strip()
        if normalized_upper in _HEADING_TO_SECTION:
            return _HEADING_TO_SECTION[normalized_upper], line

    return None


def _extract_bullets(text: str) -> List[str]:
    """Extract bullet points from section text."""
    bullets = []
    for line in text.split("\n"):
        cleaned = remove_bullets(line.strip())
        if cleaned and len(cleaned) > 5:
            bullets.append(cleaned)
    return bullets


def extract_contact_info(text: str) -> dict:
    """Extract structured contact info from the first ~300 chars or contact section."""
    from app.utils.text_utils import (
        extract_emails, extract_phones, extract_linkedin, extract_github
    )
    import re

    # Use first 500 chars + any contact section
    search_text = text[:500]

    emails = extract_emails(search_text) or extract_emails(text)
    phones = extract_phones(search_text) or extract_phones(text)
    linkedin = extract_linkedin(text)
    github = extract_github(text)

    # Name: usually the first non-empty line
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    name = None
    if lines:
        first_line = lines[0]
        # Name is likely short (1-4 words), title case or all caps, no @ or digits
        if (len(first_line.split()) <= 5
                and not re.search(r"[@\d]", first_line)
                and not any(k in first_line.lower() for k in ["resume", "cv", "curriculum"])):
            name = first_line

    # Location: look for City, State or City, Country pattern
    location_match = re.search(
        r"([A-Z][a-z]+(?: [A-Z][a-z]+)?,\s*(?:[A-Z]{2}|[A-Z][a-z]+))",
        text[:400]
    )
    location = location_match.group(1) if location_match else None

    # Portfolio: look for personal website patterns (not linkedin/github)
    portfolio_match = re.search(
        r"(?:https?://)?(?:www\.)?((?!linkedin|github)[a-z0-9\-]+\.[a-z]{2,}(?:/[\w\-/]*)?)",
        text[:500],
        re.IGNORECASE,
    )
    portfolio = portfolio_match.group(0) if portfolio_match else None

    return {
        "name": name,
        "email": emails[0] if emails else None,
        "phone": phones[0] if phones else None,
        "linkedin": linkedin or None,
        "github": github or None,
        "portfolio": portfolio,
        "location": location,
    }

import re
import unicodedata
from typing import List


def clean_text(text: str) -> str:
    """Normalize whitespace, remove control characters, fix common encoding issues."""
    if not text:
        return ""
    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)
    # Replace non-breaking spaces and similar
    text = text.replace("\xa0", " ").replace("\u200b", "").replace("\ufeff", "")
    # Collapse multiple spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)
    # Normalize line endings
    text = re.sub(r"\r\n|\r", "\n", text)
    # Collapse more than 3 consecutive newlines
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def normalize_skill(skill: str) -> str:
    """Lowercase and strip punctuation for skill comparison."""
    skill = skill.lower().strip()
    skill = re.sub(r"[^\w\s\.\+\#]", "", skill)
    skill = re.sub(r"\s+", " ", skill)
    return skill


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using simple regex."""
    # Split on . ! ? followed by whitespace or end
    sentences = re.split(r"(?<=[.!?])\s+", text)
    # Also split on newlines for bullet points
    result = []
    for sent in sentences:
        lines = sent.split("\n")
        for line in lines:
            line = line.strip()
            if len(line) > 10:  # Skip very short fragments
                result.append(line)
    return result


def split_into_chunks(text: str, chunk_size: int = 3) -> List[str]:
    """Split text into overlapping sentence chunks for semantic matching."""
    sentences = split_into_sentences(text)
    if not sentences:
        return []
    chunks = []
    for i in range(len(sentences)):
        chunk = " ".join(sentences[max(0, i - 1) : i + chunk_size])
        if chunk.strip():
            chunks.append(chunk.strip())
    return list(dict.fromkeys(chunks))  # deduplicate preserving order


def extract_years_of_experience(text: str) -> float:
    """Extract maximum years of experience mentioned in text."""
    patterns = [
        r"(\d+)\+?\s*years?\s+of\s+(?:professional\s+)?experience",
        r"(\d+)\+?\s*years?\s+experience",
        r"(\d+)\+?\s*yr[s]?\s+(?:of\s+)?experience",
        r"over\s+(\d+)\s+years?",
        r"(\d+)\s*-\s*(\d+)\s+years?",  # range like 3-5 years
        r"(\d+)\+\s*years?",
    ]
    years_found = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            try:
                years_found.append(float(match.group(1)))
            except (IndexError, ValueError):
                pass
    return max(years_found) if years_found else 0.0


def extract_numbers_from_text(text: str) -> List[str]:
    """Extract numeric/quantifiable achievements from text."""
    patterns = [
        r"\d+%",                            # percentages
        r"\$[\d,]+(?:\.\d+)?[KMBkmb]?",    # money
        r"[\d,]+\s*(?:users|customers|clients|requests|transactions)",
        r"(?:by|of|over|more than|up to)\s+\d+",
        r"\d+x\s+(?:faster|improvement|increase|speedup)",
        r"\d+\+?\s*(?:projects|applications|services|systems)",
    ]
    results = []
    for pattern in patterns:
        results.extend(re.findall(pattern, text, re.IGNORECASE))
    return results


def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text."""
    pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    return re.findall(pattern, text)


def extract_phones(text: str) -> List[str]:
    """Extract phone numbers from text."""
    pattern = r"(?:\+?\d{1,3}[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}"
    return re.findall(pattern, text)


def extract_linkedin(text: str) -> str:
    """Extract LinkedIn URL or handle."""
    pattern = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0) if match else ""


def extract_github(text: str) -> str:
    """Extract GitHub URL or handle."""
    pattern = r"(?:https?://)?(?:www\.)?github\.com/[\w\-]+"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0) if match else ""


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split()) if text else 0


def truncate_text(text: str, max_chars: int = 200) -> str:
    """Truncate text to max_chars with ellipsis."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "…"


def is_likely_heading(line: str) -> bool:
    """Heuristic: is this line a section heading?"""
    line = line.strip()
    if not line:
        return False
    # Short lines (1-5 words) in all-caps or title case
    words = line.split()
    if len(words) > 7:
        return False
    if line.isupper() and len(words) <= 5:
        return True
    # Title case with no punctuation at end
    if line.istitle() and not line.endswith((".", ",", ";")):
        return True
    # Ends with colon
    if line.endswith(":"):
        return True
    return False


def remove_bullets(text: str) -> str:
    """Strip common bullet characters from start of line."""
    return re.sub(r"^[\u2022\u2023\u25E6\u2043\u2219\*\-\•\·\→\►\▪\▸]+\s*", "", text.strip())

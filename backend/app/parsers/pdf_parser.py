"""
PDF parser using PyMuPDF (fitz).
Extracts text, detects ATS safety issues, returns structured data.
"""
import re
from typing import List, Tuple
import fitz  # PyMuPDF

from app.models.schemas import ParsingIssue
from app.utils.text_utils import clean_text, extract_emails, extract_phones


def parse_pdf(file_bytes: bytes, filename: str) -> dict:
    """
    Parse a PDF file and return extracted text with ATS analysis.

    Returns:
        dict with keys:
            raw_text, pages, page_count, text_length,
            word_count, parsing_issues, ats_safety_score,
            parsing_status
    """
    issues: List[ParsingIssue] = []

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        return {
            "raw_text": "",
            "pages": [],
            "page_count": 0,
            "text_length": 0,
            "word_count": 0,
            "parsing_issues": [
                ParsingIssue(
                    severity="critical",
                    category="file_corruption",
                    message="Could not open PDF. The file may be corrupted or password-protected.",
                    recommendation="Save the resume as a new PDF from a text editor or word processor.",
                )
            ],
            "ats_safety_score": 0.0,
            "parsing_status": "failed",
        }

    page_count = len(doc)
    pages_text: List[str] = []
    all_blocks = []
    image_only_pages = 0
    low_density_pages = 0

    for page_num, page in enumerate(doc):
        # Extract text blocks with positions
        blocks = page.get_text("blocks")  # list of (x0, y0, x1, y1, text, block_no, block_type)
        text_blocks = [b for b in blocks if b[6] == 0 and b[4].strip()]  # type 0 = text
        image_blocks = [b for b in blocks if b[6] == 1]  # type 1 = image

        page_text = page.get_text("text")
        page_text = clean_text(page_text)

        # Check for image-only page
        if not page_text.strip() and image_blocks:
            image_only_pages += 1
        elif len(page_text.strip()) < 100 and page_num == 0:
            # Very low text on first page
            low_density_pages += 1

        pages_text.append(page_text)
        all_blocks.extend(text_blocks)

    doc.close()

    raw_text = "\n\n".join(pages_text)
    word_count = len(raw_text.split())

    # ── ATS Checks ─────────────────────────────────────────────────────────

    # 1. Image-only pages
    if image_only_pages == page_count:
        issues.append(ParsingIssue(
            severity="critical",
            category="image_only",
            message="Your resume appears to be image-based (scanned). No text could be extracted.",
            recommendation="Re-create your resume as a text-based document. Scanned PDFs cannot be read by most ATS systems.",
        ))
    elif image_only_pages > 0:
        issues.append(ParsingIssue(
            severity="high",
            category="image_pages",
            message=f"{image_only_pages} of {page_count} page(s) contain only images with no extractable text.",
            recommendation="Ensure all pages contain selectable text, not embedded images of text.",
        ))

    # 2. Very low text density
    if word_count < 100 and image_only_pages < page_count:
        issues.append(ParsingIssue(
            severity="high",
            category="low_text_density",
            message=f"Very little text was extracted ({word_count} words). The resume may use complex graphics.",
            recommendation="Simplify the layout and ensure your content is plain selectable text.",
        ))

    # 3. Check for multi-column layout indicators
    if _detect_multi_column(all_blocks):
        issues.append(ParsingIssue(
            severity="medium",
            category="multi_column",
            message="The resume appears to use a multi-column layout. Some ATS systems read columns left-to-right across the entire page, mixing content from different columns.",
            recommendation="Consider using a single-column layout for maximum ATS compatibility.",
        ))

    # 4. Unusual characters
    unusual_chars = _detect_unusual_characters(raw_text)
    if unusual_chars:
        issues.append(ParsingIssue(
            severity="low",
            category="unusual_characters",
            message=f"Unusual or decorative characters detected: {', '.join(unusual_chars[:5])}. These may not render correctly in all ATS systems.",
            recommendation="Replace decorative symbols with plain text equivalents (e.g., use '-' instead of '•' if needed).",
        ))

    # 5. Broken email check
    emails = extract_emails(raw_text)
    if not emails:
        # Check if there's an @ sign that looks like a broken email
        if "@" in raw_text:
            issues.append(ParsingIssue(
                severity="medium",
                category="broken_email",
                message="An email address was detected but could not be properly extracted. It may be formatted in a way that confuses parsers.",
                recommendation="Use plain text email format: yourname@domain.com",
            ))

    # 6. Broken phone check
    phones = extract_phones(raw_text)
    phone_digit_groups = re.findall(r"\d{3,}", raw_text)
    if not phones and len(phone_digit_groups) > 0:
        issues.append(ParsingIssue(
            severity="low",
            category="phone_format",
            message="A phone number may be formatted in an unusual way that some ATS systems cannot parse.",
            recommendation="Use standard phone formats: (555) 123-4567 or +1-555-123-4567",
        ))

    # 7. Broken URLs
    broken_urls = _detect_broken_urls(raw_text)
    if broken_urls:
        issues.append(ParsingIssue(
            severity="low",
            category="broken_urls",
            message="Some URLs appear to be split across lines or contain unusual formatting.",
            recommendation="Ensure URLs are on a single line and include the full https:// prefix.",
        ))

    # 8. Very short document
    if word_count < 200:
        issues.append(ParsingIssue(
            severity="medium",
            category="too_short",
            message=f"The resume is very short ({word_count} words). ATS systems may flag it as incomplete.",
            recommendation="A typical professional resume should have 400-700 words. Ensure all sections are complete.",
        ))

    # 9. Very long document (> 3 pages worth of text)
    if word_count > 1500 and page_count <= 2:
        issues.append(ParsingIssue(
            severity="low",
            category="text_density",
            message="The resume has an unusually high text density. It may be difficult to parse cleanly.",
            recommendation="Consider using more whitespace and concise bullet points.",
        ))

    # ── Compute ATS Safety Score ───────────────────────────────────────────
    penalty = _compute_penalty(issues)
    ats_safety_score = max(0.0, 1.0 - penalty)

    parsing_status = "success"
    if any(i.severity == "critical" for i in issues):
        parsing_status = "failed"
    elif any(i.severity == "high" for i in issues):
        parsing_status = "partial"

    return {
        "raw_text": raw_text,
        "pages": pages_text,
        "page_count": page_count,
        "text_length": len(raw_text),
        "word_count": word_count,
        "parsing_issues": issues,
        "ats_safety_score": ats_safety_score,
        "parsing_status": parsing_status,
    }


def _detect_multi_column(blocks: list) -> bool:
    """Detect if the PDF likely uses multi-column layout based on block x-positions."""
    if len(blocks) < 10:
        return False
    x_starts = [b[0] for b in blocks]
    # If there are text blocks starting in both left (<200) and right (>300) areas
    left_cols = [x for x in x_starts if x < 200]
    right_cols = [x for x in x_starts if x > 300]
    return len(left_cols) > 3 and len(right_cols) > 3


def _detect_unusual_characters(text: str) -> List[str]:
    """Detect unusual decorative unicode characters."""
    unusual = []
    for char in set(text):
        code = ord(char)
        # Check for decorative/special unicode ranges (not basic latin, latin-1, common punctuation)
        if code > 0x2500 and code not in range(0x2580, 0x25FF):
            if char not in "•·→►▪▸●○◆◇▶▷▲△▼▽":
                unusual.append(repr(char))
        # Excessive decorative bullets
        if char in "❖✦✧✩✪✫✬✭✮✯✰✱✲✳✴✵✶✷✸✹✺✻✼✽✾":
            unusual.append(repr(char))
    return unusual[:10]


def _detect_broken_urls(text: str) -> bool:
    """Detect URLs that appear to span multiple lines."""
    # Look for http/https that doesn't have a complete domain following it
    broken = re.findall(r"https?://\s*\n", text)
    return len(broken) > 0


def _compute_penalty(issues: List[ParsingIssue]) -> float:
    """Compute cumulative penalty from parsing issues."""
    severity_weights = {
        "critical": 0.40,
        "high": 0.20,
        "medium": 0.08,
        "low": 0.03,
    }
    total = sum(severity_weights.get(i.severity, 0) for i in issues)
    return min(total, 1.0)

"""
DOCX parser using python-docx.
Extracts text from paragraphs and tables, detects ATS issues.
"""
from typing import List

from docx import Document
from docx.oxml.ns import qn
import io

from app.models.schemas import ParsingIssue
from app.utils.text_utils import clean_text, extract_emails, extract_phones


def parse_docx(file_bytes: bytes, filename: str) -> dict:
    """
    Parse a DOCX file and return extracted text with ATS analysis.
    """
    issues: List[ParsingIssue] = []

    try:
        doc = Document(io.BytesIO(file_bytes))
    except Exception:
        return {
            "raw_text": "",
            "pages": [],
            "page_count": None,
            "text_length": 0,
            "word_count": 0,
            "parsing_issues": [
                ParsingIssue(
                    severity="critical",
                    category="file_corruption",
                    message="Could not open DOCX file. It may be corrupted or in an unsupported format.",
                    recommendation="Re-save the document as DOCX from Microsoft Word or Google Docs.",
                )
            ],
            "ats_safety_score": 0.0,
            "parsing_status": "failed",
        }

    text_parts: List[str] = []
    has_tables = False
    has_text_boxes = False

    # ── Extract paragraph text ──────────────────────────────────────────────
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            text_parts.append(text)

    # ── Extract table text ──────────────────────────────────────────────────
    for table in doc.tables:
        has_tables = True
        for row in table.rows:
            row_text = []
            for cell in row.cells:
                cell_text = cell.text.strip()
                if cell_text:
                    row_text.append(cell_text)
            if row_text:
                text_parts.append(" | ".join(row_text))

    # ── Check for text boxes (shapes) ──────────────────────────────────────
    for shape in _get_text_boxes(doc):
        has_text_boxes = True
        if shape.strip():
            text_parts.append(shape)

    raw_text = clean_text("\n".join(text_parts))
    word_count = len(raw_text.split())

    # ── ATS Checks ─────────────────────────────────────────────────────────

    if not raw_text.strip():
        issues.append(ParsingIssue(
            severity="critical",
            category="empty_document",
            message="No text could be extracted from the DOCX file.",
            recommendation="Ensure the document contains actual text content, not just images.",
        ))

    if has_tables:
        issues.append(ParsingIssue(
            severity="medium",
            category="tables",
            message="Your resume uses tables for layout. Many ATS systems cannot correctly parse table-based content and may scramble the reading order.",
            recommendation="Replace tables with plain bullet points and standard paragraph formatting.",
        ))

    if has_text_boxes:
        issues.append(ParsingIssue(
            severity="high",
            category="text_boxes",
            message="Text boxes were detected. Most ATS systems completely ignore text in text boxes, causing important content to be missed.",
            recommendation="Move all content out of text boxes into regular document paragraphs.",
        ))

    emails = extract_emails(raw_text)
    if not emails and "@" in raw_text:
        issues.append(ParsingIssue(
            severity="medium",
            category="broken_email",
            message="An email address was found but could not be extracted properly.",
            recommendation="Use a standard email format on its own line: yourname@example.com",
        ))

    if word_count < 200:
        issues.append(ParsingIssue(
            severity="medium",
            category="too_short",
            message=f"The resume is very short ({word_count} words).",
            recommendation="Ensure all sections are complete. A typical resume has 400-700 words.",
        ))

    # Check for header/footer content (heuristic: repeated short lines)
    header_footer_issues = _check_headers_footers(doc)
    if header_footer_issues:
        issues.append(ParsingIssue(
            severity="low",
            category="header_footer",
            message="Content in headers or footers may not be parsed correctly by some ATS systems.",
            recommendation="Move critical contact information (name, email, phone) into the main document body.",
        ))

    penalty = _compute_penalty(issues)
    ats_safety_score = max(0.0, 1.0 - penalty)

    parsing_status = "success"
    if any(i.severity == "critical" for i in issues):
        parsing_status = "failed"
    elif any(i.severity == "high" for i in issues):
        parsing_status = "partial"

    return {
        "raw_text": raw_text,
        "pages": [raw_text],
        "page_count": None,
        "text_length": len(raw_text),
        "word_count": word_count,
        "parsing_issues": issues,
        "ats_safety_score": ats_safety_score,
        "parsing_status": parsing_status,
    }


def _get_text_boxes(doc: Document) -> List[str]:
    """Attempt to extract text from drawing/text box XML elements."""
    texts = []
    try:
        body = doc.element.body
        for elem in body.iter():
            if elem.tag.endswith("}txbx") or "txbx" in elem.tag:
                for t in elem.iter(qn("w:t")):
                    if t.text:
                        texts.append(t.text)
    except Exception:
        pass
    return texts


def _check_headers_footers(doc: Document) -> bool:
    """Check if document has header/footer sections with content."""
    try:
        for section in doc.sections:
            header = section.header
            if header and any(p.text.strip() for p in header.paragraphs):
                return True
            footer = section.footer
            if footer and any(p.text.strip() for p in footer.paragraphs):
                return True
    except Exception:
        pass
    return False


def _compute_penalty(issues: List[ParsingIssue]) -> float:
    severity_weights = {
        "critical": 0.40,
        "high": 0.20,
        "medium": 0.08,
        "low": 0.03,
    }
    total = sum(severity_weights.get(i.severity, 0) for i in issues)
    return min(total, 1.0)

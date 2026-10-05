"""
Skill extractor: identifies skills from resume text using the taxonomy + aliases.
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

from app.models.schemas import ExtractedSkill, SkillCategory
from app.utils.text_utils import normalize_skill

# ─── Load taxonomy & aliases ──────────────────────────────────────────────────
_DATA_DIR = Path(__file__).parent.parent / "data"

with open(_DATA_DIR / "skills.json", encoding="utf-8") as f:
    SKILL_TAXONOMY: Dict[str, List[str]] = json.load(f)

with open(_DATA_DIR / "aliases.json", encoding="utf-8") as f:
    ALIASES: Dict[str, str] = json.load(f)

def _find_category_for(skill_name: str) -> str:
    """Find which category a canonical skill belongs to."""
    norm = normalize_skill(skill_name)
    for category, skills in SKILL_TAXONOMY.items():
        for s in skills:
            if normalize_skill(s) == norm:
                return category
    return "Tools"


# Build normalized skill → canonical name mapping
_SKILL_NORMALIZED: Dict[str, Tuple[str, str]] = {}  # normalized → (canonical, category)
for category, skills in SKILL_TAXONOMY.items():
    for skill in skills:
        norm = normalize_skill(skill)
        _SKILL_NORMALIZED[norm] = (skill, category)

# Also add aliases
for alias, canonical in ALIASES.items():
    norm_alias = normalize_skill(alias)
    _SKILL_NORMALIZED[norm_alias] = (canonical, _find_category_for(canonical))


def extract_skills(text: str) -> Tuple[List[ExtractedSkill], List[SkillCategory]]:
    """
    Extract skills from resume text.

    Returns:
        skills: list of ExtractedSkill with name, category, frequency, context
        categories: aggregated SkillCategory list
    """
    found: Dict[str, Dict] = {}  # canonical_name → {category, frequency, contexts}
    text_lower = text.lower()

    # Build sorted list of known skills (longer first to avoid partial matches)
    sorted_skills = sorted(_SKILL_NORMALIZED.keys(), key=len, reverse=True)

    for norm_skill in sorted_skills:
        canonical, category = _SKILL_NORMALIZED[norm_skill]

        # Use word-boundary-aware search
        pattern = _build_pattern(norm_skill)
        if not pattern:
            continue

        matches = list(re.finditer(pattern, text_lower))
        if matches:
            key = canonical
            if key not in found:
                found[key] = {
                    "canonical": canonical,
                    "category": category,
                    "frequency": 0,
                    "contexts": [],
                }
            found[key]["frequency"] += len(matches)
            # Collect context around first match
            if len(found[key]["contexts"]) < 2:
                m = matches[0]
                start = max(0, m.start() - 40)
                end = min(len(text), m.end() + 40)
                ctx = text[start:end].strip().replace("\n", " ")
                found[key]["contexts"].append(ctx)

    # Build output
    skills: List[ExtractedSkill] = []
    category_map: Dict[str, List[str]] = {}

    for data in found.values():
        context = data["contexts"][0] if data["contexts"] else None
        skills.append(ExtractedSkill(
            name=data["canonical"],
            normalized_name=normalize_skill(data["canonical"]),
            category=data["category"],
            frequency=data["frequency"],
            context=context,
        ))
        cat = data["category"]
        if cat not in category_map:
            category_map[cat] = []
        category_map[cat].append(data["canonical"])

    # Sort skills by frequency (desc) then name
    skills.sort(key=lambda s: (-s.frequency, s.name))

    # Build category summaries
    categories: List[SkillCategory] = [
        SkillCategory(category=cat, skills=skill_list, count=len(skill_list))
        for cat, skill_list in sorted(category_map.items())
    ]

    return skills, categories


def _build_pattern(norm_skill: str) -> str:
    """Build a regex pattern for skill matching with word boundaries."""
    # Escape special regex chars
    escaped = re.escape(norm_skill)
    # C++ and C# need special handling
    if norm_skill in ("c++", "c#"):
        return r"(?<!\w)" + escaped + r"(?!\w)"
    # For skills with dots (node.js, react.js) make dot optional
    escaped = escaped.replace(r"\.", r"\.?")
    # For skills with plus (c++) already escaped
    return r"(?<!\w)" + escaped + r"(?!\w)"


def normalize_skill_name(raw: str) -> str:
    """Public helper: normalize and look up canonical skill name."""
    norm = normalize_skill(raw)
    if norm in _SKILL_NORMALIZED:
        return _SKILL_NORMALIZED[norm][0]
    return raw.strip()


def get_skill_category(skill_name: str) -> str:
    """Get the category for a skill name."""
    norm = normalize_skill(skill_name)
    if norm in _SKILL_NORMALIZED:
        return _SKILL_NORMALIZED[norm][1]
    return "Other"


def all_known_skills() -> Set[str]:
    """Return all canonical skill names."""
    return {v[0] for v in _SKILL_NORMALIZED.values()}

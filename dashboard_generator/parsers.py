"""Lightweight parsers for resume text and job descriptions.

Pure-stdlib, no NLP libs. Good enough to drive matching and tailoring.
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

SECTION_HEADERS = {
    "summary": ["summary", "profile", "professional summary", "objective", "about"],
    "experience": ["experience", "work experience", "professional experience", "employment"],
    "projects": ["projects", "side projects", "personal projects", "selected projects"],
    "skills": ["skills", "technical skills", "tools", "tech stack", "core competencies"],
    "education": ["education", "academic", "studies"],
    "certifications": ["certifications", "certificates", "licenses"],
    "publications": ["publications", "papers", "patents"],
    "awards": ["awards", "achievements", "honors"],
    "contact": ["contact", "details", "header"],
}

# small curated stopword list — keep deps zero
_STOP = {
    "the", "and", "for", "with", "you", "your", "our", "are", "was", "were",
    "this", "that", "from", "have", "has", "will", "but", "not", "all", "any",
    "can", "may", "use", "uses", "used", "via", "into", "than", "then", "also",
    "their", "they", "them", "such", "more", "less", "very", "much", "every",
    "etc", "about", "across", "within", "between", "while", "what", "when",
    "who", "which", "where", "why", "how", "we", "us", "i", "in", "on", "of",
    "to", "a", "an", "is", "be", "by", "or", "as", "at", "it", "its", "if",
    "do", "does", "did", "doing", "should", "would", "could", "must",
    "team", "teams", "work", "works", "working", "role", "roles", "job",
    "company", "companies", "candidate", "opportunity", "position", "join",
    "ability", "experience", "experiences", "responsibilities", "duties",
    "preferred", "plus", "required", "minimum", "must-have", "nice", "have",
    "year", "years", "month", "months", "day", "days", "week", "weeks",
}


def load_resume_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8", errors="replace")


def parse_resume(text: str) -> dict[str, str]:
    """Split a resume into sections keyed by canonical name.

    Recognizes lines that look like section headers (uppercase, short, ending
    with ':' or surrounded by ---). Anything before the first detected header
    falls into 'contact'.
    """
    if not text.strip():
        return {}

    lines = text.splitlines()
    sections: dict[str, list[str]] = {"contact": []}
    current = "contact"

    for raw in lines:
        line = raw.rstrip()
        header = _detect_header(line)
        if header:
            current = header
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(raw)

    # drop empty sections + strip whitespace
    return {name: "\n".join(body).strip() for name, body in sections.items() if "".join(body).strip()}


def _detect_header(line: str) -> str | None:
    bare = line.strip().rstrip(":").lower()
    if not bare or len(bare) > 40:
        return None
    if re.match(r"^[-=]{3,}$", bare):
        return None
    for canonical, aliases in SECTION_HEADERS.items():
        if bare in aliases:
            return canonical
    # All-caps short header (e.g., "EXPERIENCE")
    if line.strip() and line.strip().isupper() and len(line.strip()) <= 40:
        for canonical, aliases in SECTION_HEADERS.items():
            if bare in aliases:
                return canonical
    return None


def extract_resume_skills(sections: dict[str, str]) -> list[str]:
    """Pull a flat skill list from the skills section, splitting on common separators."""
    block = sections.get("skills", "")
    if not block:
        return []
    parts = re.split(r"[\n,;|•·●▪▶/]+", block)
    skills: list[str] = []
    for p in parts:
        s = p.strip(" -–—:").strip()
        if not s or len(s) > 60:
            continue
        # strip leading category labels like "Languages:"
        s = re.sub(r"^[A-Za-z &/+]{1,30}:\s*", "", s)
        if s:
            skills.append(s)
    return skills


_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9+#./-]{1,}")


def extract_jd_keywords(jd_text: str, top_n: int = 40) -> list[str]:
    """Rank tokens and short phrases by frequency, biased toward proper nouns and tech terms."""
    if not jd_text.strip():
        return []

    tokens = [t for t in _WORD_RE.findall(jd_text) if not t.isdigit()]
    lower = [t.lower() for t in tokens]

    counts: Counter[str] = Counter()
    for token, low in zip(tokens, lower):
        if low in _STOP or len(low) <= 2:
            continue
        # Promote tokens that look like tech (caps, mixed-case, contain +#.)
        boost = 2 if (token[:1].isupper() or any(c in token for c in "+#.")) else 1
        counts[low] += boost

    bigrams: Counter[str] = Counter()
    for i in range(len(lower) - 1):
        a, b = lower[i], lower[i + 1]
        if a in _STOP or b in _STOP or len(a) <= 2 or len(b) <= 2:
            continue
        bigrams[f"{a} {b}"] += 1

    ranked: list[tuple[str, int]] = []
    ranked.extend(counts.most_common(top_n))
    ranked.extend([(p, c) for p, c in bigrams.most_common(top_n // 2) if c >= 2])

    seen: set[str] = set()
    out: list[str] = []
    for term, _c in ranked:
        if term in seen:
            continue
        seen.add(term)
        out.append(term)
    return out[:top_n]


def match_resume_to_jd(
    sections: dict[str, str],
    jd_keywords: list[str],
) -> dict:
    """Score how well the resume covers JD keywords. Returns matched/missing lists."""
    if not jd_keywords:
        return {"matched": [], "missing": [], "coverage": 0.0}
    flat = " ".join(sections.values()).lower()
    matched, missing = [], []
    for kw in jd_keywords:
        if kw in flat:
            matched.append(kw)
        else:
            missing.append(kw)
    coverage = len(matched) / max(1, len(jd_keywords))
    return {"matched": matched, "missing": missing, "coverage": round(coverage, 3)}


def split_bullets(block: str) -> list[str]:
    """Split a free-form text block into bullet-like lines."""
    bullets: list[str] = []
    for line in block.splitlines():
        s = line.strip()
        if not s:
            continue
        s = re.sub(r"^[-•·●▪▶*•]\s*", "", s)
        bullets.append(s)
    return bullets

"""Tailor a resume to a specific target and emit HTML + Markdown + cover letter."""
from __future__ import annotations

import html
import re
from pathlib import Path

from dashboard_generator.models import CandidateProfile, JobTarget
from dashboard_generator.parsers import (
    extract_resume_skills, match_resume_to_jd, split_bullets,
)

COMPANY_LENS_HINTS = {
    "amazon": "Lead with bullets that map to Leadership Principles (Customer Obsession, Ownership, Bias for Action, Deliver Results, Earn Trust). Use 'I' not 'we'.",
    "google": "Lead with scale + complexity + measurable impact. Show 'Googliness' via cross-team work; bullets should make the bar (L4) or above bar (L5) obvious.",
    "meta": "Lead with shipped impact, velocity, and metrics. Move-fast language ok; show end-to-end ownership.",
    "facebook": "Lead with shipped impact and metrics. End-to-end ownership.",
    "apple": "Emphasize hardware/software boundary, silicon/firmware/system experience, attention to craft, polish, and secrecy/judgment.",
    "netflix": "Lead with judgment, senior-only context, and high-impact decisions; deemphasize process work.",
    "microsoft": "Mix shipped impact with collaborative leadership and platform breadth; AI/Copilot work is currently valued.",
    "nvidia": "Lead with GPU/CUDA/accelerator validation, perf work, low-level systems, ML infra.",
    "openai": "Frontier-model evaluation, safety, agentic systems, model behavior debugging.",
    "anthropic": "Safety + capability + frontier evaluation. Bias toward applied research engineering.",
}


def build_resume_pair(
    profile: CandidateProfile,
    sections: dict[str, str],
    target: JobTarget,
    jd_keywords: list[str],
    out_dir: Path,
) -> list[Path]:
    """Build tailored resume (HTML + MD) and cover letter (HTML + MD) for a target.

    Returns list of written paths.
    """
    slug = _slugify(f"{target.company}-{target.level or target.role or 'role'}")
    tailored = _tailor_sections(sections, jd_keywords)
    match_info = match_resume_to_jd(sections, jd_keywords)
    lens_hint = _lens_hint(target)

    paths: list[Path] = []

    html_resume = _render_resume_html(profile, tailored, target, jd_keywords, match_info, lens_hint)
    p = out_dir / f"resume_{slug}.html"
    p.write_text(html_resume, encoding="utf-8")
    paths.append(p)

    md_resume = _render_resume_md(profile, tailored, target, jd_keywords, match_info, lens_hint)
    p = out_dir / f"resume_{slug}.md"
    p.write_text(md_resume, encoding="utf-8")
    paths.append(p)

    cover_html = _render_cover_html(profile, target, jd_keywords, lens_hint)
    p = out_dir / f"cover_{slug}.html"
    p.write_text(cover_html, encoding="utf-8")
    paths.append(p)

    cover_md = _render_cover_md(profile, target, jd_keywords, lens_hint)
    p = out_dir / f"cover_{slug}.md"
    p.write_text(cover_md, encoding="utf-8")
    paths.append(p)

    return paths


def _slugify(text: str) -> str:
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", text.strip().lower())
    return s.strip("-") or "target"


def _lens_hint(target: JobTarget) -> str:
    if target.lens:
        return target.lens
    key = (target.company or "").strip().lower()
    return COMPANY_LENS_HINTS.get(key, "")


def _tailor_sections(sections: dict[str, str], jd_keywords: list[str]) -> dict[str, list[str] | str]:
    """Reorder bullets in experience/projects to put keyword-rich ones first."""
    out: dict[str, list[str] | str] = {}
    kw_lower = [k.lower() for k in jd_keywords]

    for name, body in sections.items():
        if name in ("experience", "projects"):
            bullets = split_bullets(body)
            scored = sorted(
                bullets,
                key=lambda b: -_kw_score(b, kw_lower),
            )
            out[name] = scored
        elif name == "skills":
            skills = extract_resume_skills({name: body})
            scored = sorted(skills, key=lambda s: -_kw_score(s, kw_lower))
            out[name] = scored
        else:
            out[name] = body
    return out


def _kw_score(text: str, kws_lower: list[str]) -> int:
    t = text.lower()
    return sum(1 for k in kws_lower if k in t)


def _highlight(text: str, jd_keywords: list[str]) -> str:
    esc = html.escape(text)
    for kw in sorted(jd_keywords, key=len, reverse=True):
        if not kw or len(kw) < 3:
            continue
        pattern = re.compile(rf"(?i)\b{re.escape(kw)}\b")
        esc = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", esc)
    return esc


# ---------- renderers ----------
def _render_resume_html(
    profile: CandidateProfile,
    tailored: dict,
    target: JobTarget,
    jd_keywords: list[str],
    match_info: dict,
    lens_hint: str,
) -> str:
    name = html.escape(profile.name or "Your Name")
    contact_bits = [profile.email, profile.phone, profile.location, profile.linkedin, profile.github, profile.portfolio]
    contact = " • ".join(html.escape(b) for b in contact_bits if b)

    summary_block = tailored.get("summary") or ""
    summary_html = _highlight(summary_block, jd_keywords) if isinstance(summary_block, str) else ""

    exp_bullets = tailored.get("experience") or []
    proj_bullets = tailored.get("projects") or []
    skills = tailored.get("skills") or []
    education = tailored.get("education") or ""

    exp_html = "\n".join(f"<li>{_highlight(b, jd_keywords)}</li>" for b in exp_bullets) if isinstance(exp_bullets, list) else ""
    proj_html = "\n".join(f"<li>{_highlight(b, jd_keywords)}</li>" for b in proj_bullets) if isinstance(proj_bullets, list) else ""
    skills_html = ", ".join(_highlight(s, jd_keywords) for s in skills) if isinstance(skills, list) else ""
    education_html = _highlight(education, jd_keywords) if isinstance(education, str) else ""

    matched = ", ".join(match_info.get("matched", [])[:20]) or "—"
    missing = ", ".join(match_info.get("missing", [])[:20]) or "—"
    coverage = match_info.get("coverage", 0.0)

    target_line = " — ".join(filter(None, [target.company, target.role, target.level]))

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Resume — {name} — {html.escape(target.company or 'Target')}</title>
<style>
  :root {{
    --fg: #111; --muted: #555; --mark: #fff3a8; --rule: #d8d8d8; --accent: #1f6f43;
  }}
  body {{ font: 14px/1.45 -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: var(--fg); max-width: 900px; margin: 32px auto; padding: 0 24px; }}
  h1 {{ margin: 0; font-size: 26px; letter-spacing: 0.2px; }}
  .contact {{ color: var(--muted); font-size: 13px; margin-top: 4px; }}
  .target {{ font-size: 12px; color: var(--accent); margin-top: 4px; font-weight: 600; }}
  h2 {{ font-size: 13px; text-transform: uppercase; letter-spacing: 1px; color: var(--accent); border-bottom: 1px solid var(--rule); padding-bottom: 4px; margin-top: 24px; }}
  ul {{ padding-left: 22px; margin: 8px 0; }}
  li {{ margin: 4px 0; }}
  mark {{ background: var(--mark); padding: 0 2px; border-radius: 2px; }}
  .meta {{ background: #fafafa; border: 1px solid var(--rule); border-radius: 6px; padding: 12px 14px; margin-top: 24px; font-size: 12px; color: var(--muted); }}
  .meta strong {{ color: var(--fg); }}
  @media print {{ .meta {{ display: none; }} body {{ margin: 0; }} }}
</style>
</head>
<body>
  <h1>{name}</h1>
  <div class="contact">{contact}</div>
  <div class="target">Tailored for: {html.escape(target_line)}</div>

  <h2>Summary</h2>
  <p>{summary_html or '<em>(no summary section detected — add one in tab 2)</em>'}</p>

  <h2>Experience</h2>
  <ul>{exp_html or '<li><em>(no experience bullets detected)</em></li>'}</ul>

  <h2>Projects</h2>
  <ul>{proj_html or '<li><em>(no projects detected)</em></li>'}</ul>

  <h2>Skills</h2>
  <p>{skills_html or '<em>(no skills detected)</em>'}</p>

  <h2>Education</h2>
  <p>{education_html or '<em>(no education detected)</em>'}</p>

  <div class="meta">
    <div><strong>Keyword coverage:</strong> {coverage * 100:.1f}%</div>
    <div><strong>Matched:</strong> {html.escape(matched)}</div>
    <div><strong>Missing — consider weaving in if true:</strong> {html.escape(missing)}</div>
    <div><strong>Lens hint:</strong> {html.escape(lens_hint or '—')}</div>
  </div>
</body>
</html>
"""


def _render_resume_md(
    profile: CandidateProfile,
    tailored: dict,
    target: JobTarget,
    jd_keywords: list[str],
    match_info: dict,
    lens_hint: str,
) -> str:
    parts = []
    parts.append(f"# {profile.name or 'Your Name'}")
    contact_bits = [profile.email, profile.phone, profile.location, profile.linkedin, profile.github, profile.portfolio]
    contact = " • ".join(b for b in contact_bits if b)
    if contact:
        parts.append(contact)
    parts.append("")
    parts.append(f"_Tailored for: {target.company} — {target.role} {target.level}_")
    parts.append("")

    def section(title: str, body: str) -> None:
        parts.append(f"## {title}")
        parts.append(body.strip() or "_(none)_")
        parts.append("")

    if tailored.get("summary"):
        section("Summary", str(tailored["summary"]))
    if tailored.get("experience"):
        body = "\n".join(f"- {b}" for b in tailored["experience"])  # type: ignore[arg-type]
        section("Experience", body)
    if tailored.get("projects"):
        body = "\n".join(f"- {b}" for b in tailored["projects"])  # type: ignore[arg-type]
        section("Projects", body)
    if tailored.get("skills"):
        body = ", ".join(tailored["skills"])  # type: ignore[arg-type]
        section("Skills", body)
    if tailored.get("education"):
        section("Education", str(tailored["education"]))

    parts.append("---")
    parts.append(f"**Coverage:** {match_info.get('coverage', 0.0) * 100:.1f}%")
    parts.append(f"**Matched:** {', '.join(match_info.get('matched', [])[:20]) or '—'}")
    parts.append(f"**Missing:** {', '.join(match_info.get('missing', [])[:20]) or '—'}")
    if lens_hint:
        parts.append(f"**Lens:** {lens_hint}")
    return "\n".join(parts) + "\n"


def _render_cover_html(profile: CandidateProfile, target: JobTarget, jd_keywords: list[str], lens_hint: str) -> str:
    body = _cover_body(profile, target, jd_keywords, lens_hint)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Cover letter — {html.escape(profile.name or '')} → {html.escape(target.company or '')}</title>
<style>
  body {{ font: 14px/1.55 'IBM Plex Sans', -apple-system, system-ui, sans-serif; color: #111; max-width: 720px; margin: 32px auto; padding: 0 24px; }}
  h1 {{ font-size: 20px; margin-bottom: 6px; }}
  .meta {{ color: #555; font-size: 13px; margin-bottom: 24px; }}
  p {{ margin: 12px 0; }}
</style>
</head>
<body>
  <h1>{html.escape(profile.name or 'Your Name')}</h1>
  <div class="meta">{html.escape(profile.email or '')} • {html.escape(profile.phone or '')} • {html.escape(profile.location or '')}</div>
  {''.join(f'<p>{html.escape(p)}</p>' for p in body)}
</body>
</html>
"""


def _render_cover_md(profile: CandidateProfile, target: JobTarget, jd_keywords: list[str], lens_hint: str) -> str:
    body = _cover_body(profile, target, jd_keywords, lens_hint)
    head = [profile.name or "Your Name"]
    contact = " • ".join(b for b in [profile.email, profile.phone, profile.location] if b)
    if contact:
        head.append(contact)
    head.append("")
    return "\n".join(head + body) + "\n"


def _cover_body(profile: CandidateProfile, target: JobTarget, jd_keywords: list[str], lens_hint: str) -> list[str]:
    company = target.company or "your team"
    role = target.role or "the role"
    level = target.level or ""
    top_kws = ", ".join(jd_keywords[:5]) if jd_keywords else "the requirements you posted"

    paras: list[str] = []
    paras.append(
        f"Dear {company} hiring team,"
    )
    paras.append(
        f"I'm applying for {role} {level}. My background — {profile.years_experience or 'several'} years on "
        f"AI accelerator validation, SDET, and embedded systems — maps directly to {top_kws}. "
        f"I most recently {profile.current_status or 'invested in deepening systems and GenAI depth'}."
    )
    if lens_hint:
        paras.append(f"On {company}'s lens: {lens_hint}")
    paras.append(
        "Three concrete proof points I'd bring on day one: "
        "(1) silicon-grade test rigor applied to model evaluation pipelines; "
        "(2) end-to-end ownership shipping product-shaped features; "
        "(3) calm root-cause work on intermittent, cross-stack failures."
    )
    if target.notes:
        paras.append(f"Why {company} specifically: {target.notes}")
    paras.append(
        f"I'd welcome the chance to walk through the work. {profile.linkedin or ''} {profile.github or ''}".strip()
    )
    paras.append("Thank you for the read.")
    paras.append(profile.name or "—")
    return paras

"""Build the single-file dashboard.html from collected inputs + curated content.

Vanilla JS, light theme, localStorage-backed persistence, Google Fonts only.
"""
from __future__ import annotations

import html
import json
from datetime import date, datetime, timedelta

from dashboard_generator.content import (
    AUTOMATION_QUESTIONS, BEHAVIORAL_STORIES, COMPANY_GUIDES, DSA_PATTERNS,
    INDUSTRY_PROBLEMS, JOB_BOARDS_NOTE, PREP_STRATEGY, RESOURCES,
)
from dashboard_generator.models import (
    CandidateProfile, JobTarget, PlanConfig, ProjectSpec,
)


def build_dashboard(
    profile: CandidateProfile,
    plan: PlanConfig,
    project: ProjectSpec,
    targets: list[JobTarget],
    generated_at: datetime,
) -> str:
    sched = generate_schedule(plan)
    plan_json = json.dumps(_schedule_for_js(sched))
    dsa_json = json.dumps(DSA_PATTERNS)
    auto_json = json.dumps(AUTOMATION_QUESTIONS)

    company_guide = _pick_company_guide(profile.target_company)
    gen_str = generated_at.strftime("%Y-%m-%d %H:%M")

    body_sections = "\n".join([
        _section_plan(plan, sched),
        _section_dsa(),
        _section_mocks(),
        _section_resources(),
        _section_behavioral(profile),
        _section_prep_strategy(),
        _section_industry(),
        _section_company(company_guide, profile.target_company),
        _section_jobs(targets),
        _section_gaps(profile),
        _section_project(project, profile),
        _section_overview(profile, plan, targets),
    ])

    tabs = [
        ("plan", "My Plan + TODOs"),
        ("dsa", "DSA Bank"),
        ("mocks", "Mocks & Tests"),
        ("resources", "Resources"),
        ("behavioral", "Intro + Behavioral"),
        ("strategy", "Prep Strategy"),
        ("industry", "Industry Problems"),
        ("company", f"{profile.target_company or 'Company'} Guide"),
        ("jobs", "Jobs"),
        ("gaps", "Gaps + Focus"),
        ("project", "Side Project"),
        ("overview", "Overview"),
    ]
    tab_buttons = "\n".join(
        f'<button class="tab" data-tab="{tid}">{html.escape(label)}</button>'
        for tid, label in tabs
    )

    return _HTML_SKELETON.format(
        title=html.escape(f"{profile.name or 'You'} — MAANG Prep"),
        candidate_name=html.escape(profile.name or "(set your name in tab 1)"),
        target_line=html.escape(_target_line(profile)),
        comp_goal=html.escape(profile.comp_goal or "(set in profile)"),
        application_date=html.escape(profile.application_date or "(set in profile)"),
        days_left=_days_left_html(profile.application_date),
        tab_buttons=tab_buttons,
        body_sections=body_sections,
        plan_json=plan_json,
        dsa_json=dsa_json,
        auto_json=auto_json,
        generated_at=html.escape(gen_str),
    )


# ---------------- target line ----------------
def _target_line(p: CandidateProfile) -> str:
    bits = []
    if p.target_company:
        bits.append(p.target_company)
    if p.target_level:
        bits.append(p.target_level)
    if p.stretch_level and p.stretch_level != p.target_level:
        bits.append(f"stretch: {p.stretch_level}")
    return " · ".join(bits) or "(set target in profile)"


def _days_left_html(app_date: str) -> str:
    if not app_date:
        return "—"
    try:
        d = datetime.strptime(app_date, "%Y-%m-%d").date()
    except ValueError:
        return "—"
    delta = (d - date.today()).days
    return f"{delta} days"


def _pick_company_guide(name: str) -> dict:
    if not name:
        return COMPANY_GUIDES["Google"]
    key = name.strip()
    if key in COMPANY_GUIDES:
        return COMPANY_GUIDES[key]
    for k in COMPANY_GUIDES:
        if k.lower() == key.lower():
            return COMPANY_GUIDES[k]
    return COMPANY_GUIDES["Google"]


# ---------------- schedule ----------------
def generate_schedule(plan: PlanConfig) -> list[dict]:
    """Build day-by-day cards from plan.start_date through plan.end_date."""
    days: list[dict] = []
    cur = plan.start_date
    pattern_idx = 0
    phases_sorted = sorted(plan.phases) if plan.phases else []
    deadline_map = {d: l for d, l in plan.deadlines}

    while cur <= plan.end_date:
        phase = _phase_for(cur, phases_sorted)
        weekday = cur.weekday()  # 0=Mon
        tasks: list[dict] = []

        # Fixed health block
        if plan.swim_block:
            tasks.append({
                "track": "Health",
                "title": plan.swim_block,
                "subtasks": ["Show up.", "No phone in the water."],
            })

        # Coursework block (Tue/Thu/Sat) if configured
        if plan.coursework and weekday in (1, 3, 5):
            tasks.append({
                "track": "Coursework",
                "title": f"{plan.coursework} — 90 min focused block",
                "subtasks": [
                    "Open current module.",
                    "Take notes in your own words.",
                    "Submit the deliverable if due this week.",
                ],
            })

        # DSA block — choose pattern from rotation
        pat = DSA_PATTERNS[pattern_idx % len(DSA_PATTERNS)]
        pattern_idx += 1
        problems = pat.get("problems", [])[:3]
        blurb = pat['blurb']
        subs = [
            f'Read pattern blurb: "{blurb}"',
            *(f"{p['name']} (LC{p['lc']}, {p['diff']}) — solve cold, narrate aloud." for p in problems),
            "Redo yesterday's hardest problem from blank.",
            "Log time + struggle notes.",
        ]
        tasks.append({
            "track": "DSA",
            "title": f"DSA — {pat['name']}",
            "subtasks": subs,
        })

        # Phase-specific second block
        phase_l = (phase or "").lower()
        if "polish" in phase_l or "final" in phase_l:
            tasks.append({
                "track": "Mock",
                "title": "Timed mock — 45 min + 15 min review",
                "subtasks": [
                    "Pick from the Mocks tab (random DSA test).",
                    "No editorial mid-mock.",
                    "Write 3 lessons in your log.",
                ],
            })
        elif "build" in phase_l:
            tasks.append({
                "track": "Behavioral",
                "title": "Behavioral — rehearse 1 STAR story aloud",
                "subtasks": [
                    "Record yourself, listen back.",
                    "Trim to under 2 minutes.",
                    "Tag which round type it fits.",
                ],
            })
        else:
            tasks.append({
                "track": "Behavioral",
                "title": "Self-intro — say the 90-second pitch out loud, twice",
                "subtasks": ["Time it.", "Cut filler words."],
            })

        # Apply day: every Sunday in build-up + polish phases
        if weekday == 6 and ("build" in phase_l or "polish" in phase_l or "final" in phase_l):
            tasks.append({
                "track": "Apply",
                "title": "Apply — 1 target end-to-end",
                "subtasks": [
                    "Pick the highest-fit target from the Jobs tab.",
                    "Tailor the resume from the generated draft.",
                    "Customize the cover letter (one paragraph from scratch).",
                    "Reach out to a real human (LinkedIn, ex-colleague).",
                ],
            })

        # Side project: capped per-week
        if weekday == 5:  # Saturday
            tasks.append({
                "track": "Portfolio",
                "title": f"Side project — capped at {int(plan.side_project_cap_pct)}% of prep time",
                "subtasks": [
                    "Ship the smallest visible improvement.",
                    "Commit + push.",
                    "Update README.",
                ],
            })

        # Buffer / catch-up
        tasks.append({
            "track": "Buffer",
            "title": "Buffer — review yesterday's notes, then rest",
            "subtasks": ["What worked.", "What stuck.", "What to redo tomorrow."],
        })

        day = {
            "date": cur.isoformat(),
            "weekday": cur.strftime("%a"),
            "phase": phase,
            "deadline": deadline_map.get(cur, ""),
            "tasks": tasks,
        }
        days.append(day)
        cur += timedelta(days=1)

    return days


def _phase_for(d: date, phases: list[tuple[date, str]]) -> str:
    label = ""
    for ph_date, ph_label in phases:
        if d >= ph_date:
            label = ph_label
    return label


def _schedule_for_js(sched: list[dict]) -> list[dict]:
    """Pass through; already JSON-friendly."""
    return sched


# ---------------- sections ----------------
def _section_plan(plan: PlanConfig, sched: list[dict]) -> str:
    deadline_rows = "".join(
        f"<tr><td>{html.escape(d.isoformat())}</td><td>{html.escape(label)}</td></tr>"
        for d, label in sorted(plan.deadlines)
    ) or "<tr><td colspan='2' class='muted'>No deadlines added.</td></tr>"

    phase_rows = "".join(
        f"<tr><td>{html.escape(d.isoformat())}</td><td>{html.escape(label)}</td></tr>"
        for d, label in sorted(plan.phases)
    ) or "<tr><td colspan='2' class='muted'>No phases configured.</td></tr>"

    return f"""
<section id="tab-plan" class="panel">
  <div class="sticky-progress">
    <div class="progress-row">
      <div class="progress-bar"><div id="planProgressFill"></div></div>
      <div class="progress-meta">
        <span id="planProgressText">0 / 0</span>
        <button id="planResetBtn" class="ghost">Reset all checks</button>
      </div>
    </div>
  </div>

  <div class="cards">
    <div class="card">
      <h3>Why this plan</h3>
      <p>{_intro_paragraph(plan)}</p>
    </div>
    <div class="card">
      <h3>Hard external deadlines</h3>
      <table class="kv"><tbody>{deadline_rows}</tbody></table>
    </div>
    <div class="card">
      <h3>Phases</h3>
      <table class="kv"><tbody>{phase_rows}</tbody></table>
    </div>
  </div>

  <h2 class="section-title">Day-by-day</h2>
  <div id="planDays"></div>
</section>
"""


def _intro_paragraph(plan: PlanConfig) -> str:
    days = (plan.end_date - plan.start_date).days + 1
    return html.escape(
        f"{days} days from {plan.start_date.isoformat()} to {plan.end_date.isoformat()}, "
        f"~{plan.hours_per_day:.1f} focused hours/day, side project capped at "
        f"{plan.side_project_cap_pct:.0f}% of prep time. Health block is fixed and non-negotiable. "
        f"DSA rotates through patterns; mocks and apply blocks ramp up by phase."
    )


def _section_dsa() -> str:
    return """
<section id="tab-dsa" class="panel">
  <div class="toolbar">
    <input type="search" id="dsaSearch" placeholder="Filter by problem name, LC number, or pattern…" />
    <span class="muted small" id="dsaCount"></span>
  </div>
  <div id="dsaBank"></div>
</section>
"""


def _section_mocks() -> str:
    return """
<section id="tab-mocks" class="panel">

  <div class="card">
    <h3>Randomized DSA test</h3>
    <div class="toolbar">
      <label>Problems: <input type="number" id="dsaTestN" min="1" max="20" value="3"/></label>
      <label>Minutes/problem: <input type="number" id="dsaTestMin" min="5" max="120" value="25"/></label>
      <button id="dsaTestStart" class="primary">Generate test</button>
      <span id="dsaTestTimer" class="timer"></span>
    </div>
    <div id="dsaTestArea"></div>
  </div>

  <div class="card">
    <h3>Randomized Automation/SDET test</h3>
    <div class="toolbar">
      <label>Questions: <input type="number" id="autoTestN" min="1" max="18" value="3"/></label>
      <button id="autoTestStart" class="primary">Generate</button>
    </div>
    <div id="autoTestArea"></div>
  </div>

  <div class="card">
    <h3>Guided mock rounds</h3>
    <p class="muted small">Type your answer, submit, then self-score 1–5 against the rubric and the follow-up.</p>
    <div id="guidedMockArea"></div>
  </div>

</section>
"""


def _section_resources() -> str:
    cards = []
    for group, items in RESOURCES.items():
        rows = "".join(
            f'<li><a href="{html.escape(it["url"])}" target="_blank" rel="noopener">{html.escape(it["name"])}</a>'
            f' — <span class="muted">{html.escape(it["why"])}</span></li>'
            for it in items
        )
        cards.append(f"""
<div class="card">
  <h3>{html.escape(group)}</h3>
  <ul class="resources">{rows}</ul>
</div>
""")
    return f"""
<section id="tab-resources" class="panel">
  <div class="cards">{''.join(cards)}</div>
</section>
"""


def _section_behavioral(profile: CandidateProfile) -> str:
    intro = profile.intro_draft.strip() or _default_intro(profile)
    story_cards = "".join(
        f"""
<div class="card story">
  <h3>{html.escape(s['title'])}</h3>
  <p><span class="pill s">S</span> {html.escape(s['s'])}</p>
  <p><span class="pill t">T</span> {html.escape(s['t'])}</p>
  <p><span class="pill a">A</span> {html.escape(s['a'])}</p>
  <p><span class="pill r">R</span> {html.escape(s['r'])}</p>
  <p class="muted small"><strong>Why it lands:</strong> {html.escape(s['why'])}</p>
</div>
"""
        for s in BEHAVIORAL_STORIES
    )
    return f"""
<section id="tab-behavioral" class="panel">
  <div class="card">
    <h3>90-second self-intro</h3>
    <p>{html.escape(intro)}</p>
    <p class="muted small">Time yourself. Trim until it lands in 90 seconds with breathing room.</p>
  </div>
  <h2 class="section-title">STAR stories</h2>
  <div class="cards">{story_cards}</div>
</section>
"""


def _default_intro(p: CandidateProfile) -> str:
    name = p.name or "I"
    yrs = p.years_experience or "~7"
    target = p.target_company or "your team"
    return (
        f"I'm {name}. Background: about {yrs} years on AI accelerator validation and SDET, "
        f"with embedded/ADAS roots before that. I recently stepped out of a full-time role to ship two "
        f"side projects and finish a postgrad in Generative & Agentic AI — a deliberate "
        f"validation-to-generative pivot, not a gap. What I'd bring to {target}: silicon-grade test rigor "
        f"applied to LLM evaluation, end-to-end ownership shipping AI features, and calm root-cause work "
        f"on intermittent, cross-stack failures. I'm targeting roles that sit on the model-systems-product "
        f"boundary, which is where I've been most useful and want to keep growing."
    )


def _section_prep_strategy() -> str:
    pat_rows = "".join(
        f"<tr><td>{html.escape(trigger)}</td><td>{html.escape(algo)}</td></tr>"
        for trigger, algo in PREP_STRATEGY["patterns"]
    )
    retention = "".join(f"<li>{html.escape(x)}</li>" for x in PREP_STRATEGY["retention"])
    in_room = "".join(f"<li>{html.escape(x)}</li>" for x in PREP_STRATEGY["in_room_algo"])
    return f"""
<section id="tab-strategy" class="panel">
  <div class="card">
    <h3>Pattern triggers (phrase → algorithm)</h3>
    <table class="kv">
      <thead><tr><th>If the prompt sounds like…</th><th>Reach for…</th></tr></thead>
      <tbody>{pat_rows}</tbody>
    </table>
  </div>
  <div class="cards">
    <div class="card"><h3>Retention method</h3><ul>{retention}</ul></div>
    <div class="card"><h3>In-room algorithm</h3><ol>{in_room}</ol></div>
  </div>
</section>
"""


def _section_industry() -> str:
    cards = []
    for it in INDUSTRY_PROBLEMS:
        cards.append(f"""
<div class="card collapsible">
  <div class="card-header" data-toggle>
    <h3>{html.escape(it['name'])}</h3>
    <span class="chev">▾</span>
  </div>
  <div class="card-body hidden">
    <p>{html.escape(it['blurb'])}</p>
    <pre class="code"><code></code></pre>
  </div>
  <script type="application/x-code">{html.escape(it['code'])}</script>
</div>
""")
    return f"""
<section id="tab-industry" class="panel">
  <p class="muted">Applied problems that bridge silicon/SDET/GenAI work into coding credibility. Each has tested code.</p>
  <div class="cards">{''.join(cards)}</div>
</section>
"""


def _section_company(guide: dict, target_company: str) -> str:
    process_items = "".join(f"<li>{html.escape(x)}</li>" for x in guide.get("process", []))
    round_rows = "".join(
        f"<tr><td>{html.escape(name)}</td><td>{html.escape(detail)}</td></tr>"
        for name, detail in guide.get("rounds_score", [])
    )
    real_items = "".join(f"<li>{html.escape(x)}</li>" for x in guide.get("real_questions", []))
    notes = guide.get("notes", "")
    bar = guide.get("level_bar", "")
    title = html.escape(target_company or "Target company")
    return f"""
<section id="tab-company" class="panel">
  <div class="card">
    <h3>{title} — hiring process</h3>
    <ol>{process_items}</ol>
    {('<p class="muted small">' + html.escape(notes) + '</p>') if notes else ''}
  </div>
  <div class="cards">
    <div class="card">
      <h3>What each round scores</h3>
      <table class="kv"><tbody>{round_rows}</tbody></table>
    </div>
    <div class="card">
      <h3>Level bar</h3>
      <p>{html.escape(bar)}</p>
    </div>
  </div>
  <div class="card">
    <h3>Real, recent candidate-reported questions</h3>
    <ul>{real_items}</ul>
    <p class="muted small">Verify against the company's current 'how we hire' page — process shifts. Last updated by you, in this dashboard.</p>
  </div>
</section>
"""


def _section_jobs(targets: list[JobTarget]) -> str:
    if not targets:
        rows = "<tr><td colspan='5' class='muted'>No targets added — fill in tab 3 of the generator.</td></tr>"
    else:
        parts = []
        for t in targets:
            jd_cell = (
                f'<a target="_blank" rel="noopener" href="{html.escape(t.url)}">JD</a>'
                if t.url else "—"
            )
            parts.append(
                "<tr>"
                f"<td>{html.escape(t.company)}</td>"
                f"<td>{html.escape(t.role)} {html.escape(t.level)}</td>"
                f"<td>{html.escape(t.comp_range or '—')}</td>"
                f"<td>{html.escape(t.notes or '—')}</td>"
                f"<td>{jd_cell}</td>"
                "</tr>"
            )
        rows = "".join(parts)
    return f"""
<section id="tab-jobs" class="panel">
  <div class="card">
    <h3>Target companies</h3>
    <table class="kv">
      <thead><tr><th>Company</th><th>Role / Level</th><th>Comp range</th><th>Why this fits</th><th>JD</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <p class="muted small">{html.escape(JOB_BOARDS_NOTE)}</p>
  </div>
</section>
"""


def _section_gaps(profile: CandidateProfile) -> str:
    weak = profile.weak_spots or ["Interview DSA fluency", "Live system design", "Behavioral story bench"]
    rows = []
    for i, w in enumerate(weak, 1):
        rows.append(f"<tr><td>{i}</td><td>{html.escape(w)}</td><td>{html.escape(_default_fix(w))}</td></tr>")
    body = "".join(rows) or "<tr><td colspan='3' class='muted'>No gaps listed in profile.</td></tr>"

    alloc_rows = "".join(
        f"<tr><td>{html.escape(area)}</td><td>{pct}%</td></tr>"
        for area, pct in [
            ("DSA practice + mocks", 45),
            ("System design + industry problems", 20),
            ("Behavioral + intro rehearsal", 10),
            ("Coursework", 15),
            ("Capped side project", 10),
        ]
    )

    return f"""
<section id="tab-gaps" class="panel">
  <div class="card">
    <h3>Gaps ranked by hiring impact</h3>
    <table class="kv">
      <thead><tr><th>#</th><th>Gap</th><th>Concrete fix</th></tr></thead>
      <tbody>{body}</tbody>
    </table>
  </div>
  <div class="card">
    <h3>Time allocation</h3>
    <table class="kv">
      <thead><tr><th>Area</th><th>Share of focused hours</th></tr></thead>
      <tbody>{alloc_rows}</tbody>
    </table>
    <p class="muted small">Tune as you go. The only number to protect is mocks: when in doubt, do another mock.</p>
  </div>
</section>
"""


def _default_fix(weak: str) -> str:
    low = weak.lower()
    if "dsa" in low or "data structure" in low or "leetcode" in low:
        return "Daily pattern rotation + 2 mocks/week. Stick to ~25 min/problem; 25-min stuck rule. Redo failed problems 24h later from blank."
    if "system" in low or "design" in low:
        return "One design problem per week, narrated. Use the 6-step framework: clarify → estimate → API → data model → high-level → deep-dive."
    if "behavioral" in low or "intro" in low or "story" in low:
        return "Memorize 7 STAR stories cold. Rehearse aloud, time them. Tag each to round types and company values."
    return "Pick the smallest unit you can practice daily; instrument it; measure weekly."


def _section_project(project: ProjectSpec, profile: CandidateProfile) -> str:
    bullets = "".join(f"<li>{html.escape(x)}</li>" for x in (project.readme_outline or []))
    repo_cell = (
        f'<a target="_blank" rel="noopener" href="{html.escape(project.repo)}">{html.escape(project.repo)}</a>'
        if project.repo else "—"
    )
    return f"""
<section id="tab-project" class="panel">
  <div class="card">
    <h3>Side project: portfolio + behavioral + design</h3>
    <table class="kv"><tbody>
      <tr><td>Name</td><td>{html.escape(project.name or '—')}</td></tr>
      <tr><td>Pitch</td><td>{html.escape(project.one_liner or '—')}</td></tr>
      <tr><td>Repo</td><td>{repo_cell}</td></tr>
      <tr><td>AI feature shipped</td><td>{html.escape(project.ai_feature or '—')}</td></tr>
      <tr><td>System-design narrative</td><td>{html.escape(project.design_doc or '—')}</td></tr>
    </tbody></table>
  </div>
  <div class="cards">
    <div class="card">
      <h3>README outline</h3>
      <ul>{bullets or '<li class="muted">Add bullets in the generator (tab 5).</li>'}</ul>
    </div>
    <div class="card">
      <h3>How this leverages</h3>
      <ul>
        <li>Behavioral: this is your 'owned end-to-end' story.</li>
        <li>System design: walk through your real architecture as the worked example.</li>
        <li>Portfolio: public repo + README + one shipped AI feature beats a fancy site.</li>
        <li>Cap: {profile.target_level or 'whatever the target level is'} won't be won on side-project polish — keep it &lt;= 10% of prep.</li>
      </ul>
    </div>
  </div>
</section>
"""


def _section_overview(profile: CandidateProfile, plan: PlanConfig, targets: list[JobTarget]) -> str:
    return f"""
<section id="tab-overview" class="panel">
  <div class="card">
    <h3>How to use this dashboard</h3>
    <ol>
      <li>Start on <strong>My Plan</strong> every morning. Check off subtasks as you go — your progress persists.</li>
      <li>When you hit a DSA block, jump to <strong>DSA Bank</strong>, filter by the day's pattern, solve cold.</li>
      <li>Once a week, run a <strong>Mocks &amp; Tests</strong> session — timed, no peeking.</li>
      <li>Before any interview, re-read <strong>Intro + Behavioral</strong> and <strong>{html.escape(profile.target_company or 'Company')} Guide</strong>.</li>
      <li>Apply blocks live in <strong>Jobs</strong> — your targets, with comp.</li>
    </ol>
  </div>
  <div class="card">
    <h3>Comp math (sanity check the goal)</h3>
    <p>Goal: {html.escape(profile.comp_goal or '(set)')} total comp. Targets:</p>
    <ul>
      {''.join(f'<li>{html.escape(t.company)} {html.escape(t.level)} — {html.escape(t.comp_range or "no range entered")}</li>' for t in targets) or '<li class="muted">No targets added.</li>'}
    </ul>
    <p class="muted small">Verify against <a target="_blank" rel="noopener" href="https://www.levels.fyi/">Levels.fyi</a> — ranges shift; negotiation window varies by team and recruiter.</p>
  </div>
</section>
"""


# ---------------- HTML skeleton ----------------
_HTML_SKELETON = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #f7f7f6;
    --card: #ffffff;
    --header: #f0efec;
    --rule: #e2e1dd;
    --fg: #161616;
    --muted: #6b6b6b;
    --accent: #1f6f43;
    --accent-soft: #e6f1ec;
    --warn: #b06d00;
    --warn-soft: #fbf1de;
    --crit: #a52a2a;
    --crit-soft: #f7e1e1;
    --info: #2154a8;
    --info-soft: #e3ecf9;
    --gold: #8a6b00;
    --gold-soft: #faf2d6;
    --mark: #fff3a8;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; background: var(--bg); color: var(--fg); }}
  body {{ font-family: 'IBM Plex Sans', system-ui, -apple-system, sans-serif; font-size: 14px; line-height: 1.5; }}
  code, pre, .mono {{ font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace; }}

  header.top {{
    background: var(--header); border-bottom: 1px solid var(--rule);
    padding: 18px 22px;
  }}
  header.top h1 {{ margin: 0; font-family: 'JetBrains Mono'; font-size: 18px; letter-spacing: 0.5px; }}
  header.top .meta {{ color: var(--muted); font-size: 12px; margin-top: 4px; font-family: 'JetBrains Mono'; }}
  header.top .meta strong {{ color: var(--fg); }}

  nav.tabs {{
    display: flex; flex-wrap: wrap; gap: 4px;
    padding: 8px 18px; background: var(--card); border-bottom: 1px solid var(--rule);
    position: sticky; top: 0; z-index: 10;
  }}
  nav.tabs .tab {{
    border: 1px solid transparent; background: transparent; color: var(--fg);
    padding: 6px 12px; cursor: pointer; border-radius: 6px; font-family: 'JetBrains Mono'; font-size: 12px;
  }}
  nav.tabs .tab:hover {{ background: var(--accent-soft); }}
  nav.tabs .tab.active {{ background: var(--accent); color: #fff; }}

  main {{ padding: 18px 22px 60px; max-width: 1320px; margin: 0 auto; }}
  .panel {{ display: none; }}
  .panel.active {{ display: block; }}

  h2.section-title {{ font-family: 'JetBrains Mono'; font-size: 14px; letter-spacing: 0.8px; text-transform: uppercase; color: var(--muted); margin: 22px 0 8px; }}
  h3 {{ font-family: 'JetBrains Mono'; font-size: 14px; margin: 0 0 8px; letter-spacing: 0.3px; }}
  .muted {{ color: var(--muted); }}
  .small {{ font-size: 12px; }}
  a {{ color: var(--accent); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}

  .cards {{ display: grid; gap: 14px; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); margin-top: 8px; }}
  .card {{ background: var(--card); border: 1px solid var(--rule); border-radius: 10px; padding: 14px 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.03); }}
  .card.collapsible .card-header {{ display: flex; justify-content: space-between; align-items: center; cursor: pointer; }}
  .card.collapsible .card-body.hidden {{ display: none; }}
  .chev {{ font-family: 'JetBrains Mono'; color: var(--muted); }}

  table.kv {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  table.kv th, table.kv td {{ text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--rule); vertical-align: top; }}
  table.kv th {{ font-family: 'JetBrains Mono'; font-size: 11px; text-transform: uppercase; letter-spacing: 0.6px; color: var(--muted); }}

  .toolbar {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin: 8px 0 14px; }}
  .toolbar input[type="search"], .toolbar input[type="number"] {{
    font: inherit; padding: 6px 10px; border: 1px solid var(--rule); border-radius: 6px; background: #fff;
  }}
  .toolbar input[type="search"] {{ flex: 1; min-width: 240px; }}

  button {{ font: inherit; cursor: pointer; padding: 6px 12px; border: 1px solid var(--rule); border-radius: 6px; background: #fff; color: var(--fg); font-family: 'JetBrains Mono'; font-size: 12px; }}
  button.primary {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
  button.primary:hover {{ filter: brightness(0.95); }}
  button.ghost {{ background: transparent; border-color: var(--rule); color: var(--muted); }}
  .timer {{ font-family: 'JetBrains Mono'; color: var(--crit); font-weight: 600; }}

  /* Plan */
  .sticky-progress {{ position: sticky; top: 42px; background: var(--card); border: 1px solid var(--rule); border-radius: 10px; padding: 10px 14px; z-index: 5; margin-bottom: 12px; }}
  .progress-row {{ display: flex; align-items: center; gap: 12px; }}
  .progress-bar {{ flex: 1; background: var(--header); border: 1px solid var(--rule); border-radius: 6px; height: 14px; overflow: hidden; }}
  .progress-bar > div {{ height: 100%; background: var(--accent); width: 0%; transition: width 0.2s ease; }}
  .progress-meta {{ display: flex; align-items: center; gap: 10px; font-family: 'JetBrains Mono'; font-size: 12px; color: var(--muted); }}

  .day-card {{ background: var(--card); border: 1px solid var(--rule); border-radius: 10px; padding: 14px 16px; margin-bottom: 12px; }}
  .day-header {{ display: flex; justify-content: space-between; align-items: baseline; gap: 8px; flex-wrap: wrap; margin-bottom: 8px; }}
  .day-date {{ font-family: 'JetBrains Mono'; font-size: 13px; letter-spacing: 0.4px; }}
  .day-phase {{ font-family: 'JetBrains Mono'; font-size: 11px; color: var(--muted); background: var(--header); padding: 2px 8px; border-radius: 12px; }}
  .day-deadline {{ font-family: 'JetBrains Mono'; font-size: 11px; color: var(--crit); background: var(--crit-soft); padding: 2px 8px; border-radius: 12px; }}

  .task {{ border-top: 1px solid var(--rule); padding: 8px 0; }}
  .task:first-child {{ border-top: 0; }}
  .task-head {{ display: flex; align-items: center; gap: 8px; cursor: pointer; }}
  .task-chev {{ font-family: 'JetBrains Mono'; color: var(--muted); width: 14px; }}
  .task-title {{ flex: 1; font-weight: 500; }}
  .task-count {{ font-family: 'JetBrains Mono'; font-size: 11px; color: var(--muted); background: var(--header); padding: 2px 8px; border-radius: 12px; }}
  .task-count.done {{ color: var(--accent); background: var(--accent-soft); }}
  .track {{ font-family: 'JetBrains Mono'; font-size: 10px; padding: 2px 8px; border-radius: 12px; text-transform: uppercase; letter-spacing: 0.6px; }}
  .track.Health {{ background: var(--info-soft); color: var(--info); }}
  .track.Coursework {{ background: var(--gold-soft); color: var(--gold); }}
  .track.DSA {{ background: var(--accent-soft); color: var(--accent); }}
  .track.Apply {{ background: var(--crit-soft); color: var(--crit); }}
  .track.Behavioral {{ background: var(--header); color: var(--fg); }}
  .track.Mock {{ background: var(--warn-soft); color: var(--warn); }}
  .track.Portfolio {{ background: var(--gold-soft); color: var(--gold); }}
  .track.Buffer {{ background: var(--header); color: var(--muted); }}

  .subtasks {{ list-style: none; padding-left: 22px; margin: 6px 0 0; }}
  .subtasks.hidden {{ display: none; }}
  .subtasks li {{ padding: 3px 0; display: flex; align-items: flex-start; gap: 8px; }}
  .subtasks input[type="checkbox"] {{ margin-top: 4px; }}
  .subtasks label.done {{ color: var(--muted); text-decoration: line-through; }}

  /* DSA */
  .pattern {{ background: var(--card); border: 1px solid var(--rule); border-radius: 10px; margin-bottom: 12px; }}
  .pattern-header {{ display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; cursor: pointer; }}
  .pattern.starred .pattern-header h3::before {{ content: '★ '; color: var(--gold); }}
  .pattern-blurb {{ color: var(--muted); font-size: 12px; padding: 0 16px 8px; }}
  .pattern-body {{ padding: 0 16px 12px; }}
  .pattern-body.hidden {{ display: none; }}
  .problem {{ border-top: 1px solid var(--rule); padding: 10px 0; }}
  .problem-head {{ display: flex; align-items: center; gap: 10px; cursor: pointer; }}
  .problem-name {{ flex: 1; font-weight: 500; }}
  .diff {{ font-family: 'JetBrains Mono'; font-size: 10px; padding: 2px 7px; border-radius: 12px; }}
  .diff.Easy {{ background: var(--accent-soft); color: var(--accent); }}
  .diff.Medium {{ background: var(--warn-soft); color: var(--warn); }}
  .diff.Hard {{ background: var(--crit-soft); color: var(--crit); }}
  .problem-body {{ margin-top: 8px; }}
  .problem-body.hidden {{ display: none; }}

  pre.code {{ background: #0f1116; color: #e8e8e8; border-radius: 8px; padding: 12px 14px; overflow: auto; font-size: 12px; line-height: 1.45; }}
  pre.code code {{ color: inherit; background: transparent; }}

  .complexity {{ font-family: 'JetBrains Mono'; font-size: 11px; color: var(--muted); margin-top: 6px; }}

  /* Behavioral */
  .pill {{ font-family: 'JetBrains Mono'; font-size: 10px; padding: 2px 6px; border-radius: 12px; margin-right: 6px; }}
  .pill.s {{ background: var(--info-soft); color: var(--info); }}
  .pill.t {{ background: var(--warn-soft); color: var(--warn); }}
  .pill.a {{ background: var(--accent-soft); color: var(--accent); }}
  .pill.r {{ background: var(--gold-soft); color: var(--gold); }}

  /* Resources */
  ul.resources {{ padding-left: 18px; }}
  ul.resources li {{ margin: 4px 0; }}

  /* Mocks scoring */
  .mock-q {{ border-top: 1px solid var(--rule); padding: 10px 0; }}
  .mock-q:first-child {{ border-top: 0; }}
  .mock-q textarea {{ width: 100%; min-height: 80px; font: inherit; padding: 8px; border: 1px solid var(--rule); border-radius: 6px; font-family: 'JetBrains Mono'; font-size: 12px; }}
  .mock-controls {{ display: flex; gap: 8px; align-items: center; margin-top: 6px; flex-wrap: wrap; }}
  .mock-score {{ font-family: 'JetBrains Mono'; font-size: 11px; color: var(--muted); }}

  footer {{ text-align: center; color: var(--muted); font-size: 11px; padding: 22px; border-top: 1px solid var(--rule); background: var(--card); }}

  mark {{ background: var(--mark); padding: 0 2px; border-radius: 2px; }}

  @media (max-width: 720px) {{
    main {{ padding: 12px 12px 40px; }}
    .cards {{ grid-template-columns: 1fr; }}
    nav.tabs {{ overflow-x: auto; flex-wrap: nowrap; }}
  }}
</style>
</head>
<body>
<header class="top">
  <h1>{candidate_name} — MAANG interview prep</h1>
  <div class="meta">
    target: <strong>{target_line}</strong> &nbsp;·&nbsp;
    comp goal: <strong>{comp_goal}</strong> &nbsp;·&nbsp;
    apply by: <strong>{application_date}</strong> &nbsp;·&nbsp;
    days left: <strong>{days_left}</strong>
  </div>
</header>

<nav class="tabs" id="tabs">
{tab_buttons}
</nav>

<main>
{body_sections}
</main>

<footer>
  Generated {generated_at} ·
  Sources: NeetCode, Striver/takeUforward, LeetCode, Levels.fyi, official company "how we hire" pages.
  Comp ranges vary by team, location, negotiation. Process details change — re-verify before each loop.
</footer>

<script>
const PLAN_DATA = {plan_json};
const DSA_DATA = {dsa_json};
const AUTO_DATA = {auto_json};

const LS = {{
  get(k, fallback) {{
    try {{ const v = localStorage.getItem(k); return v == null ? fallback : JSON.parse(v); }}
    catch (e) {{ return fallback; }}
  }},
  set(k, v) {{
    try {{ localStorage.setItem(k, JSON.stringify(v)); }} catch (e) {{}}
  }},
  del(k) {{
    try {{ localStorage.removeItem(k); }} catch (e) {{}}
  }},
}};

// ----- Tabs -----
const tabs = document.querySelectorAll('nav.tabs .tab');
const panels = document.querySelectorAll('.panel');
function showTab(id) {{
  tabs.forEach(t => t.classList.toggle('active', t.dataset.tab === id));
  panels.forEach(p => p.classList.toggle('active', p.id === 'tab-' + id));
  LS.set('lastTab', id);
  window.scrollTo({{top: 0, behavior: 'instant'}});
}}
tabs.forEach(t => t.addEventListener('click', () => showTab(t.dataset.tab)));
showTab(LS.get('lastTab', 'plan'));

// ----- Plan -----
const planRoot = document.getElementById('planDays');
const planChecks = LS.get('planChecks', {{}});
const planOpen = LS.get('planOpen', {{}});

function renderPlan() {{
  planRoot.innerHTML = '';
  PLAN_DATA.forEach((day, di) => {{
    const dayEl = document.createElement('div');
    dayEl.className = 'day-card';
    const phaseHtml = day.phase ? '<span class="day-phase">' + escapeHtml(day.phase) + '</span>' : '';
    const deadlineHtml = day.deadline ? '<span class="day-deadline">⚠ ' + escapeHtml(day.deadline) + '</span>' : '';
    dayEl.innerHTML = '<div class="day-header"><span class="day-date">' + day.date + ' · ' + day.weekday + '</span>' + phaseHtml + deadlineHtml + '</div>';
    day.tasks.forEach((task, ti) => {{
      const tid = 'd' + di + '_t' + ti;
      const openKey = tid;
      const open = planOpen[openKey] !== false; // default open
      const taskEl = document.createElement('div');
      taskEl.className = 'task';
      let done = 0, total = task.subtasks.length;
      task.subtasks.forEach((_, si) => {{
        if (planChecks[tid + '_s' + si]) done++;
      }});
      const countCls = (done === total && total > 0) ? 'task-count done' : 'task-count';
      taskEl.innerHTML =
        '<div class="task-head" data-toggle>' +
          '<span class="task-chev">' + (open ? '▾' : '▸') + '</span>' +
          '<span class="track ' + task.track + '">' + task.track + '</span>' +
          '<span class="task-title">' + escapeHtml(task.title) + '</span>' +
          '<span class="' + countCls + '">' + done + '/' + total + '</span>' +
        '</div>' +
        '<ul class="subtasks ' + (open ? '' : 'hidden') + '">' +
          task.subtasks.map((s, si) => {{
            const skey = tid + '_s' + si;
            const checked = planChecks[skey] ? 'checked' : '';
            const doneCls = planChecks[skey] ? 'done' : '';
            return '<li><input type="checkbox" data-sub="' + skey + '" ' + checked + ' id="' + skey + '">' +
                   '<label for="' + skey + '" class="' + doneCls + '">' + escapeHtml(s) + '</label></li>';
          }}).join('') +
        '</ul>';
      taskEl.querySelector('.task-head').addEventListener('click', (e) => {{
        if (e.target.tagName === 'INPUT') return;
        const ul = taskEl.querySelector('.subtasks');
        ul.classList.toggle('hidden');
        const chev = taskEl.querySelector('.task-chev');
        const nowOpen = !ul.classList.contains('hidden');
        chev.textContent = nowOpen ? '▾' : '▸';
        planOpen[openKey] = nowOpen;
        LS.set('planOpen', planOpen);
      }});
      taskEl.querySelectorAll('input[type=checkbox]').forEach(cb => {{
        cb.addEventListener('change', () => {{
          planChecks[cb.dataset.sub] = cb.checked;
          LS.set('planChecks', planChecks);
          updateTaskCount(taskEl, tid, total);
          updatePlanProgress();
        }});
      }});
      dayEl.appendChild(taskEl);
    }});
    planRoot.appendChild(dayEl);
  }});
  updatePlanProgress();
}}
function updateTaskCount(taskEl, tid, total) {{
  let done = 0;
  for (let si = 0; si < total; si++) if (planChecks[tid + '_s' + si]) done++;
  const el = taskEl.querySelector('.task-count');
  el.textContent = done + '/' + total;
  el.className = (done === total && total > 0) ? 'task-count done' : 'task-count';
  taskEl.querySelectorAll('.subtasks label').forEach((lab, si) => {{
    lab.classList.toggle('done', !!planChecks[tid + '_s' + si]);
  }});
}}
function updatePlanProgress() {{
  let done = 0, total = 0;
  PLAN_DATA.forEach((day, di) => {{
    day.tasks.forEach((task, ti) => {{
      task.subtasks.forEach((_, si) => {{
        total++;
        if (planChecks['d' + di + '_t' + ti + '_s' + si]) done++;
      }});
    }});
  }});
  const pct = total === 0 ? 0 : Math.round(100 * done / total);
  document.getElementById('planProgressFill').style.width = pct + '%';
  document.getElementById('planProgressText').textContent = done + ' / ' + total + ' (' + pct + '%)';
}}
document.getElementById('planResetBtn').addEventListener('click', () => {{
  if (!confirm('Reset all plan checks?')) return;
  Object.keys(planChecks).forEach(k => delete planChecks[k]);
  LS.set('planChecks', planChecks);
  renderPlan();
}});
renderPlan();

// ----- DSA Bank -----
const dsaRoot = document.getElementById('dsaBank');
const dsaOpen = LS.get('dsaOpen', {{}});
function renderDsa(filter) {{
  const q = (filter || '').trim().toLowerCase();
  dsaRoot.innerHTML = '';
  let shown = 0, total = 0;
  DSA_DATA.forEach((pat, pi) => {{
    const probs = pat.problems.filter(p => {{
      if (!q) return true;
      return ('lc' + p.lc).includes(q) || String(p.lc).includes(q) ||
             p.name.toLowerCase().includes(q) || pat.name.toLowerCase().includes(q) ||
             (p.diff || '').toLowerCase().includes(q);
    }});
    total += pat.problems.length;
    shown += probs.length;
    if (probs.length === 0) return;
    const patEl = document.createElement('div');
    patEl.className = 'pattern' + (pat.starred ? ' starred' : '');
    const openKey = 'p' + pi;
    const open = dsaOpen[openKey] !== false;
    patEl.innerHTML =
      '<div class="pattern-header" data-toggle><h3>' + escapeHtml(pat.name) + ' <span class="muted small">(' + probs.length + '/' + pat.problems.length + ')</span></h3><span class="chev">' + (open ? '▾' : '▸') + '</span></div>' +
      '<div class="pattern-blurb">' + escapeHtml(pat.blurb) + '</div>' +
      '<div class="pattern-body ' + (open ? '' : 'hidden') + '"></div>';
    const body = patEl.querySelector('.pattern-body');
    probs.forEach((p, qi) => {{
      const pkey = 'p' + pi + 'q' + qi;
      const pOpen = !!dsaOpen[pkey];
      const probEl = document.createElement('div');
      probEl.className = 'problem';
      probEl.innerHTML =
        '<div class="problem-head" data-toggle>' +
          '<span class="problem-name">LC' + p.lc + ' · ' + escapeHtml(p.name) + '</span>' +
          '<span class="diff ' + p.diff + '">' + p.diff + '</span>' +
          '<a href="' + p.url + '" target="_blank" rel="noopener">link</a>' +
        '</div>' +
        '<div class="problem-body ' + (pOpen ? '' : 'hidden') + '">' +
          '<p><strong>Approach:</strong> ' + escapeHtml(p.approach) + '</p>' +
          '<pre class="code"><code></code></pre>' +
          '<p class="complexity">Time: ' + escapeHtml(p.time) + ' · Space: ' + escapeHtml(p.space) + '</p>' +
        '</div>';
      probEl.querySelector('code').textContent = p.code;
      probEl.querySelector('.problem-head').addEventListener('click', (e) => {{
        if (e.target.tagName === 'A') return;
        const body = probEl.querySelector('.problem-body');
        body.classList.toggle('hidden');
        dsaOpen[pkey] = !body.classList.contains('hidden');
        LS.set('dsaOpen', dsaOpen);
      }});
      body.appendChild(probEl);
    }});
    patEl.querySelector('.pattern-header').addEventListener('click', () => {{
      body.classList.toggle('hidden');
      const opened = !body.classList.contains('hidden');
      patEl.querySelector('.chev').textContent = opened ? '▾' : '▸';
      dsaOpen[openKey] = opened;
      LS.set('dsaOpen', dsaOpen);
    }});
    dsaRoot.appendChild(patEl);
  }});
  document.getElementById('dsaCount').textContent = shown + ' / ' + total + ' problems';
}}
document.getElementById('dsaSearch').addEventListener('input', e => renderDsa(e.target.value));
renderDsa('');

// ----- Industry code blocks (lift from <script type="application/x-code">) -----
document.querySelectorAll('#tab-industry .card.collapsible').forEach(card => {{
  const codeNode = card.querySelector('script[type="application/x-code"]');
  if (codeNode) card.querySelector('pre code').textContent = codeNode.textContent;
  card.querySelector('.card-header').addEventListener('click', () => {{
    const body = card.querySelector('.card-body');
    body.classList.toggle('hidden');
    card.querySelector('.chev').textContent = body.classList.contains('hidden') ? '▸' : '▾';
  }});
}});

// ----- Mocks: random DSA test -----
function flatDsaProblems() {{
  const out = [];
  DSA_DATA.forEach(p => p.problems.forEach(q => out.push(Object.assign({{__pat: p.name}}, q))));
  return out;
}}
function pickRandom(arr, n) {{
  const pool = arr.slice();
  const out = [];
  for (let i = 0; i < n && pool.length; i++) {{
    const idx = Math.floor(Math.random() * pool.length);
    out.push(pool.splice(idx, 1)[0]);
  }}
  return out;
}}
const dsaTestArea = document.getElementById('dsaTestArea');
const dsaTimer = document.getElementById('dsaTestTimer');
let dsaTimerHandle = null;
document.getElementById('dsaTestStart').addEventListener('click', () => {{
  const n = parseInt(document.getElementById('dsaTestN').value, 10) || 3;
  const minutes = parseInt(document.getElementById('dsaTestMin').value, 10) || 25;
  const chosen = pickRandom(flatDsaProblems(), n);
  dsaTestArea.innerHTML = chosen.map((p, i) => (
    '<div class="mock-q">' +
      '<h3>Q' + (i + 1) + ' · ' + escapeHtml(p.__pat) + ' · LC' + p.lc + ' ' + escapeHtml(p.name) + ' <span class="diff ' + p.diff + '">' + p.diff + '</span></h3>' +
      '<p>Approach? Code it up. Don\'t peek.</p>' +
      '<details><summary>Reveal solution</summary>' +
        '<p><strong>Approach:</strong> ' + escapeHtml(p.approach) + '</p>' +
        '<pre class="code"><code></code></pre>' +
        '<p class="complexity">Time: ' + escapeHtml(p.time) + ' · Space: ' + escapeHtml(p.space) + '</p>' +
      '</details>' +
    '</div>'
  )).join('');
  dsaTestArea.querySelectorAll('pre code').forEach((el, i) => {{ el.textContent = chosen[i].code; }});
  // Timer
  let secsLeft = n * minutes * 60;
  if (dsaTimerHandle) clearInterval(dsaTimerHandle);
  function fmt(s) {{ const m = Math.floor(s / 60); const r = s % 60; return m + ':' + (r < 10 ? '0' : '') + r; }}
  dsaTimer.textContent = '⏱ ' + fmt(secsLeft);
  dsaTimerHandle = setInterval(() => {{
    secsLeft--;
    if (secsLeft <= 0) {{ clearInterval(dsaTimerHandle); dsaTimer.textContent = '⏱ TIME'; return; }}
    dsaTimer.textContent = '⏱ ' + fmt(secsLeft);
  }}, 1000);
}});

// ----- Mocks: random Automation test -----
const autoArea = document.getElementById('autoTestArea');
document.getElementById('autoTestStart').addEventListener('click', () => {{
  const n = parseInt(document.getElementById('autoTestN').value, 10) || 3;
  const chosen = pickRandom(AUTO_DATA, n);
  autoArea.innerHTML = chosen.map((q, i) => (
    '<div class="mock-q">' +
      '<h3>Q' + (i + 1) + '</h3>' +
      '<p>' + escapeHtml(q.q) + '</p>' +
      '<details><summary>Reveal model answer</summary><p>' + escapeHtml(q.a) + '</p></details>' +
    '</div>'
  )).join('');
}});

// ----- Mocks: guided rounds (3) -----
const GUIDED = [
  {{
    title: 'Round 1 — Coding + communication',
    prompt: 'Given an array of ints and a target, return any two indices whose values sum to the target. Explain your approach before coding. After coding, narrate your trace on [2,7,11,15], target 9. Follow-up: what if the array is sorted? What if duplicates are allowed?',
    rubric: ['Clarified inputs/constraints', 'Stated approach + complexity before coding', 'Bug-free first pass or self-caught', 'Narrated trace', 'Answered follow-up correctly'],
  }},
  {{
    title: 'Round 2 — DSA under time + follow-ups',
    prompt: 'You have 25 minutes: LC 200 (Number of Islands). Solve, narrate, complexity. Follow-ups: (a) what changes if water touches diagonally? (b) memory limits — can you stream the grid?',
    rubric: ['Solved in time', 'Correct complexity', 'Handled both follow-ups concretely', 'Calm under time'],
  }},
  {{
    title: 'Round 3 — Behavioral / Googliness',
    prompt: 'Pick one of your STAR stories. Tell the conflict-across-teams story in under 2 minutes. Then handle this probe: "How did the other person feel afterwards?"',
    rubric: ['Specific situation + task', 'You-not-we ownership', 'Concrete result', 'Empathy in probe answer', 'Stayed under 2 minutes'],
  }},
];
const guidedRoot = document.getElementById('guidedMockArea');
const mockNotes = LS.get('mockNotes', {{}});
const mockScores = LS.get('mockScores', {{}});
guidedRoot.innerHTML = GUIDED.map((g, i) => (
  '<div class="mock-q">' +
    '<h3>' + escapeHtml(g.title) + '</h3>' +
    '<p>' + escapeHtml(g.prompt) + '</p>' +
    '<textarea data-mk="m' + i + '" placeholder="Your answer / notes…">' + escapeHtml(mockNotes['m' + i] || '') + '</textarea>' +
    '<div class="mock-controls">' +
      '<label class="mock-score">Self-score: ' +
        '<select data-ms="m' + i + '">' +
          [1,2,3,4,5].map(v => '<option ' + (mockScores['m' + i] == v ? 'selected' : '') + '>' + v + '</option>').join('') +
        '</select>' +
      '</label>' +
      '<details><summary>Rubric</summary><ul>' + g.rubric.map(r => '<li>' + escapeHtml(r) + '</li>').join('') + '</ul></details>' +
    '</div>' +
  '</div>'
)).join('');
guidedRoot.querySelectorAll('textarea').forEach(ta => {{
  ta.addEventListener('input', () => {{ mockNotes[ta.dataset.mk] = ta.value; LS.set('mockNotes', mockNotes); }});
}});
guidedRoot.querySelectorAll('select').forEach(s => {{
  s.addEventListener('change', () => {{ mockScores[s.dataset.ms] = s.value; LS.set('mockScores', mockScores); }});
}});

// ----- Helpers -----
function escapeHtml(s) {{
  if (s == null) return '';
  return String(s).replace(/[&<>"']/g, c => ({{
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }})[c]);
}}
</script>
</body>
</html>
"""

# MAANG Prep — Dashboard & Resume Generator (tkinter)

A desktop tool that takes **your resume**, **job descriptions / target companies**, and a few profile inputs, and produces:

1. A **per-target tailored resume** (HTML + Markdown) with JD keywords highlighted, plus a cover-letter draft.
2. A **single-file `dashboard.html`** — your interview-prep command center: day-by-day plan with persistent checkboxes, ~80 LeetCode problems organized by 18 patterns, randomized DSA + SDET tests, guided mock rounds, behavioral STAR stories, company-specific hiring guide, and more.

The dashboard follows the spec in `4563acc2-dashboard_generation_prompt.md`: vanilla JS, light theme, Google Fonts only, `localStorage` persistence (try/catch wrapped), no build step.

## Requirements

- Python **3.10+** (uses PEP 604 unions; tested on 3.11).
- `tkinter` — ships with the standard python.org installer on Windows / macOS. On Linux:
  ```bash
  sudo apt-get install python3-tk      # Debian/Ubuntu
  sudo dnf install python3-tkinter     # Fedora
  ```
- No third-party packages required. Everything else is stdlib.

## Run

From the repo root:

```bash
python -m dashboard_generator.main
# or
python dashboard_generator/main.py
```

## Workflow

The window has six tabs along the top — fill them in order:

1. **Profile** — name, contact, target company/level, comp goal, application date, weak spots, daily routine, any real interview signal already faced.
2. **Resume** — paste your resume, or **Load file…** to import a `.txt` / `.md`. Click **Parse sections** to preview how it'll split.
3. **Targets & JDs** — add one entry per target: company, role, level, JD URL, paste the JD text, comp range, your "why this fits" note. Multiple targets are fine.
4. **Plan** — start date, deadline (application date), focused hours/day, fixed health block (e.g., daily swim), coursework name, side-project cap %, hard external deadlines, phase markers.
5. **Side project** — one capped portfolio project. Used as the behavioral "owned end-to-end" story and a system-design worked example.
6. **Generate** — pick an output directory, then:
   - **Generate tailored resumes** — produces `resume_<company-level>.{html,md}` + `cover_<company-level>.{html,md}` per target.
   - **Generate dashboard.html** — produces a single self-contained `dashboard.html`.
   - **Generate everything** — runs both.

Use the **Save session** / **Load session** buttons at the bottom of the window to persist your inputs between runs (default: `~/.maang_prep_session.json`).

## What the dashboard contains

Tabs (in the order they're loaded — `My Plan` opens first):

| Tab | What's in it |
|-----|---|
| My Plan + TODOs | Day-by-day cards with time-blocked tasks, nested subtasks with checkboxes, sticky overall progress bar, expand/collapse per task. State persists via `localStorage`. |
| DSA Bank | ~80 LeetCode problems across 18 patterns. The "Real-Asked / MAANG-style" pattern is starred and includes LC 489 (Robot Room Cleaner). Each problem has plain-English approach, **tested code** (rendered with `textContent` to avoid HTML injection), time/space, real LC link. Search box filters live. |
| Mocks & Tests | Randomized DSA test (pick N problems and minutes/problem, with countdown timer + reveal). Randomized Automation/SDET test (18-question pool incl. LLM-eval validation and intermittent hardware root-cause). 3 guided mock rounds with rubrics + self-scoring. |
| Resources | Curated **free** links by round type: NeetCode, Striver/takeUforward, HelloInterview, ByteByteGo, Karpathy Zero-to-Hero, Hugging Face Learn, Pramp, interviewing.io, etc. |
| Intro + Behavioral | 90-second self-intro draft, 7 STAR stories (why-leave, conflict, mentoring, hardest challenge, proudest project, failure, decision under incomplete info), each tagged S/T/A/R with a "why it lands" note. |
| Prep Strategy | Pattern-trigger table (phrase → algorithm), retention method, in-room algorithm. |
| Industry Problems | LRU cache, token-bucket rate limiter, LLM-eval pipeline with judge aggregation, hallucinated-API-call detection, exponential backoff with jitter — code each. |
| Company Guide | Verified hiring process for the target company (Google by default), what each round scores, the level bar, real recent candidate-reported questions. Process changes — re-verify before each loop. |
| Jobs | Your target list with comp ranges. Verify against [Levels.fyi](https://www.levels.fyi/). |
| Gaps + Focus | Your weak spots ranked, each with a concrete fix; time-allocation table. |
| Side Project | Your project as portfolio + behavioral + design — capped at ≤10% of prep time. |
| Overview | How to use the dashboard + comp math. |

## Code accuracy

The embedded DSA solutions and industry problems are tested by `/tmp/test_dsa_code.py` (60 solutions pass, 0 fail, 5 skipped because they require LeetCode environment stubs like `TreeNode` / `ListNode` / `Robot`). The skipped ones use canonical, well-known patterns.

## Extending the content

Edit `dashboard_generator/content.py`:

- `DSA_PATTERNS` — append a pattern or problem dict; keys: `name`, `lc`, `diff`, `approach`, `code`, `time`, `space`, `url`.
- `INDUSTRY_PROBLEMS` — append `{name, blurb, code}`.
- `AUTOMATION_QUESTIONS` — append `{q, a}`.
- `BEHAVIORAL_STORIES` — append `{title, s, t, a, r, why}`.
- `RESOURCES` — add a group or a link.
- `COMPANY_GUIDES` — add a company key with `process`, `rounds_score`, `level_bar`, `real_questions`, `notes`.

Re-run the test harness after editing `DSA_PATTERNS` or `INDUSTRY_PROBLEMS` if you change code.

## Files

```
dashboard_generator/
├── main.py                 # entry point (python -m dashboard_generator.main)
├── app.py                  # tkinter App with 6 input tabs + generate
├── models.py               # CandidateProfile, JobTarget, PlanConfig, ProjectSpec
├── parsers.py              # resume sectioning + JD keyword extraction
├── resume_builder.py       # tailored resume + cover letter (HTML + MD)
├── dashboard_builder.py    # builds the single-file dashboard.html
├── content.py              # DSA bank, resources, behavioral, industry, automation, company guides
└── README.md
```

## Caveats — read these

- **Comp ranges and hiring processes drift.** The company guide is seeded with what's true at time of writing; verify against the company's official "how we hire" page before each loop. Comp numbers on [Levels.fyi](https://www.levels.fyi/) vary by team, location, and negotiation.
- **The DSA bank is a starting point, not a complete library.** ~80 problems covering 18 patterns is enough to anchor a 12-week prep, but you'll want to add the specific problems your target's questions index has surfaced recently.
- **Resume tailoring is a tool, not a replacement for craft.** The generator highlights JD keywords and reorders bullets by match score — it doesn't write your bullets. Always re-read before sending.

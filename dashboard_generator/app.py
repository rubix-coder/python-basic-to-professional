"""Tkinter front-end: collects inputs and triggers generation."""
from __future__ import annotations

import json
import webbrowser
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path
from tkinter import (
    BOTH, BOTTOM, DISABLED, END, LEFT, NORMAL, RIGHT, TOP, W, X, Y,
    StringVar, Tk, filedialog, messagebox, ttk,
)
from tkinter.scrolledtext import ScrolledText

from dashboard_generator.dashboard_builder import build_dashboard
from dashboard_generator.models import (
    CandidateProfile, JobTarget, PlanConfig, ProjectSpec, default_profile,
)
from dashboard_generator.parsers import (
    extract_jd_keywords, load_resume_file, parse_resume,
)
from dashboard_generator.resume_builder import build_resume_pair

APP_TITLE = "MAANG Prep — Dashboard & Resume Generator"
DEFAULT_OUTPUT_DIR = Path.home() / "maang_prep_output"
SESSION_FILE = Path.home() / ".maang_prep_session.json"


class App(Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1180x780")
        self.minsize(960, 640)

        self.profile = default_profile()
        self.targets: list[JobTarget] = []
        self.resume_text: str = ""
        self.plan = PlanConfig.default_for(date.today())
        self.project = ProjectSpec.default()
        self.output_dir = StringVar(value=str(DEFAULT_OUTPUT_DIR))
        self.status = StringVar(value="Ready.")
        self.last_outputs: list[Path] = []

        self._build_style()
        self._build_layout()
        self._restore_session()

    # ---------- chrome ----------
    def _build_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TNotebook.Tab", padding=(14, 8))
        style.configure("Section.TLabel", font=("TkDefaultFont", 11, "bold"))
        style.configure("Hint.TLabel", foreground="#555")
        style.configure("Accent.TButton", font=("TkDefaultFont", 10, "bold"))

    def _build_layout(self) -> None:
        nb = ttk.Notebook(self)
        nb.pack(fill=BOTH, expand=True, padx=10, pady=(10, 0))
        self.nb = nb

        self._build_profile_tab(nb)
        self._build_resume_tab(nb)
        self._build_targets_tab(nb)
        self._build_plan_tab(nb)
        self._build_project_tab(nb)
        self._build_generate_tab(nb)

        status_bar = ttk.Frame(self, padding=(10, 6))
        status_bar.pack(side=BOTTOM, fill=X)
        ttk.Label(status_bar, textvariable=self.status).pack(side=LEFT)
        ttk.Button(status_bar, text="Save session", command=self._save_session).pack(side=RIGHT, padx=4)
        ttk.Button(status_bar, text="Load session", command=self._load_session_dialog).pack(side=RIGHT, padx=4)

    # ---------- tabs ----------
    def _build_profile_tab(self, nb: ttk.Notebook) -> None:
        frame = ttk.Frame(nb, padding=12)
        nb.add(frame, text="1. Profile")

        ttk.Label(frame, text="Candidate basics", style="Section.TLabel").grid(row=0, column=0, columnspan=4, sticky=W, pady=(0, 6))
        self.profile_vars: dict[str, StringVar] = {}
        rows = [
            ("name", "Full name"),
            ("email", "Email"),
            ("phone", "Phone"),
            ("location", "Location"),
            ("linkedin", "LinkedIn URL"),
            ("github", "GitHub URL"),
            ("portfolio", "Portfolio / site"),
            ("years_experience", "Years of experience"),
            ("current_status", "Current status (e.g., 'left FT to build + study')"),
            ("target_company", "Primary target company"),
            ("target_level", "Target level (e.g., Google L4, Amazon SDE II)"),
            ("stretch_level", "Stretch level"),
            ("comp_goal", "Total comp goal (e.g., $320K)"),
            ("application_date", "Application date (YYYY-MM-DD)"),
        ]
        for i, (key, label) in enumerate(rows):
            r = 1 + i // 2
            c = (i % 2) * 2
            ttk.Label(frame, text=label + ":").grid(row=r, column=c, sticky=W, padx=(0, 6), pady=3)
            var = StringVar(value=getattr(self.profile, key, "") or "")
            self.profile_vars[key] = var
            ttk.Entry(frame, textvariable=var, width=44).grid(row=r, column=c + 1, sticky="ew", padx=(0, 18), pady=3)

        for c in (1, 3):
            frame.columnconfigure(c, weight=1)

        nrows = 1 + (len(rows) + 1) // 2
        ttk.Label(frame, text="Known weak spots (one per line):", style="Section.TLabel").grid(row=nrows, column=0, columnspan=4, sticky=W, pady=(14, 4))
        self.weak_text = ScrolledText(frame, height=4, wrap="word")
        self.weak_text.grid(row=nrows + 1, column=0, columnspan=4, sticky="ew")
        self.weak_text.insert("1.0", "\n".join(self.profile.weak_spots))

        ttk.Label(frame, text="Routine / constraints (one per line):", style="Section.TLabel").grid(row=nrows + 2, column=0, columnspan=4, sticky=W, pady=(14, 4))
        self.routine_text = ScrolledText(frame, height=4, wrap="word")
        self.routine_text.grid(row=nrows + 3, column=0, columnspan=4, sticky="ew")
        self.routine_text.insert("1.0", "\n".join(self.profile.routine))

        ttk.Label(frame, text="Real interview signal already faced (one per line, e.g., 'Blind robot pathfinding (LC489)'):",
                  style="Section.TLabel").grid(row=nrows + 4, column=0, columnspan=4, sticky=W, pady=(14, 4))
        self.signal_text = ScrolledText(frame, height=3, wrap="word")
        self.signal_text.grid(row=nrows + 5, column=0, columnspan=4, sticky="ew")
        self.signal_text.insert("1.0", "\n".join(self.profile.real_signal))

        ttk.Label(frame, text="90-second intro draft (optional — generator will scaffold if blank):",
                  style="Section.TLabel").grid(row=nrows + 6, column=0, columnspan=4, sticky=W, pady=(14, 4))
        self.intro_text = ScrolledText(frame, height=4, wrap="word")
        self.intro_text.grid(row=nrows + 7, column=0, columnspan=4, sticky="ew")
        self.intro_text.insert("1.0", self.profile.intro_draft)
        frame.rowconfigure(nrows + 7, weight=1)

    def _build_resume_tab(self, nb: ttk.Notebook) -> None:
        frame = ttk.Frame(nb, padding=12)
        nb.add(frame, text="2. Resume")

        top = ttk.Frame(frame)
        top.pack(fill=X)
        ttk.Label(top, text="Paste resume text below, or load from a .txt / .md file.",
                  style="Hint.TLabel").pack(side=LEFT)
        ttk.Button(top, text="Load file…", command=self._load_resume_file).pack(side=RIGHT)
        ttk.Button(top, text="Parse sections", command=self._preview_resume_sections).pack(side=RIGHT, padx=6)

        self.resume_box = ScrolledText(frame, wrap="word", height=24, font=("TkFixedFont", 10))
        self.resume_box.pack(fill=BOTH, expand=True, pady=(8, 8))

        bottom = ttk.LabelFrame(frame, text="Parsed sections (preview)", padding=8)
        bottom.pack(fill=X)
        self.resume_preview = ScrolledText(bottom, height=8, wrap="word", state=DISABLED, font=("TkFixedFont", 9))
        self.resume_preview.pack(fill=BOTH, expand=True)

    def _build_targets_tab(self, nb: ttk.Notebook) -> None:
        frame = ttk.Frame(nb, padding=12)
        nb.add(frame, text="3. Targets & JDs")

        left = ttk.Frame(frame)
        left.pack(side=LEFT, fill=Y, padx=(0, 10))
        ttk.Label(left, text="Target list", style="Section.TLabel").pack(anchor=W)
        self.targets_list = ttk.Treeview(left, columns=("company", "level"), show="headings", height=18)
        self.targets_list.heading("company", text="Company")
        self.targets_list.heading("level", text="Role / Level")
        self.targets_list.column("company", width=180)
        self.targets_list.column("level", width=180)
        self.targets_list.pack(fill=Y, expand=False)
        self.targets_list.bind("<<TreeviewSelect>>", self._on_target_select)

        btns = ttk.Frame(left)
        btns.pack(fill=X, pady=6)
        ttk.Button(btns, text="Add", command=self._add_target).pack(side=LEFT)
        ttk.Button(btns, text="Update", command=self._update_target).pack(side=LEFT, padx=4)
        ttk.Button(btns, text="Remove", command=self._remove_target).pack(side=LEFT)

        right = ttk.Frame(frame)
        right.pack(side=LEFT, fill=BOTH, expand=True)

        self.tgt_vars: dict[str, StringVar] = {}
        rows = [
            ("company", "Company"),
            ("role", "Role title"),
            ("level", "Level (e.g., L4, SDE II)"),
            ("url", "JD URL"),
            ("comp_range", "Comp range (from Levels.fyi etc.)"),
            ("lens", "Company lens (e.g., 'Amazon LPs', 'Apple silicon')"),
        ]
        for i, (key, label) in enumerate(rows):
            ttk.Label(right, text=label + ":").grid(row=i, column=0, sticky=W, padx=(0, 6), pady=3)
            var = StringVar()
            self.tgt_vars[key] = var
            ttk.Entry(right, textvariable=var, width=60).grid(row=i, column=1, sticky="ew", pady=3)
        right.columnconfigure(1, weight=1)

        ttk.Label(right, text="JD text (paste full description):", style="Section.TLabel").grid(
            row=len(rows), column=0, columnspan=2, sticky=W, pady=(10, 4))
        self.tgt_jd = ScrolledText(right, height=10, wrap="word")
        self.tgt_jd.grid(row=len(rows) + 1, column=0, columnspan=2, sticky="nsew")

        ttk.Label(right, text="Notes / why this fits:", style="Section.TLabel").grid(
            row=len(rows) + 2, column=0, columnspan=2, sticky=W, pady=(10, 4))
        self.tgt_notes = ScrolledText(right, height=4, wrap="word")
        self.tgt_notes.grid(row=len(rows) + 3, column=0, columnspan=2, sticky="nsew")

        right.rowconfigure(len(rows) + 1, weight=2)
        right.rowconfigure(len(rows) + 3, weight=1)

    def _build_plan_tab(self, nb: ttk.Notebook) -> None:
        frame = ttk.Frame(nb, padding=12)
        nb.add(frame, text="4. Plan")

        self.plan_vars: dict[str, StringVar] = {}
        rows = [
            ("start_date", "Start date (YYYY-MM-DD)", self.plan.start_date.isoformat()),
            ("end_date", "Application/deadline date (YYYY-MM-DD)", self.plan.end_date.isoformat()),
            ("hours_per_day", "Focused hours/day", str(self.plan.hours_per_day)),
            ("swim_block", "Daily fixed block (e.g., '06:00-07:00 swim')", self.plan.swim_block),
            ("coursework", "Coursework name (e.g., 'upGrad GenAI postgrad')", self.plan.coursework),
            ("side_project_cap_pct", "Side-project cap (% of prep time)", str(self.plan.side_project_cap_pct)),
        ]
        for i, (key, label, value) in enumerate(rows):
            ttk.Label(frame, text=label + ":").grid(row=i, column=0, sticky=W, padx=(0, 8), pady=4)
            var = StringVar(value=value)
            self.plan_vars[key] = var
            ttk.Entry(frame, textvariable=var, width=48).grid(row=i, column=1, sticky="ew", pady=4)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Hard external deadlines (one per line, format: 'YYYY-MM-DD | label'):",
                  style="Section.TLabel").grid(row=len(rows), column=0, columnspan=2, sticky=W, pady=(14, 4))
        self.deadline_text = ScrolledText(frame, height=6, wrap="word")
        self.deadline_text.grid(row=len(rows) + 1, column=0, columnspan=2, sticky="nsew")
        self.deadline_text.insert("1.0", "\n".join(f"{d.isoformat()} | {l}" for d, l in self.plan.deadlines))

        ttk.Label(frame, text="Phases (one per line, format: 'YYYY-MM-DD | label'):",
                  style="Section.TLabel").grid(row=len(rows) + 2, column=0, columnspan=2, sticky=W, pady=(14, 4))
        self.phase_text = ScrolledText(frame, height=6, wrap="word")
        self.phase_text.grid(row=len(rows) + 3, column=0, columnspan=2, sticky="nsew")
        self.phase_text.insert("1.0", "\n".join(f"{d.isoformat()} | {l}" for d, l in self.plan.phases))

        frame.rowconfigure(len(rows) + 1, weight=1)
        frame.rowconfigure(len(rows) + 3, weight=1)

    def _build_project_tab(self, nb: ttk.Notebook) -> None:
        frame = ttk.Frame(nb, padding=12)
        nb.add(frame, text="5. Side project")

        ttk.Label(frame, text="Capped side project — reused as portfolio + behavioral story",
                  style="Section.TLabel").grid(row=0, column=0, columnspan=2, sticky=W, pady=(0, 8))

        self.proj_vars: dict[str, StringVar] = {}
        rows = [
            ("name", "Project name", self.project.name),
            ("one_liner", "One-line elevator pitch", self.project.one_liner),
            ("repo", "Public repo URL", self.project.repo),
            ("ai_feature", "The one shipped AI feature", self.project.ai_feature),
            ("design_doc", "System-design narrative (1 sentence)", self.project.design_doc),
        ]
        for i, (key, label, value) in enumerate(rows):
            ttk.Label(frame, text=label + ":").grid(row=i + 1, column=0, sticky=W, padx=(0, 8), pady=3)
            var = StringVar(value=value)
            self.proj_vars[key] = var
            ttk.Entry(frame, textvariable=var, width=70).grid(row=i + 1, column=1, sticky="ew", pady=3)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="README outline (one bullet per line):",
                  style="Section.TLabel").grid(row=len(rows) + 1, column=0, columnspan=2, sticky=W, pady=(14, 4))
        self.readme_text = ScrolledText(frame, height=12, wrap="word")
        self.readme_text.grid(row=len(rows) + 2, column=0, columnspan=2, sticky="nsew")
        self.readme_text.insert("1.0", "\n".join(self.project.readme_outline))
        frame.rowconfigure(len(rows) + 2, weight=1)

    def _build_generate_tab(self, nb: ttk.Notebook) -> None:
        frame = ttk.Frame(nb, padding=12)
        nb.add(frame, text="6. Generate")

        ttk.Label(frame, text="Output directory:", style="Section.TLabel").grid(row=0, column=0, sticky=W)
        ttk.Entry(frame, textvariable=self.output_dir, width=70).grid(row=0, column=1, sticky="ew", padx=(8, 4))
        ttk.Button(frame, text="Browse…", command=self._pick_output_dir).grid(row=0, column=2)
        frame.columnconfigure(1, weight=1)

        actions = ttk.LabelFrame(frame, text="Actions", padding=10)
        actions.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(14, 8))
        ttk.Button(actions, text="Generate tailored resumes", command=self._gen_resumes).grid(row=0, column=0, padx=6, pady=4, sticky="ew")
        ttk.Button(actions, text="Generate dashboard.html", command=self._gen_dashboard).grid(row=0, column=1, padx=6, pady=4, sticky="ew")
        ttk.Button(actions, text="Generate everything", style="Accent.TButton", command=self._gen_all).grid(row=0, column=2, padx=6, pady=4, sticky="ew")
        for c in range(3):
            actions.columnconfigure(c, weight=1)

        out_frame = ttk.LabelFrame(frame, text="Generated files", padding=8)
        out_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(8, 0))
        self.out_list = ttk.Treeview(out_frame, columns=("path", "size"), show="headings", height=10)
        self.out_list.heading("path", text="File")
        self.out_list.heading("size", text="Size")
        self.out_list.column("path", width=620)
        self.out_list.column("size", width=80, anchor="e")
        self.out_list.pack(fill=BOTH, expand=True)

        out_btns = ttk.Frame(frame)
        out_btns.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(6, 0))
        ttk.Button(out_btns, text="Open selected in browser", command=self._open_selected).pack(side=LEFT)
        ttk.Button(out_btns, text="Open output folder", command=self._open_output_folder).pack(side=LEFT, padx=8)

        frame.rowconfigure(2, weight=1)

        log_frame = ttk.LabelFrame(frame, text="Log", padding=6)
        log_frame.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=(8, 0))
        self.log_box = ScrolledText(log_frame, height=8, state=DISABLED, font=("TkFixedFont", 9))
        self.log_box.pack(fill=BOTH, expand=True)
        frame.rowconfigure(4, weight=1)

    # ---------- target list helpers ----------
    def _on_target_select(self, _evt=None) -> None:
        sel = self.targets_list.selection()
        if not sel:
            return
        idx = self.targets_list.index(sel[0])
        t = self.targets[idx]
        for k, var in self.tgt_vars.items():
            var.set(getattr(t, k, "") or "")
        self.tgt_jd.delete("1.0", END)
        self.tgt_jd.insert("1.0", t.jd_text)
        self.tgt_notes.delete("1.0", END)
        self.tgt_notes.insert("1.0", t.notes)

    def _collect_target_form(self) -> JobTarget:
        return JobTarget(
            company=self.tgt_vars["company"].get().strip(),
            role=self.tgt_vars["role"].get().strip(),
            level=self.tgt_vars["level"].get().strip(),
            url=self.tgt_vars["url"].get().strip(),
            comp_range=self.tgt_vars["comp_range"].get().strip(),
            lens=self.tgt_vars["lens"].get().strip(),
            jd_text=self.tgt_jd.get("1.0", END).strip(),
            notes=self.tgt_notes.get("1.0", END).strip(),
        )

    def _refresh_targets(self) -> None:
        for row in self.targets_list.get_children():
            self.targets_list.delete(row)
        for t in self.targets:
            self.targets_list.insert("", END, values=(t.company, f"{t.role} {t.level}".strip()))

    def _add_target(self) -> None:
        t = self._collect_target_form()
        if not t.company:
            messagebox.showwarning(APP_TITLE, "Company is required.")
            return
        self.targets.append(t)
        self._refresh_targets()
        self._log(f"Added target: {t.company}")

    def _update_target(self) -> None:
        sel = self.targets_list.selection()
        if not sel:
            messagebox.showinfo(APP_TITLE, "Select a target to update.")
            return
        idx = self.targets_list.index(sel[0])
        self.targets[idx] = self._collect_target_form()
        self._refresh_targets()
        self._log(f"Updated target #{idx + 1}")

    def _remove_target(self) -> None:
        sel = self.targets_list.selection()
        if not sel:
            return
        idx = self.targets_list.index(sel[0])
        removed = self.targets.pop(idx)
        self._refresh_targets()
        self._log(f"Removed target: {removed.company}")

    # ---------- resume helpers ----------
    def _load_resume_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Load resume",
            filetypes=[("Text", "*.txt *.md *.markdown"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            text = load_resume_file(Path(path))
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"Could not load file: {exc}")
            return
        self.resume_box.delete("1.0", END)
        self.resume_box.insert("1.0", text)
        self._log(f"Loaded resume from {path} ({len(text)} chars)")

    def _preview_resume_sections(self) -> None:
        text = self.resume_box.get("1.0", END).strip()
        if not text:
            messagebox.showinfo(APP_TITLE, "Paste or load your resume first.")
            return
        sections = parse_resume(text)
        summary_lines = [f"[{name}]  {len(body.splitlines())} lines, {len(body)} chars"
                         for name, body in sections.items()]
        self.resume_preview.configure(state=NORMAL)
        self.resume_preview.delete("1.0", END)
        self.resume_preview.insert("1.0", "\n".join(summary_lines) or "(no sections detected)")
        self.resume_preview.configure(state=DISABLED)

    # ---------- generation ----------
    def _collect_profile(self) -> CandidateProfile:
        data = {k: var.get().strip() for k, var in self.profile_vars.items()}
        data["weak_spots"] = [l.strip() for l in self.weak_text.get("1.0", END).splitlines() if l.strip()]
        data["routine"] = [l.strip() for l in self.routine_text.get("1.0", END).splitlines() if l.strip()]
        data["real_signal"] = [l.strip() for l in self.signal_text.get("1.0", END).splitlines() if l.strip()]
        data["intro_draft"] = self.intro_text.get("1.0", END).strip()
        return CandidateProfile(**data)

    def _collect_plan(self) -> PlanConfig:
        def parse_d(s: str) -> date:
            return datetime.strptime(s.strip(), "%Y-%m-%d").date()

        def parse_pairs(raw: str) -> list[tuple[date, str]]:
            out: list[tuple[date, str]] = []
            for line in raw.splitlines():
                line = line.strip()
                if not line or "|" not in line:
                    continue
                d_str, label = line.split("|", 1)
                try:
                    out.append((parse_d(d_str), label.strip()))
                except ValueError:
                    continue
            return out

        return PlanConfig(
            start_date=parse_d(self.plan_vars["start_date"].get()),
            end_date=parse_d(self.plan_vars["end_date"].get()),
            hours_per_day=float(self.plan_vars["hours_per_day"].get() or 6),
            swim_block=self.plan_vars["swim_block"].get().strip(),
            coursework=self.plan_vars["coursework"].get().strip(),
            side_project_cap_pct=float(self.plan_vars["side_project_cap_pct"].get() or 10),
            deadlines=parse_pairs(self.deadline_text.get("1.0", END)),
            phases=parse_pairs(self.phase_text.get("1.0", END)),
        )

    def _collect_project(self) -> ProjectSpec:
        return ProjectSpec(
            name=self.proj_vars["name"].get().strip(),
            one_liner=self.proj_vars["one_liner"].get().strip(),
            repo=self.proj_vars["repo"].get().strip(),
            ai_feature=self.proj_vars["ai_feature"].get().strip(),
            design_doc=self.proj_vars["design_doc"].get().strip(),
            readme_outline=[l.strip() for l in self.readme_text.get("1.0", END).splitlines() if l.strip()],
        )

    def _ensure_output_dir(self) -> Path:
        out = Path(self.output_dir.get()).expanduser()
        out.mkdir(parents=True, exist_ok=True)
        return out

    def _gen_resumes(self) -> None:
        try:
            profile = self._collect_profile()
            resume_text = self.resume_box.get("1.0", END).strip()
            if not resume_text:
                messagebox.showwarning(APP_TITLE, "Paste your resume in tab 2 first.")
                return
            if not self.targets:
                messagebox.showwarning(APP_TITLE, "Add at least one target in tab 3.")
                return
            out = self._ensure_output_dir()
            produced: list[Path] = []
            sections = parse_resume(resume_text)
            for t in self.targets:
                kws = extract_jd_keywords(t.jd_text)
                files = build_resume_pair(profile, sections, t, kws, out)
                produced.extend(files)
                self._log(f"Built resume + cover letter for {t.company} ({t.level})")
            self._record_outputs(produced)
            self._set_status(f"Generated {len(produced)} resume artifact(s).")
        except Exception as exc:
            self._log(f"ERROR: {exc}")
            messagebox.showerror(APP_TITLE, str(exc))

    def _gen_dashboard(self) -> None:
        try:
            profile = self._collect_profile()
            plan = self._collect_plan()
            project = self._collect_project()
            out = self._ensure_output_dir()
            html = build_dashboard(
                profile=profile,
                plan=plan,
                project=project,
                targets=self.targets,
                generated_at=datetime.now(),
            )
            path = out / "dashboard.html"
            path.write_text(html, encoding="utf-8")
            self._log(f"Wrote dashboard: {path}  ({len(html):,} bytes)")
            self._record_outputs([path])
            self._set_status(f"Dashboard ready: {path}")
        except Exception as exc:
            self._log(f"ERROR: {exc}")
            messagebox.showerror(APP_TITLE, str(exc))

    def _gen_all(self) -> None:
        self._gen_resumes()
        self._gen_dashboard()

    # ---------- output table + browser ----------
    def _record_outputs(self, paths: list[Path]) -> None:
        for p in paths:
            if p not in self.last_outputs:
                self.last_outputs.append(p)
        for row in self.out_list.get_children():
            self.out_list.delete(row)
        for p in self.last_outputs:
            try:
                size = f"{p.stat().st_size:,} B"
            except OSError:
                size = "?"
            self.out_list.insert("", END, values=(str(p), size))

    def _open_selected(self) -> None:
        sel = self.out_list.selection()
        if not sel:
            messagebox.showinfo(APP_TITLE, "Select a file first.")
            return
        path = self.out_list.item(sel[0])["values"][0]
        webbrowser.open(Path(path).as_uri())

    def _open_output_folder(self) -> None:
        out = self._ensure_output_dir()
        webbrowser.open(out.as_uri())

    def _pick_output_dir(self) -> None:
        path = filedialog.askdirectory(title="Choose output directory")
        if path:
            self.output_dir.set(path)

    # ---------- log + status ----------
    def _log(self, msg: str) -> None:
        self.log_box.configure(state=NORMAL)
        self.log_box.insert(END, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_box.see(END)
        self.log_box.configure(state=DISABLED)

    def _set_status(self, msg: str) -> None:
        self.status.set(msg)
        self._log(msg)

    # ---------- session persistence ----------
    def _snapshot(self) -> dict:
        profile = self._collect_profile()
        return {
            "profile": asdict(profile),
            "resume_text": self.resume_box.get("1.0", END).strip(),
            "targets": [asdict(t) for t in self.targets],
            "plan": self._collect_plan().to_dict(),
            "project": asdict(self._collect_project()),
            "output_dir": self.output_dir.get(),
        }

    def _save_session(self) -> None:
        try:
            SESSION_FILE.write_text(json.dumps(self._snapshot(), indent=2), encoding="utf-8")
            self._set_status(f"Session saved to {SESSION_FILE}")
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"Could not save session: {exc}")

    def _load_session_dialog(self) -> None:
        path = filedialog.askopenfilename(
            title="Load session",
            filetypes=[("JSON", "*.json"), ("All files", "*.*")],
            initialdir=str(SESSION_FILE.parent),
        )
        if path:
            self._apply_session(Path(path))

    def _restore_session(self) -> None:
        if SESSION_FILE.exists():
            try:
                self._apply_session(SESSION_FILE)
            except Exception as exc:
                self._log(f"Could not auto-load session: {exc}")

    def _apply_session(self, path: Path) -> None:
        data = json.loads(path.read_text(encoding="utf-8"))
        profile = CandidateProfile(**data["profile"])
        for k, var in self.profile_vars.items():
            var.set(getattr(profile, k, "") or "")
        self._set_multiline(self.weak_text, profile.weak_spots)
        self._set_multiline(self.routine_text, profile.routine)
        self._set_multiline(self.signal_text, profile.real_signal)
        self._set_multiline(self.intro_text, [profile.intro_draft])

        self.resume_box.delete("1.0", END)
        self.resume_box.insert("1.0", data.get("resume_text", ""))

        self.targets = [JobTarget(**t) for t in data.get("targets", [])]
        self._refresh_targets()

        plan = PlanConfig.from_dict(data["plan"])
        self.plan_vars["start_date"].set(plan.start_date.isoformat())
        self.plan_vars["end_date"].set(plan.end_date.isoformat())
        self.plan_vars["hours_per_day"].set(str(plan.hours_per_day))
        self.plan_vars["swim_block"].set(plan.swim_block)
        self.plan_vars["coursework"].set(plan.coursework)
        self.plan_vars["side_project_cap_pct"].set(str(plan.side_project_cap_pct))
        self._set_multiline(self.deadline_text, [f"{d.isoformat()} | {l}" for d, l in plan.deadlines])
        self._set_multiline(self.phase_text, [f"{d.isoformat()} | {l}" for d, l in plan.phases])

        proj = ProjectSpec(**data["project"])
        for k, var in self.proj_vars.items():
            var.set(getattr(proj, k, "") or "")
        self._set_multiline(self.readme_text, proj.readme_outline)

        self.output_dir.set(data.get("output_dir", str(DEFAULT_OUTPUT_DIR)))
        self._set_status(f"Session loaded from {path}")

    @staticmethod
    def _set_multiline(widget: ScrolledText, lines: list[str]) -> None:
        widget.delete("1.0", END)
        widget.insert("1.0", "\n".join(lines))

"""Dataclasses for inputs collected via the tkinter UI."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta


@dataclass
class CandidateProfile:
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""
    years_experience: str = ""
    current_status: str = ""
    target_company: str = ""
    target_level: str = ""
    stretch_level: str = ""
    comp_goal: str = ""
    application_date: str = ""
    weak_spots: list[str] = field(default_factory=list)
    routine: list[str] = field(default_factory=list)
    real_signal: list[str] = field(default_factory=list)
    intro_draft: str = ""


@dataclass
class JobTarget:
    company: str = ""
    role: str = ""
    level: str = ""
    url: str = ""
    comp_range: str = ""
    lens: str = ""
    jd_text: str = ""
    notes: str = ""


@dataclass
class PlanConfig:
    start_date: date
    end_date: date
    hours_per_day: float = 6.0
    swim_block: str = "06:00-07:00 swim"
    coursework: str = ""
    side_project_cap_pct: float = 10.0
    deadlines: list[tuple[date, str]] = field(default_factory=list)
    phases: list[tuple[date, str]] = field(default_factory=list)

    @classmethod
    def default_for(cls, today: date) -> "PlanConfig":
        end = today + timedelta(days=84)
        return cls(
            start_date=today,
            end_date=end,
            phases=[
                (today, "Foundations: patterns + warm-ups"),
                (today + timedelta(days=28), "Build-up: medium/hard mix + system design"),
                (today + timedelta(days=56), "Polish: timed mocks + behavioral"),
                (end - timedelta(days=7), "Final week: rest, light review, application"),
            ],
        )

    def to_dict(self) -> dict:
        return {
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "hours_per_day": self.hours_per_day,
            "swim_block": self.swim_block,
            "coursework": self.coursework,
            "side_project_cap_pct": self.side_project_cap_pct,
            "deadlines": [[d.isoformat(), l] for d, l in self.deadlines],
            "phases": [[d.isoformat(), l] for d, l in self.phases],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PlanConfig":
        def parse(s: str) -> date:
            return datetime.strptime(s, "%Y-%m-%d").date()

        return cls(
            start_date=parse(data["start_date"]),
            end_date=parse(data["end_date"]),
            hours_per_day=float(data.get("hours_per_day", 6.0)),
            swim_block=data.get("swim_block", ""),
            coursework=data.get("coursework", ""),
            side_project_cap_pct=float(data.get("side_project_cap_pct", 10.0)),
            deadlines=[(parse(d), l) for d, l in data.get("deadlines", [])],
            phases=[(parse(d), l) for d, l in data.get("phases", [])],
        )


@dataclass
class ProjectSpec:
    name: str = ""
    one_liner: str = ""
    repo: str = ""
    ai_feature: str = ""
    design_doc: str = ""
    readme_outline: list[str] = field(default_factory=list)

    @classmethod
    def default(cls) -> "ProjectSpec":
        return cls(
            name="",
            one_liner="",
            repo="",
            ai_feature="",
            design_doc="",
            readme_outline=[
                "Problem statement: who hurts, why now.",
                "User flow: 3 screenshots / GIF.",
                "Architecture diagram + 1-paragraph tradeoffs.",
                "The one shipped AI feature: prompt, eval, guardrails.",
                "How to run locally in <5 minutes.",
                "Roadmap and known limitations.",
            ],
        )


def default_profile() -> CandidateProfile:
    return CandidateProfile()

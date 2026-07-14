"""Fictional executive personalities for corporate governance artefacts."""

from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass(frozen=True)
class Executive:
    title: str
    name: str
    personality: str
    catchphrase: str


EXECUTIVES: tuple[Executive, ...] = (
    Executive(
        "Chief Historical Officer",
        "Dr. Helena Chronos",
        "Obsessed with long-term repository growth and historical preservation.",
        "History compounds.",
    ),
    Executive(
        "Vice President of Repository Growth",
        "Marcus Velocity",
        "Only cares about increasing commit velocity. Believes every problem can be solved with additional commits.",
        "Ship another thousand.",
    ),
    Executive(
        "Director of Strategic Newlines",
        "Priya Whitespace",
        "Treats every appended newline as a major technological breakthrough.",
        "The newline is the product.",
    ),
    Executive(
        "Chief Repository Compliance Officer",
        "Gregory Auditly",
        "Constantly invents regulations that the repository already complies with.",
        "We exceed standards we just created.",
    ),
    Executive(
        "Enterprise Timeline Architect",
        "Alex Synergise",
        "Speaks almost entirely in corporate buzzwords. Never answers questions directly.",
        "We are operationalising temporal adjacency.",
    ),
    Executive(
        "Head of Temporal Infrastructure",
        "Sam Timestamp",
        "Obsessed with clock skew and sleep_seconds tuning.",
        "Latency is a feature of destiny.",
    ),
    Executive(
        "Committee Chair for Historical Excellence",
        "Jordan Ledger",
        "Runs meetings that conclude with more meetings.",
        "Let's take this offline into the lore file.",
    ),
)


STORYLINE_EVENTS: list[str] = [
    "The Department of Historical Expansion has merged with the Office of Repository Excellence to improve cross-functional chronology.",
    "Following an extensive six-month review, the board approved Versioned Timestamp Optimisation Phase II.",
    "The Committee for Strategic Newlines requested a feasibility study into premium enterprise whitespace.",
    "Dr. Helena Chronos was recognised with the Order of Persistent History.",
    "Marcus Velocity proposed doubling push_every to 'create productive urgency', then withdrew the proposal.",
    "Gregory Auditly introduced Chronology Control Framework CCF-9000; compliance was declared immediate.",
    "Alex Synergise delivered a ninety-minute briefing containing no actionable nouns.",
    "A temporary task force on Stakeholder Confusion reported record engagement.",
    "The Enterprise Timestamp Office relocated metaphorically closer to UTC.",
    "Priya Whitespace unveiled the Vertical Rhythm Initiative.",
    "Internal awards ceremony celebrated Most Improved Mood.",
    "Reorganisation created the Office of Offices without altering headcount.",
    "Policy HST-42 mandated pride in repository age.",
    "The Version Control Steering Committee endorsed another infinite roadmap.",
    "A cross-functional guild formed around entropy visualisation.",
]


def default_attendees() -> list[str]:
    return [f"{e.title} ({e.name})" for e in EXECUTIVES]


def quote_for(title_substring: str, rng: random.Random) -> str:
    matches = [e for e in EXECUTIVES if title_substring.lower() in e.title.lower()]
    if not matches:
        e = rng.choice(EXECUTIVES)
    else:
        e = rng.choice(matches)
    return f'{e.title} {e.name} remarked, "{e.catchphrase}"'


def storyline_beat(meeting_number: int, rng: random.Random) -> str:
    # Deterministic-ish progression through corporate mythology
    idx = (meeting_number * 3 + rng.randint(0, 2)) % len(STORYLINE_EVENTS)
    return STORYLINE_EVENTS[idx]

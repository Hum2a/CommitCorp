"""Generates the Repository Expansion Report (history file)."""

from __future__ import annotations

import random
from datetime import datetime
from pathlib import Path

from commit_machine.entropy_engine import EntropyReport

REPOSITORY_MOODS: list[str] = [
    "Visionary",
    "Determined",
    "Enterprise",
    "Motivated",
    "Agile",
    "Scrum Compatible",
    "Cloud Native",
    "Audit Ready",
    "ISO Compliant",
    "Revolutionary",
    "AI Powered",
    "Synergistic",
    "Optimistic",
    "Chronological",
]

BUZZWORDS: list[str] = [
    "Leveraging repository synergies.",
    "Unlocking historical scalability.",
    "Maximising chronological throughput.",
    "Future-proofing version control.",
    "Driving repository transformation.",
    "Creating stakeholder value.",
    "Accelerating enterprise chronology.",
    "Mission-critical timestamp deployment.",
    "Hyper-scalable historical persistence.",
    "Continuous Repository Excellence.",
]

OBJECTIVES: list[str] = [
    "Continue existing.",
    "Expand historical surface area.",
    "Sustain chronological velocity.",
    "Preserve enterprise emptiness.",
    "Advance the infinite roadmap.",
]

MISSIONS: list[str] = [
    "Preserve history.",
    "Institutionalise chronology.",
    "Deliver versioned permanence.",
    "Champion repository growth.",
    "Safeguard temporal integrity.",
]

OUTLOOKS: list[str] = [
    "Further chronology anticipated.",
    "Additional history forecast.",
    "Expansion trajectory confirmed.",
    "Stakeholders expect more timestamps.",
    "The roadmap remains infinite.",
]

STATUSES: list[str] = [
    "Nominal",
    "Operational",
    "Optimal",
    "Enterprise Ready",
    "Board Approved",
]


class FileGenerator:
    """Writes the target history file with slight per-cycle variation."""

    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()

    def choose_mood(self) -> str:
        return self._rng.choice(REPOSITORY_MOODS)

    def render(
        self,
        *,
        revision: int,
        entropy: EntropyReport,
        mood: str | None = None,
        version: str = "v0.0.0",
    ) -> str:
        mood = mood or self.choose_mood()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        buzzword = self._rng.choice(BUZZWORDS)
        objective = self._rng.choice(OBJECTIVES)
        mission = self._rng.choice(MISSIONS)
        outlook = self._rng.choice(OUTLOOKS)
        status = self._rng.choice(STATUSES)
        # Slight content drift: variable blank lines and a rotating footnote
        spacer = "\n" * self._rng.randint(1, 3)
        footnote_id = self._rng.randint(1000, 9999)

        return f"""Repository Expansion Report

Historical Revision

{revision}

Timestamp

{timestamp}

Repository Mood

{mood}

Operational Status

{status}

Historical Confidence

{entropy.historical_confidence}%

Entropy Level

{entropy.score:.0f}%

Entropy Classification

{entropy.level_label}

Current Objective

{objective}

Corporate Mission

{mission}

Git Satisfaction

{entropy.git_satisfaction}

Strategic Outlook

{outlook}

Enterprise Initiative

{buzzword}

Platform Version

{version}
{spacer}
Document Control
Classification: Internal — Chronological Operations
Reference: ICM-{footnote_id}
Department of Historical Expansion
CommitCorp Enterprise
"""

    def write(
        self,
        path: Path,
        *,
        revision: int,
        entropy: EntropyReport,
        mood: str | None = None,
        version: str = "v0.0.0",
    ) -> tuple[str, str]:
        """Write history file. Returns (content, mood)."""
        mood = mood or self.choose_mood()
        content = self.render(
            revision=revision,
            entropy=entropy,
            mood=mood,
            version=version,
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return content, mood

    @staticmethod
    def newline_count(content: str) -> int:
        return content.count("\n")

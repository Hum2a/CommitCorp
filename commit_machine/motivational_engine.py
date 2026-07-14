"""Company mottos and corporate encouragement for operational logs."""

from __future__ import annotations

import random
from typing import Sequence

MOTTOS: Sequence[str] = (
    "History won't write itself.",
    "Every commit matters.",
    "Committed to commitment.",
    "The future is versioned.",
    "Enterprise-grade chronology.",
    "Building tomorrow's Git history today.",
    "History is our primary deliverable.",
    "Moving version control forward one pointless commit at a time.",
    "Our roadmap is infinite.",
    "Preserving the present for the future.",
)

CORPORATE_VALUES: Sequence[str] = (
    "Integrity",
    "Reliability",
    "Chronology",
    "Documentation",
    "Persistence",
    "Sustainable Repository Growth",
    "Continuous Historical Improvement",
    "Stakeholder Confusion",
)


class MotivationalEngine:
    """Supplies mottos and values for dashboards and departmental logs."""

    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()

    def motto(self) -> str:
        return self._rng.choice(list(MOTTOS))

    def value(self) -> str:
        return self._rng.choice(list(CORPORATE_VALUES))

    def pep_talk(self) -> str:
        return f"{self.motto()} Value of the cycle: {self.value()}."

"""Board of Directors minutes — every 5,000 commits."""

from __future__ import annotations

import logging
import random
from datetime import date
from pathlib import Path

from commit_machine.executives import (
    default_attendees,
    quote_for,
    storyline_beat,
)
from commit_machine.state import RuntimeState

logger = logging.getLogger(__name__)

BOARD_INTERVAL = 5_000


class BoardMinutesGenerator:
    """Appends solemn board minutes to BOARD_MINUTES.md."""

    def __init__(self, path: Path, rng: random.Random | None = None) -> None:
        self.path = path
        self._rng = rng or random.Random()

    def due(self, state: RuntimeState) -> bool:
        if state.total_commits < BOARD_INTERVAL:
            return False
        if state.total_commits % BOARD_INTERVAL != 0:
            return False
        return state.total_commits > state.last_board_meeting

    def generate_entry(self, state: RuntimeState) -> str:
        state.board_meeting_count += 1
        meeting_no = state.board_meeting_count
        attendees = "\n\n".join(default_attendees())
        beat = storyline_beat(meeting_no, self._rng)
        cho = quote_for("Chief Historical", self._rng)
        vp = quote_for("Vice President", self._rng)
        compliance = quote_for("Compliance", self._rng)

        return f"""
================================================

CommitCorp Enterprise

Board Meeting #{meeting_no}

================================================

Date

{date.today().isoformat()}

Attendees

{attendees}

================================================

Agenda

Review repository maturity.

Assess historical expansion velocity.

Evaluate enterprise chronology initiatives.

Approve future newline strategy.

Review stakeholder confidence.

================================================

Key Metrics

Total Commits

{state.total_commits:,}

Historical Density

Excellent

Repository Confidence

99.998%

Operational Readiness

Green

Business Value

Undetermined

================================================

Discussion

The board congratulated the Historical Expansion Division on another
successful period of continuous repository growth.

{beat}

{cho}

{vp}

{compliance}

Historical confidence continues to exceed internal expectations despite
the complete absence of practical utility.

Management agreed that the repository is successfully fulfilling its core
objective of becoming increasingly historical.

================================================

Risks

A developer may eventually ask why this exists.

Git may become self-aware.

Repository history may exceed available human attention span.

================================================

Action Items

Increase historical expansion.

Continue strategic timestamp deployment.

Investigate opportunities for additional chronology.

Maintain enterprise-grade pointlessness.

================================================

Closing Statement

The Board unanimously approved continued investment in repository growth
and congratulated all departments on another exceptionally productive
period of accomplishing almost nothing.

Meeting Adjourned.

================================================
"""

    def append(self, state: RuntimeState) -> Path | None:
        if not self.due(state):
            return None
        entry = self.generate_entry(state)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(entry)
        state.last_board_meeting = state.total_commits
        logger.info(
            "Committee Chair for Historical Excellence: Board Meeting #%s "
            "recorded at %s commits",
            state.board_meeting_count,
            state.total_commits,
        )
        return self.path

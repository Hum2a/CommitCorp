"""Annual shareholder letters from the CEO — every 100,000 commits."""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

from commit_machine.state import RuntimeState
from commit_machine.version_manager import VersionManager

logger = logging.getLogger(__name__)

LETTER_INTERVAL = 100_000


class ShareholderLetterGenerator:
    """Generates sincere CEO letters celebrating commit count growth."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.versions = VersionManager()

    def due(self, state: RuntimeState) -> bool:
        if state.total_commits < LETTER_INTERVAL:
            return False
        if state.total_commits % LETTER_INTERVAL != 0:
            return False
        return state.total_commits > state.last_shareholder_letter

    def generate(self, state: RuntimeState) -> str:
        version = self.versions.from_commits(state.total_commits)
        year_no = state.total_commits // LETTER_INTERVAL
        return f"""# Letter to Shareholders — Fiscal Chronology {year_no}

{date.today().isoformat()}

Dear Shareholders,

I am pleased to report another year of record-breaking repository growth
at CommitCorp. Our market leadership in historical expansion remains
uncontested, largely because no rational competitor has entered the category.

## Innovation

We continued to innovate within our core competency: appending carefully
worded emptiness to a text file and recording it in Git with ceremony
normally reserved for payment systems.

Platform {version.label} ({version.codename}) embodies our philosophy that
Semantic Versioning can be driven entirely by counting.

## Operational Excellence

Uptime of the chronological loop met internal expectations. Failure backoff
remained available as a strategic capability. Our compliance badges remain
unexplained and therefore impressive.

## Historical Expansion

Total historical density reached **{state.total_commits:,}** commits.
This is the metric against which we measure everything, including things
that are not this metric.

## Long-term Strategy

Our strategy is unchanged and infinite. We will build tomorrow's history
today, at a cadence governed by `sleep_seconds`, with occasional board
meetings to congratulate ourselves.

## Stakeholder Value

Stakeholder value accrued primarily as confusion, which our research
indicates is a durable moat.

## Enterprise Resilience

The platform recovers cleanly after restart, persists state, and refuses
to corrupt the repository. These are table stakes for a company whose
sole deliverable is history.

We reaffirm our unwavering commitment to **building tomorrow's history today**.

Sincerely,

**Absolutely Nobody**  
Chief Executive Officer  
CommitCorp Enterprise
"""

    def write(self, state: RuntimeState) -> Path | None:
        if not self.due(state):
            return None
        self.output_dir.mkdir(parents=True, exist_ok=True)
        year_no = state.total_commits // LETTER_INTERVAL
        path = (
            self.output_dir
            / f"SHAREHOLDER_LETTER_Y{year_no}_{state.total_commits}.md"
        )
        path.write_text(self.generate(state), encoding="utf-8")
        state.last_shareholder_letter = state.total_commits
        logger.info(
            "CommitCorp Executive Office: shareholder letter Y%s issued",
            year_no,
        )
        return path

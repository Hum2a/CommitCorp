"""Annual Reports — every 100,000 commits."""

from __future__ import annotations

import logging
import random
from datetime import date
from pathlib import Path

from commit_machine.executives import quote_for
from commit_machine.state import RuntimeState
from commit_machine.version_manager import VersionManager

logger = logging.getLogger(__name__)

ANNUAL_INTERVAL = 100_000


class AnnualReportGenerator:
    """Generates full annual reports treating the repo as a multinational."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.versions = VersionManager()

    def due(self, state: RuntimeState) -> bool:
        if state.total_commits < ANNUAL_INTERVAL:
            return False
        if state.total_commits % ANNUAL_INTERVAL != 0:
            return False
        return state.total_commits > state.last_annual

    def generate(self, state: RuntimeState) -> str:
        version = self.versions.from_commits(state.total_commits)
        year_no = state.total_commits // ANNUAL_INTERVAL
        rng = random.Random(state.total_commits + 7)
        return f"""# CommitCorp Annual Report — Year {year_no}

**Fiscal Chronology Marker:** {state.total_commits:,} commits  
**Date:** {date.today().isoformat()}  
**Platform Version:** {version.label} — {version.codename}

## Executive Summary

CommitCorp delivered another year of record-breaking repository growth.
Historical expansion remains the sole north-star metric, and it performed
exactly as designed: upward.

{quote_for("Chief Historical", rng)}

## Operational Performance

The Infinite Commit Machine operated continuously within approved sleep
parameters. Push synchronisation met policy. Achievements were unlocked on
schedule. No customers were acquired; none were required.

## Historical Expansion Metrics

* Total Commits: {state.total_commits:,}
* Session Continuity: Restored successfully after all restarts
* Newline Production: {state.total_newlines_produced:,}
* Longest Streak: {state.longest_streak:,}

## Repository Maturity

The repository exhibits multinational characteristics: departments,
committees, board minutes, and an unexplained lore file.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Someone asks why | Medium | Existential | FAQ |
| Meaning emerges | Low | High | Additional commits |
| Disk full | Low | High | Buy disk |

## Future Strategy

Build tomorrow's history today. Expand chronological surface area.
Maintain enterprise-grade pointlessness.

## Lessons Learned

1. History compounds.
2. Documentation outranks purpose.
3. The newline is the product.

— CommitCorp Enterprise
"""

    def write(self, state: RuntimeState) -> Path | None:
        if not self.due(state):
            return None
        self.output_dir.mkdir(parents=True, exist_ok=True)
        year_no = state.total_commits // ANNUAL_INTERVAL
        path = (
            self.output_dir
            / f"ANNUAL_REPORT_Y{year_no}_{state.total_commits}.md"
        )
        path.write_text(self.generate(state), encoding="utf-8")
        state.last_annual = state.total_commits
        logger.info(
            "Department of Historical Expansion: Annual Report Y%s published",
            year_no,
        )
        return path

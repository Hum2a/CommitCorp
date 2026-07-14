"""Quarterly Business Reviews — every 25,000 commits."""

from __future__ import annotations

import logging
import random
from datetime import date
from pathlib import Path

from commit_machine.executives import quote_for
from commit_machine.state import RuntimeState
from commit_machine.version_manager import VersionManager

logger = logging.getLogger(__name__)

QBR_INTERVAL = 25_000


class QuarterlyReportGenerator:
    """Generates corporate QBR documents."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.versions = VersionManager()

    def due(self, state: RuntimeState) -> bool:
        if state.total_commits < QBR_INTERVAL:
            return False
        if state.total_commits % QBR_INTERVAL != 0:
            return False
        return state.total_commits > state.last_qbr

    def generate(self, state: RuntimeState) -> str:
        version = self.versions.from_commits(state.total_commits)
        quarter_no = state.total_commits // QBR_INTERVAL
        return f"""# Quarterly Business Review — Q{quarter_no}

**CommitCorp Enterprise**  
**Date:** {date.today().isoformat()}  
**Platform Version:** {version.label}

## Executive Summary

Historical expansion exceeded expectations. The Infinite Commit Machine
delivered another {QBR_INTERVAL:,} units of chronological density with
unwavering operational discipline.

{quote_for("Chief Historical", random.Random(state.total_commits))}

## KPIs

| Metric | Status |
|--------|--------|
| Historical Growth | Exceeds Target |
| Commit Velocity | Sustainable |
| Repository Mood | {state.last_mood} |
| Business Value | Undetermined |
| Stakeholder Confusion | Industry-Leading |

## Historical Growth

Total commits stand at {state.total_commits:,}. Repository age multiplier
continues its responsible ascent.

## Business Value

Value creation remains abstract yet confidently asserted in all materials.

## Operational Excellence

Sleep intervals were honoured. Failure backoff was available and largely
unnecessary. Dashboards remained rectangular.

## Repository Maturity

Maturity model assessment: **Enterprise**. The codebase continues to
outperform the product concept.

## Technical Debt

Technical debt is primarily philosophical.

## Strategic Outlook

Further chronology anticipated. Roadmap remains infinite.

## Risks

Somebody may eventually ask why.

## Closing

The Chronological Operations Division recommends continued investment in
historical persistence.
"""

    def write(self, state: RuntimeState) -> Path | None:
        if not self.due(state):
            return None
        self.output_dir.mkdir(parents=True, exist_ok=True)
        quarter_no = state.total_commits // QBR_INTERVAL
        path = self.output_dir / f"QBR_Q{quarter_no}_{state.total_commits}.md"
        path.write_text(self.generate(state), encoding="utf-8")
        state.last_qbr = state.total_commits
        logger.info(
            "Office of Repository Excellence: QBR Q%s filed",
            quarter_no,
        )
        return path

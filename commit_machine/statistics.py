"""Persistent operational statistics for Historical Throughput Optimisation."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from commit_machine.state import RuntimeState, atomic_write_json

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Statistics:
    """Enterprise KPI ledger."""

    total_commits: int = 0
    session_commits: int = 0
    todays_commits: int = 0
    todays_date: str = field(default_factory=lambda: date.today().isoformat())
    runtime_seconds: float = 0.0
    average_commits_per_hour: float = 0.0
    average_pushes_per_day: float = 0.0
    commit_velocity: float = 0.0  # commits/hour session
    repository_age_multiplier: float = 1.0
    total_newline_production: int = 0
    entropy_score: float = 0.0
    longest_runtime_seconds: float = 0.0
    longest_streak: int = 0
    total_pushes: int = 0
    session_started_at: str = field(
        default_factory=lambda: _utc_now().isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Statistics:
        from dataclasses import fields as dc_fields

        known = {f.name for f in dc_fields(cls)}
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)


class StatisticsService:
    """Loads, updates, and persists statistics."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.stats = self._load()
        self._session_start = _utc_now()
        self.stats.session_commits = 0
        self.stats.session_started_at = self._session_start.isoformat()

    def _load(self) -> Statistics:
        if not self.path.exists():
            return Statistics()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return Statistics.from_dict(data)
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            logger.warning(
                "Historical Accuracy Board: statistics recovery degraded (%s)",
                exc,
            )
            return Statistics()

    def save(self) -> None:
        atomic_write_json(self.path, self.stats.to_dict())

    def _roll_day_if_needed(self) -> None:
        today = date.today().isoformat()
        if self.stats.todays_date != today:
            self.stats.todays_date = today
            self.stats.todays_commits = 0

    def record_commit(
        self,
        state: RuntimeState,
        *,
        newlines: int,
        entropy_score: float,
    ) -> Statistics:
        self._roll_day_if_needed()
        self.stats.total_commits = state.total_commits
        self.stats.session_commits = state.session_commits
        self.stats.todays_commits += 1
        self.stats.total_newline_production = state.total_newlines_produced
        self.stats.entropy_score = entropy_score
        self.stats.longest_streak = state.longest_streak
        self.stats.total_pushes = state.total_pushes

        elapsed = (_utc_now() - self._session_start).total_seconds()
        self.stats.runtime_seconds = elapsed
        if elapsed > self.stats.longest_runtime_seconds:
            self.stats.longest_runtime_seconds = elapsed
        state.longest_runtime_seconds = max(
            state.longest_runtime_seconds, elapsed
        )

        hours = max(elapsed / 3600.0, 1 / 3600.0)
        self.stats.commit_velocity = round(self.stats.session_commits / hours, 2)
        self.stats.average_commits_per_hour = self.stats.commit_velocity

        # Age multiplier: gentle growth with commit count
        self.stats.repository_age_multiplier = round(
            1.0 + (state.total_commits / 10000.0), 3
        )

        days = max(elapsed / 86400.0, 1 / 86400.0)
        self.stats.average_pushes_per_day = round(
            self.stats.total_pushes / days, 2
        )

        self.stats.total_newline_production += 0  # already synced from state
        _ = newlines  # accounted via state.total_newlines_produced
        self.save()
        return self.stats

    def snapshot(self) -> Statistics:
        self._roll_day_if_needed()
        elapsed = (_utc_now() - self._session_start).total_seconds()
        self.stats.runtime_seconds = elapsed
        return self.stats

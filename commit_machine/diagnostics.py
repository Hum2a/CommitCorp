"""Diagnostics, doctor mode, entropy peek, and million-commit forecasting."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from commit_machine.achievement_engine import AchievementEngine
from commit_machine.config import AppConfig
from commit_machine.entropy_engine import EntropyEngine
from commit_machine.git_manager import GitManager
from commit_machine.repository_health import RepositoryHealthService
from commit_machine.state import RuntimeState
from commit_machine.statistics import Statistics
from commit_machine.version_manager import VersionManager


@dataclass
class Forecast:
    target_commits: int
    remaining: int
    commits_per_hour: float
    eta: datetime | None
    narrative: str


class DiagnosticsService:
    """Enterprise diagnostic surfaces for CLI inspection commands."""

    def __init__(
        self,
        config: AppConfig,
        git: GitManager,
        state: RuntimeState,
        stats: Statistics,
    ) -> None:
        self.config = config
        self.git = git
        self.state = state
        self.stats = stats
        self.entropy = EntropyEngine()
        self.achievements = AchievementEngine()
        self.versions = VersionManager()

    def health_text(self) -> str:
        service = RepositoryHealthService(self.git, self.config.target_path())
        return service.assess().render()

    def doctor_text(self) -> str:
        health = self.health_text()
        version = self.versions.from_commits(self.state.total_commits)
        lines = [
            "=" * 50,
            "INFINITE COMMIT MACHINE - DOCTOR",
            "Enterprise Temporal Integrity Diagnostics",
            "=" * 50,
            "",
            health,
            "",
            f"Persisted Total Commits: {self.state.total_commits:,}",
            f"Git Rev-List Count: {self.git.commit_count():,}",
            f"Current Version: {version.label}",
            f"Career Title: {self.achievements.current_title(self.state.total_commits)}",
            f"Commits Since Push: {self.state.commits_since_push}",
            f"Push Every: {self.config.push_every}",
            f"Target File: {self.config.target_file}",
            f"State File: {self.config.state_file}",
            f"Dry-capable: yes",
            f"Config Path Exists: {Path('config.json').exists()}",
            "",
            "Recommendation: Continue historical expansion.",
            "=" * 50,
        ]
        return "\n".join(lines)

    def entropy_text(self) -> str:
        report = self.entropy.evaluate(
            total_commits=self.state.total_commits,
            revision=self.state.total_commits,
            mood=self.state.last_mood,
            session_commits=self.state.session_commits,
        )
        return (
            f"Entropy Score: {report.score}%\n"
            f"Classification: {report.level_label}\n"
            f"Historical Confidence: {report.historical_confidence}%\n"
            f"Git Satisfaction: {report.git_satisfaction}"
        )

    def forecast(self, target: int = 1_000_000) -> Forecast:
        remaining = max(0, target - self.state.total_commits)
        velocity = self.stats.commit_velocity or self.stats.average_commits_per_hour
        if velocity <= 0 and self.config.sleep_seconds > 0:
            # Theoretical velocity from sleep interval
            velocity = 3600.0 / self.config.sleep_seconds
        eta: datetime | None = None
        if remaining == 0:
            narrative = "Target historical density already achieved."
        elif velocity <= 0:
            narrative = "Insufficient velocity data; expansion rate undetermined."
        else:
            hours = remaining / velocity
            eta = datetime.now(timezone.utc) + timedelta(hours=hours)
            narrative = (
                f"At current chronological throughput ({velocity:.2f}/hr), "
                f"{target:,} commits projected for {eta.date().isoformat()}."
            )
        return Forecast(
            target_commits=target,
            remaining=remaining,
            commits_per_hour=round(velocity, 2),
            eta=eta,
            narrative=narrative,
        )

    def forecast_text(self, target: int = 1_000_000) -> str:
        f = self.forecast(target)
        eta = f.eta.date().isoformat() if f.eta else "Undetermined"
        return (
            f"Projected {f.target_commits:,} Commit Date\n"
            f"{eta}\n\n"
            f"Remaining: {f.remaining:,}\n"
            f"Velocity: {f.commits_per_hour} commits/hour\n\n"
            f"{f.narrative}"
        )

    def stats_text(self) -> str:
        s = self.stats
        return "\n".join(
            [
                "Enterprise Statistics Ledger",
                f"Total Commits: {s.total_commits:,}",
                f"Session Commits: {s.session_commits:,}",
                f"Today's Commits: {s.todays_commits:,}",
                f"Runtime (session): {s.runtime_seconds:,.1f}s",
                f"Avg Commits/Hour: {s.average_commits_per_hour}",
                f"Avg Pushes/Day: {s.average_pushes_per_day}",
                f"Commit Velocity: {s.commit_velocity}",
                f"Repository Age Multiplier: {s.repository_age_multiplier}",
                f"Total Newline Production: {s.total_newline_production:,}",
                f"Entropy Score: {s.entropy_score}",
                f"Longest Runtime: {s.longest_runtime_seconds:,.1f}s",
                f"Longest Streak: {s.longest_streak:,}",
            ]
        )

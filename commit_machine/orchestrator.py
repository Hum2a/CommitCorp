"""Main Historical Persistence Engine orchestration loop."""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from commit_machine.achievement_engine import AchievementEngine
from commit_machine.annual_reports import AnnualReportGenerator
from commit_machine.board_minutes import BoardMinutesGenerator
from commit_machine.commit_messages import CommitMessageProvider
from commit_machine.config import AppConfig, HotReloadConfig
from commit_machine.dashboard import Dashboard
from commit_machine.diagnostics import DiagnosticsService
from commit_machine.entropy_engine import EntropyEngine
from commit_machine.file_generator import FileGenerator
from commit_machine.git_manager import GitError, GitManager
from commit_machine.lore_engine import LoreEngine
from commit_machine.milestone import MilestoneTracker
from commit_machine.motivational_engine import MotivationalEngine
from commit_machine.quarterly_reports import QuarterlyReportGenerator
from commit_machine.release_manager import ReleaseManager
from commit_machine.repository_health import RepositoryHealthService
from commit_machine.scheduler import Scheduler
from commit_machine.shareholder_letter import ShareholderLetterGenerator
from commit_machine.state import RuntimeState, load_state, save_state
from commit_machine.statistics import StatisticsService
from commit_machine.version_manager import VersionManager

logger = logging.getLogger(__name__)


@dataclass
class CycleResult:
    committed: bool
    pushed: bool
    message: str
    revision: int
    celebration: str | None = None
    batch_size: int = 1
    messages: list[str] | None = None
    files: list[str] | None = None


class Orchestrator:
    """Coordinates one cycle or an infinite Continuous Chronological Integration run."""

    def __init__(
        self,
        config_path: Path,
        *,
        dry_run: bool = False,
        show_dashboard: bool | None = None,
        sleep_seconds_override: int | None = None,
        commits_per_cycle_override: int | None = None,
        target_files_override: list[str] | None = None,
    ) -> None:
        self.config_path = Path(config_path)
        self.hot = HotReloadConfig(self.config_path)
        self.dry_run = dry_run
        self._show_dashboard_override = show_dashboard
        self._sleep_seconds_override = sleep_seconds_override
        self._commits_per_cycle_override = commits_per_cycle_override
        self._target_files_override = target_files_override

        cfg = self.hot.config
        if sleep_seconds_override is not None:
            cfg.sleep_seconds = sleep_seconds_override
        if commits_per_cycle_override is not None:
            cfg.commits_per_cycle = commits_per_cycle_override
        if target_files_override is not None:
            cfg.target_files = list(target_files_override)
            cfg.target_file = target_files_override[0]
        self.repo_root = cfg.repo_path()
        self.git = GitManager(self.repo_root, dry_run=dry_run)
        self.state = load_state(cfg.state_path())
        self.stats_service = StatisticsService(cfg.stats_path())
        self.entropy = EntropyEngine()
        self.files = FileGenerator()
        self.messages = CommitMessageProvider(
            mode=cfg.commit_message_mode,
            start_index=self.state.message_index,
        )
        self.achievements = AchievementEngine()
        self.milestones = MilestoneTracker()
        self.versions = VersionManager()
        self.releases = ReleaseManager(self.repo_root)
        self.dashboard = Dashboard()
        self.motivation = MotivationalEngine()
        self.scheduler = Scheduler(
            cfg.sleep_seconds,
            cfg.failure_backoff_seconds,
            cfg.max_failure_backoff_seconds,
        )
        self.lore = LoreEngine(self.repo_root / "reports" / "lore.md")
        self.lore.ensure_header()
        self.board = BoardMinutesGenerator(self.repo_root / "BOARD_MINUTES.md")
        self.qbr = QuarterlyReportGenerator(
            self.repo_root / "reports" / "quarterly"
        )
        self.annual = AnnualReportGenerator(
            self.repo_root / "reports" / "annual"
        )
        self.shareholders = ShareholderLetterGenerator(
            self.repo_root / "reports" / "shareholder_letters"
        )
        self._rng = random.Random()

    @property
    def config(self) -> AppConfig:
        return self.hot.config

    def _diagnostics(self) -> DiagnosticsService:
        return DiagnosticsService(
            self.config,
            self.git,
            self.state,
            self.stats_service.snapshot(),
        )

    def run_forever(self) -> None:
        logger.info(
            "Department of Historical Expansion: entering infinite "
            "chronological loop. %s",
            self.motivation.motto(),
        )
        while True:
            try:
                self.run_once()
                self.scheduler.wait_success()
            except KeyboardInterrupt:
                logger.info(
                    "Chronological Operations Division: graceful shutdown "
                    "requested"
                )
                save_state(self.config.state_path(), self.state)
                raise
            except Exception:
                logger.exception(
                    "Temporal Compliance Team: cycle failure; applying backoff"
                )
                save_state(self.config.state_path(), self.state)
                self.scheduler.wait_failure()

    def _apply_runtime_overrides(self, cfg: AppConfig) -> AppConfig:
        if self._sleep_seconds_override is not None:
            cfg.sleep_seconds = self._sleep_seconds_override
        if self._commits_per_cycle_override is not None:
            cfg.commits_per_cycle = self._commits_per_cycle_override
        if self._target_files_override is not None:
            cfg.target_files = list(self._target_files_override)
            cfg.target_file = self._target_files_override[0]
        return cfg

    def run_once(self) -> CycleResult:
        """Run one batch: N separate commits to N different files, full pipeline each."""
        cfg = self._apply_runtime_overrides(self.hot.maybe_reload())
        self.scheduler.update_from_config(
            cfg.sleep_seconds,
            cfg.failure_backoff_seconds,
            cfg.max_failure_backoff_seconds,
        )
        self.messages.mode = cfg.commit_message_mode

        health = RepositoryHealthService(self.git, cfg.target_path()).assess()
        if not health.healthy:
            raise RuntimeError(
                f"Repository health {health.grade}; refusing cycle\n"
                f"{health.render()}"
            )

        git_count = self.git.commit_count()
        if git_count > self.state.total_commits:
            self.state.total_commits = git_count

        targets = cfg.batch_target_files()
        batch_messages: list[str] = []
        celebration: str | None = None
        last_entropy = self.entropy.evaluate(
            total_commits=self.state.total_commits,
            revision=self.state.total_commits,
            mood=self.state.last_mood,
            session_commits=self.state.session_commits,
        )
        last_revision = self.state.total_commits
        last_message = ""

        for relative_path in targets:
            previous_count = self.state.total_commits
            next_revision = self.state.total_commits + 1
            version = self.versions.from_commits(next_revision)
            entropy_report = self.entropy.evaluate(
                total_commits=next_revision,
                revision=next_revision,
                mood=self.state.last_mood,
                session_commits=self.state.session_commits,
            )
            last_entropy = entropy_report
            target_path = cfg.resolve_path(relative_path)
            content, mood = self.files.write(
                target_path,
                revision=next_revision,
                entropy=entropy_report,
                version=version.label,
                stream_name=Path(relative_path).stem,
            )
            self.state.last_mood = mood
            newlines = self.files.newline_count(content)

            message = self.messages.next_message(rng_choice=self._rng.choice)
            self.state.message_index = self.messages.index
            batch_messages.append(message)
            last_message = message
            last_revision = next_revision

            rel_target = str(target_path.relative_to(self.repo_root))
            if not self.dry_run:
                self.git.add(rel_target)
            committed = self.git.commit(message)
            if not committed and not self.dry_run:
                raise GitError(
                    f"Commit skipped for {rel_target}; chronology not advanced"
                )

            self.state.total_commits = next_revision
            self.state.session_commits += 1
            self.state.commits_since_push += 1
            self.state.current_streak += 1
            self.state.longest_streak = max(
                self.state.longest_streak, self.state.current_streak
            )
            self.state.total_newlines_produced += newlines
            self.state.last_commit_at = datetime.now(timezone.utc).isoformat()
            self.state.current_version = version.label

            self.stats_service.record_commit(
                self.state,
                newlines=newlines,
                entropy_score=entropy_report.score,
            )

            if cfg.enable_achievements:
                self.achievements.evaluate(self.state)
            if cfg.enable_milestones:
                self.milestones.check(self.state.total_commits)
            if cfg.enable_lore:
                self.lore.evaluate(self.state)
            if cfg.enable_board_minutes:
                self.board.append(self.state)
            if cfg.enable_quarterly_reports:
                self.qbr.write(self.state)
            if cfg.enable_annual_reports:
                self.annual.write(self.state)
                self.shareholders.write(self.state)

            bump = self.releases.process(
                self.state,
                previous_count,
                enabled=cfg.enable_releases,
            )
            if bump and bump.kind != "none":
                celebration = self.releases.celebration_text(
                    bump.current, self.state.total_commits
                )
                logger.info("\n%s", celebration)

            logger.info(
                "Enterprise Timestamp Office: batch unit complete "
                "(%s -> rev %s). %s",
                rel_target,
                next_revision,
                self.motivation.pep_talk(),
            )

        pushed = False
        if (
            cfg.push_enabled
            and self.state.commits_since_push >= cfg.push_every
        ):
            pushed = self.push_now()

        self._stage_sidecar_artefacts()
        save_state(cfg.state_path(), self.state)

        show_dash = (
            self._show_dashboard_override
            if self._show_dashboard_override is not None
            else cfg.enable_dashboard
        )
        if show_dash:
            self._refresh_dashboard(
                health.grade,
                last_entropy.historical_confidence,
                last_entropy.git_satisfaction,
                last_entropy.score,
            )

        logger.info(
            "Chronological Operations Division: batch of %s commits complete "
            "(head rev %s).",
            len(targets),
            last_revision,
        )
        return CycleResult(
            committed=True,
            pushed=pushed,
            message=last_message,
            revision=last_revision,
            celebration=celebration,
            batch_size=len(targets),
            messages=batch_messages,
            files=targets,
        )

    def _stage_sidecar_artefacts(self) -> None:
        """Best-effort stage of governance outputs for subsequent chronology."""
        if self.dry_run:
            return
        candidates = [
            "BOARD_MINUTES.md",
            "CHANGELOG.md",
            "README.md",
            "reports",
            "releases",
            "generated",
        ]
        existing = [
            c
            for c in candidates
            if (self.repo_root / c).exists()
        ]
        if not existing:
            return
        try:
            self.git.add(*existing)
        except GitError as exc:
            logger.debug("Sidecar staging deferred: %s", exc)

    def push_now(self) -> bool:
        try:
            ok = self.git.push()
            if ok:
                self.state.total_pushes += 1
                self.state.commits_since_push = 0
                save_state(self.config.state_path(), self.state)
            return ok
        except GitError as exc:
            logger.error(
                "Enterprise Timestamp Office: push failed - %s",
                exc,
            )
            return False

    def _refresh_dashboard(
        self,
        health: str,
        confidence: float,
        satisfaction: str,
        entropy: float,
    ) -> None:
        diag = self._diagnostics()
        forecast = diag.forecast(1_000_000)
        projected = (
            forecast.eta.date().isoformat() if forecast.eta else "Undetermined"
        )
        vm = self.dashboard.build(
            state=self.state,
            stats=self.stats_service.snapshot(),
            version=self.versions.from_commits(self.state.total_commits),
            health=health,
            confidence=confidence,
            satisfaction=satisfaction,
            entropy=entropy,
            push_every=self.config.push_every,
            projected_million=projected,
        )
        self.dashboard.display(vm, clear=True)

    def reset_state(self) -> None:
        cfg = self.config
        self.state = RuntimeState()
        save_state(cfg.state_path(), self.state)
        stats_path = cfg.stats_path()
        if stats_path.exists():
            stats_path.unlink()
        self.stats_service = StatisticsService(stats_path)
        logger.info(
            "Office of Repository Excellence: runtime state reset to greenfield"
        )

    def print_dashboard_once(self) -> None:
        entropy_report = self.entropy.evaluate(
            total_commits=self.state.total_commits,
            revision=self.state.total_commits,
            mood=self.state.last_mood,
            session_commits=self.state.session_commits,
        )
        health = RepositoryHealthService(
            self.git, self.config.target_path()
        ).assess()
        self._refresh_dashboard(
            health.grade,
            entropy_report.historical_confidence,
            entropy_report.git_satisfaction,
            entropy_report.score,
        )

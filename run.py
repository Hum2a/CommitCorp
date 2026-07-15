#!/usr/bin/env python3
"""Infinite Commit Machine — Enterprise CLI entrypoint.

CommitCorp Autonomous Historical Expansion Platform.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from commit_machine.config import ConfigError, load_config
from commit_machine.diagnostics import DiagnosticsService
from commit_machine.git_manager import GitManager
from commit_machine.logger import setup_logging
from commit_machine.orchestrator import Orchestrator
from commit_machine.state import load_state
from commit_machine.statistics import StatisticsService
from commit_machine.version_manager import VersionManager

# =============================================================================
# Chronological cadence — edit these to control batch timing and size.
# These override config.json when running via run.py.
# =============================================================================
SECONDS_BETWEEN_COMMITS = 0

# How many separate commits to create each cycle (each to a different file).
COMMITS_PER_CYCLE = 5

# One file per commit in the batch. Length should match COMMITS_PER_CYCLE.
TARGET_FILES = [
    "generated/history.txt",
    "generated/chronology.txt",
    "generated/ledger.txt",
    "generated/expansion.txt",
    "generated/continuity.txt",
]



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run.py",
        description=(
            "Infinite Commit Machine — Enterprise Historical Expansion Platform"
        ),
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to enterprise configuration JSON",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Execute a single chronological cycle and exit",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Display the enterprise statistics ledger",
    )
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Render the live operational dashboard once",
    )
    parser.add_argument(
        "--doctor",
        action="store_true",
        help="Run Temporal Integrity diagnostics",
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Assess repository health",
    )
    parser.add_argument(
        "--entropy",
        action="store_true",
        help="Display current entropy assessment",
    )
    parser.add_argument(
        "--forecast",
        action="store_true",
        help="Project the one-million-commit date",
    )
    parser.add_argument(
        "--celebrate",
        action="store_true",
        help="Display a ceremonial release celebration for the current version",
    )
    parser.add_argument(
        "--push-now",
        action="store_true",
        help="Synchronise the remote chronological ledger immediately",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate chronology without mutating Git history",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset persisted runtime state to greenfield",
    )
    return parser


def _diag_from_config(config_path: Path) -> DiagnosticsService:
    cfg = load_config(config_path)
    cfg.sleep_seconds = SECONDS_BETWEEN_COMMITS
    git = GitManager(cfg.repo_path())
    state = load_state(cfg.state_path())
    stats = StatisticsService(cfg.stats_path()).snapshot()
    return DiagnosticsService(cfg, git, state, stats)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config_path = Path(args.config)

    try:
        cfg = load_config(config_path)
    except ConfigError as exc:
        print(f"Configuration compliance failure: {exc}", file=sys.stderr)
        return 2

    cfg.sleep_seconds = SECONDS_BETWEEN_COMMITS
    setup_logging(cfg.log_path())

    # Read-only / diagnostic commands (no orchestrator loop)
    if args.stats or args.doctor or args.health or args.entropy or args.forecast:
        diag = _diag_from_config(config_path)
        if args.doctor:
            print(diag.doctor_text())
        if args.health:
            print(diag.health_text())
        if args.entropy:
            print(diag.entropy_text())
        if args.forecast:
            print(diag.forecast_text())
        if args.stats:
            print(diag.stats_text())
        return 0

    orch = Orchestrator(
        config_path,
        dry_run=args.dry_run,
        show_dashboard=True if args.dashboard and not args.once else None,
        sleep_seconds_override=SECONDS_BETWEEN_COMMITS,
        commits_per_cycle_override=COMMITS_PER_CYCLE,
        target_files_override=TARGET_FILES,
    )

    if args.reset:
        orch.reset_state()
        print("Runtime state reset to greenfield baseline.")
        return 0

    if args.celebrate:
        version = VersionManager().from_commits(orch.state.total_commits)
        print(
            orch.releases.celebration_text(version, orch.state.total_commits)
        )
        return 0

    if args.push_now:
        ok = orch.push_now()
        print(
            "Remote ledger synchronised."
            if ok
            else "Push deferred or failed; consult logs."
        )
        return 0 if ok else 1

    if args.dashboard and not args.once:
        orch.print_dashboard_once()
        return 0

    if args.once or args.dry_run:
        # --dry-run alone implies a single simulated cycle unless forever wanted;
        # forever + dry-run is allowed via no --once, but default dry-run to once
        # for safety when only --dry-run is passed.
        if args.dry_run and not args.once and _only_dry_run(argv):
            result = orch.run_once()
            _print_cycle_result(result, dry_run=True)
            return 0
        if args.once:
            result = orch.run_once()
            _print_cycle_result(result, dry_run=args.dry_run)
            return 0

    # Infinite loop
    try:
        orch.run_forever()
    except KeyboardInterrupt:
        print("\nHistorical expansion suspended by operator.")
        return 0
    return 0


def _only_dry_run(argv: list[str] | None) -> bool:
    """True when user passed --dry-run without --once (safe default: single cycle)."""
    tokens = list(argv or sys.argv[1:])
    return "--dry-run" in tokens and "--once" not in tokens


def _print_cycle_result(result, *, dry_run: bool = False) -> None:
    prefix = "[DRY-RUN] " if dry_run else ""
    print(
        f"{prefix}Batch complete: {result.batch_size} commit(s); "
        f"head revision {result.revision}"
    )
    files = result.files or []
    messages = result.messages or [result.message]
    for index, message in enumerate(messages):
        target = files[index] if index < len(files) else "?"
        print(f"  {index + 1}. {target} -> {message}")
    if result.celebration:
        print(result.celebration)


if __name__ == "__main__":
    raise SystemExit(main())

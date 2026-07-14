"""Repository health checks for Temporal Integrity System readiness."""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from commit_machine.git_manager import GitManager

logger = logging.getLogger(__name__)


@dataclass
class HealthCheck:
    name: str
    ok: bool
    detail: str


@dataclass
class HealthReport:
    checks: list[HealthCheck] = field(default_factory=list)

    @property
    def healthy(self) -> bool:
        return all(c.ok for c in self.checks)

    @property
    def grade(self) -> str:
        if not self.checks:
            return "Unknown"
        passed = sum(1 for c in self.checks if c.ok)
        ratio = passed / len(self.checks)
        if ratio == 1.0:
            return "Excellent"
        if ratio >= 0.8:
            return "Good"
        if ratio >= 0.5:
            return "Degraded"
        return "Critical"

    def render(self) -> str:
        lines = [
            "Repository Health Assessment",
            f"Overall: {self.grade}",
            "",
        ]
        for check in self.checks:
            mark = "PASS" if check.ok else "FAIL"
            lines.append(f"[{mark}] {check.name}: {check.detail}")
        return "\n".join(lines)


class RepositoryHealthService:
    """Performs non-destructive readiness checks before chronology cycles."""

    def __init__(self, git: GitManager, target_file: Path) -> None:
        self.git = git
        self.target_file = target_file

    def assess(self) -> HealthReport:
        report = HealthReport()
        git_ok = self.git.is_repository()
        report.checks.append(
            HealthCheck(
                "Git Work Tree",
                git_ok,
                "Inside a Git work tree" if git_ok else "Not a Git repository",
            )
        )

        git_bin = shutil.which("git") is not None
        report.checks.append(
            HealthCheck(
                "Git Binary",
                git_bin,
                "git executable located" if git_bin else "git not found on PATH",
            )
        )

        parent = self.target_file.parent
        try:
            parent.mkdir(parents=True, exist_ok=True)
            writable = parent.exists() and os_writable(parent)
        except OSError as exc:
            writable = False
            detail_w = str(exc)
        else:
            detail_w = f"Writable path {parent}"

        report.checks.append(
            HealthCheck("Target Path Writable", writable, detail_w)
        )

        disk = shutil.disk_usage(self.git.repo_root)
        free_ok = disk.free > 10 * 1024 * 1024
        report.checks.append(
            HealthCheck(
                "Disk Capacity",
                free_ok,
                f"{disk.free // (1024 * 1024)} MiB free",
            )
        )

        if git_ok:
            branch = self.git.current_branch()
            report.checks.append(
                HealthCheck(
                    "Branch Identity",
                    branch not in {"", "unknown"},
                    f"Branch: {branch}",
                )
            )
            remote = self.git.has_remote()
            report.checks.append(
                HealthCheck(
                    "Remote Configuration",
                    True,  # advisory only — missing remote is not unhealthy
                    "Remote configured" if remote else "No remote (push deferred)",
                )
            )

        if report.healthy:
            logger.debug(
                "Temporal Compliance Team: repository health Excellent"
            )
        else:
            logger.warning(
                "Temporal Compliance Team: repository health %s",
                report.grade,
            )
        return report


def os_writable(path: Path) -> bool:
    probe = path / ".icm_write_probe"
    try:
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except OSError:
        return False

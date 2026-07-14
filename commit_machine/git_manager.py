"""Safe Git operations for the Distributed Chronological Ledger."""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_AUTHOR_NAME = "Infinite Commit Machine"
DEFAULT_AUTHOR_EMAIL = "icm@commitcorp.enterprise.invalid"


class GitError(Exception):
    """Raised when a Git operation fails enterprise safety checks."""


@dataclass
class GitResult:
    stdout: str
    stderr: str
    returncode: int


class GitManager:
    """Thin, conservative wrapper around git subprocess calls.

    Never force-pushes. Never rewrites history. Prefer abort over corruption.
    Never mutates git config; identity overrides are passed per-invocation.
    """

    def __init__(self, repo_root: Path, *, dry_run: bool = False) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.dry_run = dry_run

    def _run(
        self,
        args: list[str],
        *,
        check: bool = True,
        allow_dry: bool = False,
        with_identity: bool = False,
    ) -> GitResult:
        if self.dry_run and not allow_dry:
            logger.info("[DRY-RUN] git %s", " ".join(args))
            return GitResult(stdout="", stderr="", returncode=0)

        prefix: list[str] = []
        if with_identity:
            prefix = [
                "-c",
                f"user.name={DEFAULT_AUTHOR_NAME}",
                "-c",
                f"user.email={DEFAULT_AUTHOR_EMAIL}",
            ]

        completed = subprocess.run(
            ["git", *prefix, *args],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        result = GitResult(
            stdout=completed.stdout.strip(),
            stderr=completed.stderr.strip(),
            returncode=completed.returncode,
        )
        if check and result.returncode != 0:
            raise GitError(
                f"git {' '.join(args)} failed ({result.returncode}): "
                f"{result.stderr or result.stdout}"
            )
        return result

    def is_repository(self) -> bool:
        result = self._run(
            ["rev-parse", "--is-inside-work-tree"],
            check=False,
            allow_dry=True,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"

    def commit_count(self) -> int:
        result = self._run(
            ["rev-list", "--count", "HEAD"],
            check=False,
            allow_dry=True,
        )
        if result.returncode != 0:
            return 0
        try:
            return int(result.stdout.strip())
        except ValueError:
            return 0

    def status_porcelain(self) -> str:
        return self._run(["status", "--porcelain"], allow_dry=True).stdout

    def has_remote(self) -> bool:
        result = self._run(["remote"], check=False, allow_dry=True)
        return bool(result.stdout.strip())

    def current_branch(self) -> str:
        result = self._run(
            ["rev-parse", "--abbrev-ref", "HEAD"],
            check=False,
            allow_dry=True,
        )
        return result.stdout.strip() or "unknown"

    def has_identity(self) -> bool:
        name = self._run(
            ["config", "--get", "user.name"], check=False, allow_dry=True
        ).stdout
        email = self._run(
            ["config", "--get", "user.email"], check=False, allow_dry=True
        ).stdout
        return bool(name and email)

    def add(self, *paths: str) -> None:
        if not paths:
            raise GitError("No paths provided for staging")
        self._run(["add", "--", *paths])

    def commit(self, message: str) -> bool:
        """Create a commit. Returns False if there was nothing to commit."""
        if self.dry_run:
            logger.info("[DRY-RUN] would commit: %s", message)
            return True

        status = self.status_porcelain()
        if not status:
            logger.warning(
                "Version Control Steering Committee: nothing to commit; "
                "chronology unchanged"
            )
            return False

        # Prefer existing identity; otherwise use per-invocation -c overrides
        # without writing to .git/config.
        use_identity = not self.has_identity()
        self._run(["commit", "-m", message], with_identity=use_identity)
        logger.info(
            "Department of Historical Expansion: chronology recorded - %s",
            message,
        )
        return True

    def push(self, remote: str = "origin", branch: str | None = None) -> bool:
        """Push to remote. Never force. Returns False if no remote configured."""
        if self.dry_run:
            logger.info("[DRY-RUN] would push to %s", remote)
            return True

        if not self.has_remote():
            logger.warning(
                "Enterprise Timestamp Office: no remote configured; "
                "push deferred"
            )
            return False

        target_branch = branch or self.current_branch()
        if target_branch in {"HEAD", "unknown"}:
            raise GitError("Unable to determine branch for push")

        self._run(["push", remote, target_branch])
        logger.info(
            "Chronological Operations Division: remote ledger synchronised "
            "(%s/%s)",
            remote,
            target_branch,
        )
        return True

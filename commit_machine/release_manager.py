"""Enterprise release orchestration: CHANGELOG, README, notes, celebrations."""

from __future__ import annotations

import json
import logging
import re
from datetime import date
from pathlib import Path

from commit_machine.press_release import PressReleaseGenerator
from commit_machine.state import RuntimeState
from commit_machine.version_manager import ReleaseBump, VersionInfo, VersionManager

logger = logging.getLogger(__name__)


class ReleaseManager:
    """Handles SemVer bumps derived from commit density."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.versions = VersionManager()
        self.press = PressReleaseGenerator()
        self.changelog_path = repo_root / "CHANGELOG.md"
        self.readme_path = repo_root / "README.md"
        self.releases_dir = repo_root / "releases"

    def process(
        self,
        state: RuntimeState,
        previous_count: int,
        *,
        enabled: bool = True,
    ) -> ReleaseBump | None:
        if not enabled:
            return None
        bump = self.versions.detect_bump(previous_count, state.total_commits)
        if bump.kind == "none":
            state.current_version = bump.current.label
            return bump

        self._append_changelog(bump.current, bump.kind)
        self._update_readme_version(bump.current)
        notes_path = self._write_release_notes(bump.current, state.total_commits)
        meta_path = self._write_metadata(bump.current, state.total_commits, bump.kind)
        if bump.kind == "major":
            self.press.write(
                self.releases_dir, bump.current, state.total_commits
            )

        state.current_version = bump.current.label
        if bump.kind == "major":
            state.last_major = state.total_commits
        elif bump.kind == "minor":
            state.last_minor = state.total_commits
        else:
            state.last_patch = state.total_commits

        logger.info(
            "Version Control Steering Committee: %s release %s (%s)",
            bump.kind,
            bump.current.label,
            notes_path.name,
        )
        _ = meta_path
        return bump

    def _append_changelog(self, version: VersionInfo, kind: str) -> None:
        entry = (
            f"## {version.label}\n\n"
            f"*{date.today().isoformat()} — {version.codename}*\n\n"
            f"### Added\n\n"
            f"Additional newline.\n\n"
            f"### Improved\n\n"
            f"Repository is now older.\n\n"
            f"### Performance\n\n"
            f"Historical throughput increased by 0%.\n\n"
            f"### Fixed\n\n"
            f"Nothing.\n\n"
            f"### Notes\n\n"
            f"This {kind} release was authorised by commit density policy.\n"
        )
        if self.changelog_path.exists():
            existing = self.changelog_path.read_text(encoding="utf-8")
        else:
            existing = (
                "# Changelog\n\n"
                "All notable historical expansion is documented herein.\n"
            )

        marker = "\n## "
        idx = existing.find(marker)
        if idx == -1:
            new_content = existing.rstrip() + "\n\n" + entry + "\n"
        else:
            new_content = (
                existing[:idx].rstrip() + "\n\n" + entry + existing[idx:]
            )
        self.changelog_path.write_text(new_content, encoding="utf-8")

    def _update_readme_version(self, version: VersionInfo) -> None:
        if not self.readme_path.exists():
            return
        text = self.readme_path.read_text(encoding="utf-8")
        pattern = r"(<!-- ICM_VERSION -->).*?(<!-- /ICM_VERSION -->)"
        replacement = (
            f"<!-- ICM_VERSION -->**{version.label}** — {version.codename}"
            f"<!-- /ICM_VERSION -->"
        )
        if re.search(pattern, text, flags=re.DOTALL):
            text = re.sub(pattern, replacement, text, flags=re.DOTALL)
        else:
            # Prepend version badge line after first heading
            lines = text.splitlines()
            if lines:
                lines.insert(
                    1,
                    f"\n<!-- ICM_VERSION -->**{version.label}** — "
                    f"{version.codename}<!-- /ICM_VERSION -->\n",
                )
                text = "\n".join(lines)
        self.readme_path.write_text(text, encoding="utf-8")

    def _write_release_notes(
        self, version: VersionInfo, total_commits: int
    ) -> Path:
        self.releases_dir.mkdir(parents=True, exist_ok=True)
        path = self.releases_dir / f"RELEASE_NOTES_{version.label}.md"
        path.write_text(
            f"""# Release Notes — {version.label}

**Codename:** {version.codename}  
**Historical Density:** {total_commits:,}  
**Date:** {date.today().isoformat()}

## Highlights

* Repository is older
* Chronology remains continuous
* Stakeholders remain confused

## Upgrade Guide

No upgrade required. Continue existing.
""",
            encoding="utf-8",
        )
        return path

    def _write_metadata(
        self, version: VersionInfo, total_commits: int, kind: str
    ) -> Path:
        self.releases_dir.mkdir(parents=True, exist_ok=True)
        path = self.releases_dir / f"release_{version.label}.json"
        path.write_text(
            json.dumps(
                {
                    "version": version.label,
                    "codename": version.codename,
                    "kind": kind,
                    "total_commits": total_commits,
                    "date": date.today().isoformat(),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return path

    def celebration_text(self, version: VersionInfo, total_commits: int) -> str:
        bar = "=" * 49
        return "\n".join(
            [
                bar,
                "ENTERPRISE RELEASE CELEBRATION",
                version.label,
                version.codename,
                bar,
                f"Commits: {total_commits:,}",
                "Champagne: metaphorical",
                "Applause: mandatory",
                bar,
            ]
        )

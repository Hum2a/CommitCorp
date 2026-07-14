"""Corporate press releases for major platform versions."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from commit_machine.version_manager import VersionInfo


class PressReleaseGenerator:
    """Produces FOR IMMEDIATE RELEASE documents on major bumps."""

    def generate(self, version: VersionInfo, total_commits: int) -> str:
        today = date.today().isoformat()
        return f"""FOR IMMEDIATE RELEASE

Infinite Commit Machine Announces {version.label}

{today} — CommitCorp Enterprise

The Infinite Commit Machine today announced another major milestone in
enterprise historical preservation with the release of {version.label}
({version.codename}).

"This release represents our continued investment in scalable chronological
infrastructure," said absolutely nobody.

New features include:

* Expanded historical continuity
* Enterprise newline generation
* Best-in-class timestamp delivery
* Repository growth optimisation
* Reinforced temporal integrity controls

At the time of announcement, the platform had recorded {total_commits:,}
units of historical density.

About CommitCorp

CommitCorp builds tomorrow's Git history today. History is our primary
deliverable.

###
"""

    def write(
        self,
        releases_dir: Path,
        version: VersionInfo,
        total_commits: int,
    ) -> Path:
        releases_dir.mkdir(parents=True, exist_ok=True)
        path = releases_dir / f"PRESS_RELEASE_{version.label}.md"
        path.write_text(
            self.generate(version, total_commits), encoding="utf-8"
        )
        return path

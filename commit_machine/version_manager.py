"""Semantic versioning derived entirely from commit history."""

from __future__ import annotations

from dataclasses import dataclass

MAJOR_EVERY = 100_000
MINOR_EVERY = 10_000
PATCH_EVERY = 1_000

MAJOR_CODENAMES: dict[int, str] = {
    0: "Pre-Historical Bootstrap",
    1: "Historical Persistence Platform",
    2: "Enterprise Chronology Initiative",
    3: "Temporal Infrastructure Modernisation",
    4: "Repository Excellence Framework",
    5: "Strategic Historical Optimisation",
    6: "Continuous Chronological Integration",
    7: "Distributed Chronological Ledger",
    8: "Autonomous Historical Expansion",
    9: "Version Continuity Platform",
    10: "Supreme Temporal Dominion",
}


@dataclass(frozen=True)
class VersionInfo:
    major: int
    minor: int
    patch: int

    @property
    def label(self) -> str:
        return f"v{self.major}.{self.minor}.{self.patch}"

    @property
    def codename(self) -> str:
        if self.major in MAJOR_CODENAMES:
            return MAJOR_CODENAMES[self.major]
        return f"Epoch {self.major} Chronology Programme"


@dataclass(frozen=True)
class ReleaseBump:
    previous: VersionInfo
    current: VersionInfo
    kind: str  # major | minor | patch | none


class VersionManager:
    """Maps total commits to SemVer using CommitCorp release policy."""

    def from_commits(self, total_commits: int) -> VersionInfo:
        n = max(0, total_commits)
        major = n // MAJOR_EVERY
        minor = (n % MAJOR_EVERY) // MINOR_EVERY
        patch = (n % MINOR_EVERY) // PATCH_EVERY
        return VersionInfo(major=major, minor=minor, patch=patch)

    def detect_bump(self, previous_count: int, current_count: int) -> ReleaseBump:
        prev = self.from_commits(previous_count)
        curr = self.from_commits(current_count)
        if curr == prev:
            return ReleaseBump(prev, curr, "none")
        if curr.major != prev.major:
            return ReleaseBump(prev, curr, "major")
        if curr.minor != prev.minor:
            return ReleaseBump(prev, curr, "minor")
        return ReleaseBump(prev, curr, "patch")

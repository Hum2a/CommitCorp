"""Milestone detection for Strategic Repository Expansion events."""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Milestone:
    threshold: int
    name: str
    category: str


# Core numeric milestones (achievements cover titles; these are operational)
NUMERIC_MILESTONES: tuple[Milestone, ...] = (
    Milestone(1, "First Chronological Record", "ops"),
    Milestone(10, "Decimal Persistence", "ops"),
    Milestone(100, "Century of History", "ops"),
    Milestone(1_000, "Millennial Timestamp", "ops"),
    Milestone(5_000, "Board-Eligible Density", "governance"),
    Milestone(10_000, "Minor Release Horizon", "release"),
    Milestone(25_000, "Quarterly Business Review Gate", "governance"),
    Milestone(50_000, "Second Epoch Threshold", "lore"),
    Milestone(100_000, "Major Release Horizon", "release"),
    Milestone(250_000, "Enterprise Density", "lore"),
    Milestone(500_000, "Council Acknowledgement", "lore"),
    Milestone(1_000_000, "First Great Expansion", "lore"),
    Milestone(2_000_000, "The Repository Remembers", "lore"),
)


class MilestoneTracker:
    """Reports when a cycle lands exactly on a milestone threshold."""

    def __init__(self) -> None:
        self._announced: set[int] = set()

    def check(self, total_commits: int) -> list[Milestone]:
        hit: list[Milestone] = []
        for milestone in NUMERIC_MILESTONES:
            if (
                total_commits == milestone.threshold
                and milestone.threshold not in self._announced
            ):
                self._announced.add(milestone.threshold)
                hit.append(milestone)
                logger.info(
                    "Version Control Steering Committee: milestone reached - "
                    "%s (%s)",
                    milestone.name,
                    milestone.threshold,
                )
        return hit

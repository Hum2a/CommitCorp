"""Achievement unlocks for career progression in Historical Expansion."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from commit_machine.state import RuntimeState

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Achievement:
    threshold: int
    title: str
    code: str


ACHIEVEMENTS: tuple[Achievement, ...] = (
    Achievement(1, "Committed to the Mission", "mission"),
    Achievement(100, "Intern", "intern"),
    Achievement(500, "Junior Repository Engineer", "junior"),
    Achievement(1_000, "Repository Associate", "associate"),
    Achievement(5_000, "Senior Historical Specialist", "senior"),
    Achievement(10_000, "Principal Commit Engineer", "principal"),
    Achievement(50_000, "Director of Repository Growth", "director"),
    Achievement(100_000, "Vice President of Historical Operations", "vp"),
    Achievement(500_000, "Chief Executive of Git", "ceo_git"),
    Achievement(1_000_000, "Supreme Keeper of Version Control", "supreme"),
)


class AchievementEngine:
    """Unlocks achievements when commit thresholds are crossed."""

    def evaluate(self, state: RuntimeState) -> list[Achievement]:
        newly: list[Achievement] = []
        unlocked = set(state.unlocked_achievements)
        for achievement in ACHIEVEMENTS:
            if (
                state.total_commits >= achievement.threshold
                and achievement.code not in unlocked
            ):
                unlocked.add(achievement.code)
                newly.append(achievement)
                logger.info(
                    "Office of Repository Excellence: achievement unlocked - "
                    "%s (%s)",
                    achievement.title,
                    achievement.threshold,
                )
        state.unlocked_achievements = sorted(unlocked)
        return newly

    def current_title(self, total_commits: int) -> str:
        title = "Applicant"
        for achievement in ACHIEVEMENTS:
            if total_commits >= achievement.threshold:
                title = achievement.title
        return title

    def all_for_display(self, state: RuntimeState) -> list[tuple[Achievement, bool]]:
        unlocked = set(state.unlocked_achievements)
        return [(a, a.code in unlocked) for a in ACHIEVEMENTS]

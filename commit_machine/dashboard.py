"""Live terminal dashboard for the Enterprise Historical Expansion Platform."""

from __future__ import annotations

import sys
from dataclasses import dataclass

from commit_machine.achievement_engine import AchievementEngine
from commit_machine.motivational_engine import MotivationalEngine
from commit_machine.state import RuntimeState
from commit_machine.statistics import Statistics
from commit_machine.version_manager import VersionInfo


@dataclass
class DashboardViewModel:
    status: str
    health: str
    current_commit: int
    push_queue: int
    push_every: int
    mood: str
    historical_confidence: float
    enterprise_compliance: str
    projected_million: str
    git_satisfaction: str
    version: VersionInfo
    title: str
    entropy: float
    motto: str


class Dashboard:
    """Renders and refreshes a ceremonial ANSI dashboard."""

    def __init__(self) -> None:
        self._achievements = AchievementEngine()
        self._motivation = MotivationalEngine()

    def build(
        self,
        *,
        state: RuntimeState,
        stats: Statistics,
        version: VersionInfo,
        health: str,
        confidence: float,
        satisfaction: str,
        entropy: float,
        push_every: int,
        projected_million: str,
        status: str = "Operational",
    ) -> DashboardViewModel:
        return DashboardViewModel(
            status=status,
            health=health,
            current_commit=state.total_commits,
            push_queue=state.commits_since_push,
            push_every=push_every,
            mood=state.last_mood,
            historical_confidence=confidence,
            enterprise_compliance="Certified",
            projected_million=projected_million,
            git_satisfaction=satisfaction,
            version=version,
            title=self._achievements.current_title(state.total_commits),
            entropy=entropy,
            motto=self._motivation.motto(),
        )

    def render(self, vm: DashboardViewModel) -> str:
        width = 49
        bar = "=" * width
        remaining_push = max(0, vm.push_every - vm.push_queue)
        lines = [
            bar,
            "INFINITE COMMIT MACHINE",
            "Enterprise Historical Expansion Platform",
            bar,
            "",
            "Status",
            vm.status,
            "",
            "Repository Health",
            vm.health,
            "",
            "Current Commit",
            f"{vm.current_commit:,}",
            "",
            "Push Queue",
            f"{vm.push_queue} / {vm.push_every}  ({remaining_push} until synchronisation)",
            "",
            "Repository Mood",
            vm.mood,
            "",
            "Historical Confidence",
            f"{vm.historical_confidence}%",
            "",
            "Entropy Level",
            f"{vm.entropy:.0f}%",
            "",
            "Enterprise Compliance",
            vm.enterprise_compliance,
            "",
            "Projected One Million Commit Date",
            vm.projected_million,
            "",
            "Git Satisfaction",
            vm.git_satisfaction,
            "",
            "Career Title",
            vm.title,
            "",
            "Current Version",
            f"{vm.version.label} - {vm.version.codename}",
            "",
            "Company Motto",
            vm.motto,
            "",
            bar,
        ]
        return "\n".join(lines)

    def display(self, vm: DashboardViewModel, *, clear: bool = True) -> None:
        text = self.render(vm)
        if clear and sys.stdout.isatty():
            # ANSI clear screen + home
            sys.stdout.write("\033[2J\033[H")
        sys.stdout.write(text + "\n")
        sys.stdout.flush()

    def celebrate(self, version: VersionInfo, total_commits: int) -> str:
        bar = "=" * 49
        return "\n".join(
            [
                bar,
                "RELEASE CELEBRATION",
                f"{version.label}",
                version.codename,
                bar,
                f"Historical Density: {total_commits:,} commits",
                "The board congratulates all departments.",
                "Champagne is metaphorical.",
                bar,
            ]
        )

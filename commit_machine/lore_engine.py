"""Repository lore — unexplained internal mythology."""

from __future__ import annotations

import logging
from pathlib import Path

from commit_machine.state import RuntimeState

logger = logging.getLogger(__name__)

LORE_EVENTS: dict[int, str] = {
    50_000: "The Repository entered the Second Epoch.",
    250_000: "Historical density has reached enterprise levels.",
    500_000: "The Council of Commits acknowledges this achievement.",
    1_000_000: "The First Great Expansion has concluded.",
    2_000_000: "The Repository remembers.",
}


class LoreEngine:
    """Appends lore entries when thresholds are crossed. Never explains them."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def evaluate(self, state: RuntimeState) -> list[str]:
        unlocked = set(state.unlocked_lore)
        newly: list[str] = []
        for threshold, text in sorted(LORE_EVENTS.items()):
            code = str(threshold)
            if state.total_commits >= threshold and code not in unlocked:
                unlocked.add(code)
                newly.append(text)
                self._append(threshold, text)
                logger.info(
                    "Historical Accuracy Board: lore inscribed (%s)",
                    threshold,
                )
        state.unlocked_lore = sorted(unlocked)
        return newly

    def _append(self, threshold: int, text: str) -> None:
        self.ensure_header()
        block = (
            f"\n## Threshold {threshold:,}\n\n"
            f"{text}\n\n"
            f"— Recorded without commentary.\n"
        )
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(block)

    def ensure_header(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists() or self.path.stat().st_size == 0:
            self.path.write_text(
                "# Repository Lore\n\n"
                "Internal mythology of the Infinite Commit Machine.\n"
                "Do not explain.\n",
                encoding="utf-8",
            )

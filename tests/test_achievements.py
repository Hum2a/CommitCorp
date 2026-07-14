"""Achievement threshold tests."""

from __future__ import annotations

import unittest

from commit_machine.achievement_engine import AchievementEngine
from commit_machine.state import RuntimeState


class AchievementTests(unittest.TestCase):
    def test_unlock_sequence(self) -> None:
        engine = AchievementEngine()
        state = RuntimeState(total_commits=1)
        newly = engine.evaluate(state)
        self.assertEqual(len(newly), 1)
        self.assertEqual(newly[0].title, "Committed to the Mission")
        newly2 = engine.evaluate(state)
        self.assertEqual(newly2, [])

    def test_current_title(self) -> None:
        engine = AchievementEngine()
        self.assertEqual(engine.current_title(0), "Applicant")
        self.assertEqual(engine.current_title(100), "Intern")
        self.assertEqual(
            engine.current_title(1_000_000),
            "Supreme Keeper of Version Control",
        )


if __name__ == "__main__":
    unittest.main()

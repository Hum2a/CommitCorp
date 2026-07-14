"""State persistence tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from commit_machine.state import RuntimeState, load_state, save_state


class StateTests(unittest.TestCase):
    def test_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"
            state = RuntimeState(total_commits=123, last_mood="Agile")
            save_state(path, state)
            loaded = load_state(path)
            self.assertEqual(loaded.total_commits, 123)
            self.assertEqual(loaded.last_mood, "Agile")

    def test_missing_returns_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing.json"
            state = load_state(path)
            self.assertEqual(state.total_commits, 0)


if __name__ == "__main__":
    unittest.main()

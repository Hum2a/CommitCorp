"""History file generation tests."""

from __future__ import annotations

import random
import tempfile
import unittest
from pathlib import Path

from commit_machine.entropy_engine import EntropyEngine
from commit_machine.file_generator import FileGenerator


class FileGeneratorTests(unittest.TestCase):
    def test_render_contains_core_fields(self) -> None:
        gen = FileGenerator(rng=random.Random(0))
        entropy = EntropyEngine().evaluate(
            total_commits=42,
            revision=42,
            mood="Visionary",
            session_commits=1,
        )
        text = gen.render(revision=42, entropy=entropy, mood="Visionary")
        self.assertIn("Repository Expansion Report", text)
        self.assertIn("42", text)
        self.assertIn("Visionary", text)
        self.assertIn("Historical Confidence", text)

    def test_write(self) -> None:
        gen = FileGenerator(rng=random.Random(1))
        entropy = EntropyEngine().evaluate(
            total_commits=1,
            revision=1,
            mood="Enterprise",
            session_commits=1,
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "history.txt"
            content, mood = gen.write(path, revision=1, entropy=entropy)
            self.assertTrue(path.exists())
            self.assertEqual(path.read_text(encoding="utf-8"), content)
            self.assertTrue(mood)


if __name__ == "__main__":
    unittest.main()

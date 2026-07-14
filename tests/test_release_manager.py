"""Release manager changelog / notes tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from commit_machine.release_manager import ReleaseManager
from commit_machine.state import RuntimeState


class ReleaseManagerTests(unittest.TestCase):
    def test_patch_release_writes_artefacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "CHANGELOG.md").write_text(
                "# Changelog\n\nAll notable historical expansion.\n",
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "# ICM\n\n<!-- ICM_VERSION -->**v0.0.0** — x<!-- /ICM_VERSION -->\n",
                encoding="utf-8",
            )
            mgr = ReleaseManager(root)
            state = RuntimeState(total_commits=1000)
            bump = mgr.process(state, previous_count=999, enabled=True)
            assert bump is not None
            self.assertEqual(bump.kind, "patch")
            self.assertIn("v0.0.1", (root / "CHANGELOG.md").read_text(encoding="utf-8"))
            self.assertTrue(
                (root / "releases" / "RELEASE_NOTES_v0.0.1.md").exists()
            )
            readme = (root / "README.md").read_text(encoding="utf-8")
            self.assertIn("v0.0.1", readme)


if __name__ == "__main__":
    unittest.main()

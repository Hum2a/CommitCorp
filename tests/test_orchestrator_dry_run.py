"""Dry-run cycle tests against a temporary Git repository."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from commit_machine.orchestrator import Orchestrator


class OrchestratorDryRunTests(unittest.TestCase):
    def test_dry_run_once_advances_state_without_git_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@example.com",
                    "commit",
                    "--allow-empty",
                    "-m",
                    "bootstrap",
                ],
                cwd=root,
                check=True,
                capture_output=True,
            )
            for name in (
                "generated",
                "logs",
                "state",
                "reports",
                "releases",
                "reports/quarterly",
                "reports/annual",
                "reports/shareholder_letters",
            ):
                (root / name).mkdir(parents=True, exist_ok=True)

            (root / "CHANGELOG.md").write_text("# Changelog\n\n", encoding="utf-8")
            (root / "README.md").write_text("# Test\n", encoding="utf-8")
            (root / "BOARD_MINUTES.md").write_text("# Board\n", encoding="utf-8")

            config = {
                "sleep_seconds": 0,
                "push_every": 100,
                "target_file": "generated/history.txt",
                "repo_root": str(root),
                "state_file": str(root / "state" / "runtime_state.json"),
                "stats_file": str(root / "state" / "statistics.json"),
                "log_dir": str(root / "logs"),
                "enable_dashboard": False,
                "push_enabled": False,
            }
            config_path = root / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")

            before = int(
                subprocess.run(
                    ["git", "rev-list", "--count", "HEAD"],
                    cwd=root,
                    capture_output=True,
                    text=True,
                    check=True,
                ).stdout.strip()
            )

            orch = Orchestrator(config_path, dry_run=True, show_dashboard=False)
            result = orch.run_once()
            self.assertTrue(result.committed)
            self.assertEqual(result.revision, before + 1)
            self.assertTrue((root / "generated" / "history.txt").exists())

            after = int(
                subprocess.run(
                    ["git", "rev-list", "--count", "HEAD"],
                    cwd=root,
                    capture_output=True,
                    text=True,
                    check=True,
                ).stdout.strip()
            )
            self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()

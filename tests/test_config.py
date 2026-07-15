"""Configuration compliance tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from commit_machine.config import ConfigError, HotReloadConfig, load_config


class ConfigTests(unittest.TestCase):
    def test_load_default_repo_config(self) -> None:
        root = Path(__file__).resolve().parents[1]
        cfg = load_config(root / "config.json")
        self.assertGreaterEqual(cfg.sleep_seconds, 0)
        self.assertGreaterEqual(cfg.push_every, 1)
        self.assertEqual(cfg.commits_per_cycle, 5)
        self.assertEqual(len(cfg.batch_target_files()), 5)

    def test_batch_target_files_pads_pool(self) -> None:
        from commit_machine.config import AppConfig

        cfg = AppConfig(
            commits_per_cycle=3,
            target_files=["generated/a.txt", "generated/b.txt"],
        )
        self.assertEqual(
            cfg.batch_target_files(),
            ["generated/a.txt", "generated/b.txt", "generated/a.txt"],
        )

    def test_invalid_push_every(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text(json.dumps({"push_every": 0}), encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_config(path)

    def test_hot_reload_keeps_last_good(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text(
                json.dumps({"sleep_seconds": 10, "push_every": 5}),
                encoding="utf-8",
            )
            hot = HotReloadConfig(path)
            self.assertEqual(hot.config.sleep_seconds, 10)
            path.write_text("{not json", encoding="utf-8")
            # bump mtime
            import time

            time.sleep(0.05)
            path.write_text("{not json", encoding="utf-8")
            cfg = hot.maybe_reload()
            self.assertEqual(cfg.sleep_seconds, 10)


if __name__ == "__main__":
    unittest.main()

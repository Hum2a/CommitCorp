#!/usr/bin/env python3
"""Validate Infinite Commit Machine configuration compliance."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from commit_machine.config import ConfigError, load_config  # noqa: E402


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "config.json"
    try:
        cfg = load_config(path)
    except ConfigError as exc:
        print(f"FAIL: {exc}")
        return 1
    print(f"PASS: configuration compliant ({path})")
    print(f"  sleep_seconds={cfg.sleep_seconds} push_every={cfg.push_every}")
    print(f"  target_file={cfg.target_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

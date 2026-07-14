"""Crash-safe persistence for runtime state recovery."""

from __future__ import annotations

import json
import logging
import os
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RuntimeState:
    """Persisted operational state for post-restart recovery."""

    total_commits: int = 0
    session_commits: int = 0
    commits_since_push: int = 0
    message_index: int = 0
    unlocked_achievements: list[str] = field(default_factory=list)
    unlocked_lore: list[str] = field(default_factory=list)
    last_board_meeting: int = 0
    last_qbr: int = 0
    last_annual: int = 0
    last_shareholder_letter: int = 0
    last_major: int = 0
    last_minor: int = 0
    last_patch: int = 0
    current_version: str = "v0.0.0"
    session_started_at: str = field(default_factory=_utc_now_iso)
    last_commit_at: str | None = None
    longest_runtime_seconds: float = 0.0
    longest_streak: int = 0
    current_streak: int = 0
    total_newlines_produced: int = 0
    total_pushes: int = 0
    last_mood: str = "Enterprise"
    storyline_seed: int = 42
    board_meeting_count: int = 0
    departments_created: list[str] = field(default_factory=list)
    policies_enacted: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RuntimeState:
        from dataclasses import fields as dc_fields

        known = {f.name for f in dc_fields(cls)}
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON via temp file + rename to avoid corruption."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent), prefix=".tmp_", suffix=".json"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def load_state(path: Path) -> RuntimeState:
    """Load runtime state or return a fresh enterprise baseline."""
    if not path.exists():
        logger.info(
            "Temporal Compliance Team: no prior state located; initiating "
            "greenfield historical expansion"
        )
        return RuntimeState()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("state root must be object")
        return RuntimeState.from_dict(data)
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        logger.warning(
            "Office of Repository Excellence: state recovery degraded (%s); "
            "starting fresh session state",
            exc,
        )
        return RuntimeState()


def save_state(path: Path, state: RuntimeState) -> None:
    """Persist runtime state safely."""
    atomic_write_json(path, state.to_dict())

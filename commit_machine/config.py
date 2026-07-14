"""Configuration management with hot-reload and last-good fallback."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

VALID_COMMIT_MESSAGE_MODES = frozenset({"random", "sequential", "enterprise"})


@dataclass
class AppConfig:
    """Enterprise runtime configuration for the Historical Persistence Engine."""

    sleep_seconds: int = 60
    push_every: int = 100
    target_file: str = "generated/history.txt"
    enable_milestones: bool = True
    enable_dashboard: bool = True
    enable_random_messages: bool = True
    commit_message_mode: str = "random"
    enable_achievements: bool = True
    enable_lore: bool = True
    enable_board_minutes: bool = True
    enable_quarterly_reports: bool = True
    enable_annual_reports: bool = True
    enable_releases: bool = True
    repo_root: str = "."
    state_file: str = "state/runtime_state.json"
    stats_file: str = "state/statistics.json"
    log_dir: str = "logs"
    push_enabled: bool = True
    failure_backoff_seconds: int = 30
    max_failure_backoff_seconds: int = 300

    def repo_path(self) -> Path:
        return Path(self.repo_root).resolve()

    def target_path(self) -> Path:
        path = Path(self.target_file)
        if path.is_absolute():
            return path
        return self.repo_path() / path

    def state_path(self) -> Path:
        path = Path(self.state_file)
        return path if path.is_absolute() else self.repo_path() / path

    def stats_path(self) -> Path:
        path = Path(self.stats_file)
        return path if path.is_absolute() else self.repo_path() / path

    def log_path(self) -> Path:
        path = Path(self.log_dir)
        return path if path.is_absolute() else self.repo_path() / path


class ConfigError(Exception):
    """Raised when configuration fails enterprise compliance validation."""


def _validate(data: dict[str, Any]) -> None:
    if "sleep_seconds" in data and (
        not isinstance(data["sleep_seconds"], int) or data["sleep_seconds"] < 0
    ):
        raise ConfigError("sleep_seconds must be a non-negative integer")
    if "push_every" in data and (
        not isinstance(data["push_every"], int) or data["push_every"] < 1
    ):
        raise ConfigError("push_every must be a positive integer")
    mode = data.get("commit_message_mode", "random")
    if mode not in VALID_COMMIT_MESSAGE_MODES:
        raise ConfigError(
            f"commit_message_mode must be one of {sorted(VALID_COMMIT_MESSAGE_MODES)}"
        )
    if "target_file" in data and not isinstance(data["target_file"], str):
        raise ConfigError("target_file must be a string")


def config_from_dict(data: dict[str, Any]) -> AppConfig:
    """Build AppConfig from a dictionary, ignoring unknown keys."""
    _validate(data)
    known = {f.name for f in fields(AppConfig)}
    filtered = {k: v for k, v in data.items() if k in known}
    return AppConfig(**filtered)


def load_config(path: Path | str) -> AppConfig:
    """Load and validate configuration from JSON."""
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Configuration not found: {config_path}")
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in {config_path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigError("Configuration root must be a JSON object")
    return config_from_dict(raw)


def save_config(config: AppConfig, path: Path | str) -> None:
    """Persist configuration to JSON."""
    config_path = Path(path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps(asdict(config), indent=2) + "\n", encoding="utf-8"
    )


class HotReloadConfig:
    """Tracks config.json mtime and reloads when the file changes."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._mtime: float | None = None
        self._config = load_config(self.path)
        self._mtime = self._stat_mtime()

    def _stat_mtime(self) -> float | None:
        try:
            return self.path.stat().st_mtime
        except OSError:
            return None

    @property
    def config(self) -> AppConfig:
        return self._config

    def maybe_reload(self) -> AppConfig:
        """Reload if mtime changed; keep last-good config on failure."""
        current = self._stat_mtime()
        if current is None or current == self._mtime:
            return self._config
        try:
            self._config = load_config(self.path)
            self._mtime = current
            logger.info(
                "Temporal Compliance Team: configuration hot-reloaded from %s",
                self.path,
            )
        except ConfigError as exc:
            logger.warning(
                "Office of Repository Excellence: rejected non-compliant config "
                "(%s); retaining last-good configuration",
                exc,
            )
        return self._config

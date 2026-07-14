"""Professional logging with departmental attribution."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

DEPARTMENTS = (
    "Department of Historical Expansion",
    "Committee for Strategic Newlines",
    "Office of Repository Excellence",
    "Temporal Compliance Team",
    "Enterprise Timestamp Office",
    "Version Control Steering Committee",
    "Historical Accuracy Board",
    "Chronological Operations Division",
)


def _configure_stdio() -> None:
    """Prefer UTF-8 on Windows consoles to avoid charmap failures."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def setup_logging(log_dir: Path, level: int = logging.INFO) -> logging.Logger:
    """Configure console and file logging for ICM."""
    _configure_stdio()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "icm.log"

    root = logging.getLogger()
    root.setLevel(level)

    if root.handlers:
        for handler in list(root.handlers):
            root.removeHandler(handler)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(formatter)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    root.addHandler(console)
    root.addHandler(file_handler)

    logger = logging.getLogger("commit_machine")
    logger.info(
        "Chronological Operations Division: logging subsystem initialised -> %s",
        log_file,
    )
    return logger


def departmental(message: str, department: str | None = None) -> str:
    """Prefix a message with a fictional department attribution."""
    dept = department or DEPARTMENTS[0]
    return f"[{dept}] {message}"

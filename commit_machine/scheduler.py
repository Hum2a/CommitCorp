"""Sleep and backoff scheduling for Continuous Chronological Integration."""

from __future__ import annotations

import logging
import time

logger = logging.getLogger(__name__)


class Scheduler:
    """Controls inter-cycle delay and failure backoff."""

    def __init__(
        self,
        sleep_seconds: int = 60,
        failure_backoff_seconds: int = 30,
        max_failure_backoff_seconds: int = 300,
    ) -> None:
        self.sleep_seconds = sleep_seconds
        self.failure_backoff_seconds = failure_backoff_seconds
        self.max_failure_backoff_seconds = max_failure_backoff_seconds
        self._current_backoff = failure_backoff_seconds

    def update_from_config(
        self,
        sleep_seconds: int,
        failure_backoff_seconds: int,
        max_failure_backoff_seconds: int,
    ) -> None:
        self.sleep_seconds = sleep_seconds
        self.failure_backoff_seconds = failure_backoff_seconds
        self.max_failure_backoff_seconds = max_failure_backoff_seconds

    def wait_success(self) -> None:
        self._current_backoff = self.failure_backoff_seconds
        logger.debug(
            "Chronological Operations Division: sleeping %ss",
            self.sleep_seconds,
        )
        time.sleep(self.sleep_seconds)

    def wait_failure(self) -> None:
        delay = self._current_backoff
        logger.warning(
            "Temporal Compliance Team: applying failure backoff (%ss)",
            delay,
        )
        time.sleep(delay)
        self._current_backoff = min(
            self._current_backoff * 2,
            self.max_failure_backoff_seconds,
        )

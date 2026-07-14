"""Entropy scoring for Historical Throughput Optimisation dashboards."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class EntropyReport:
    """Enterprise entropy assessment for a chronological cycle."""

    score: float  # 0.0–100.0
    level_label: str
    historical_confidence: float  # e.g. 99.999
    git_satisfaction: str


SATISFACTION_BANDS = (
    (90, "Extremely High"),
    (75, "Very High"),
    (60, "High"),
    (40, "Nominal"),
    (20, "Cautiously Optimistic"),
    (0, "Under Review"),
)

LEVEL_LABELS = (
    (90, "Singular"),
    (75, "Elevated"),
    (50, "Balanced"),
    (25, "Stable"),
    (0, "Contained"),
)


def _label_for(score: float, bands: tuple[tuple[int, str], ...]) -> str:
    for threshold, label in bands:
        if score >= threshold:
            return label
    return bands[-1][1]


class EntropyEngine:
    """Produces deterministic-ish entropy metrics from repository signals."""

    def evaluate(
        self,
        *,
        total_commits: int,
        revision: int,
        mood: str,
        session_commits: int,
    ) -> EntropyReport:
        material = f"{total_commits}:{revision}:{mood}:{session_commits}".encode()
        digest = hashlib.sha256(material).hexdigest()
        raw = int(digest[:8], 16) / 0xFFFFFFFF
        # Gentle oscillation so dashboards feel alive without chaos
        wave = (math.sin(total_commits / 17.0) + 1.0) / 2.0
        score = round(min(100.0, max(0.0, (raw * 55.0) + (wave * 45.0))), 1)

        # Historical confidence asymptotically approaches but never quite hits 100
        confidence = round(99.0 + (1.0 - math.exp(-total_commits / 50000.0)) * 0.999, 3)
        confidence = min(99.999, confidence)

        return EntropyReport(
            score=score,
            level_label=_label_for(score, LEVEL_LABELS),
            historical_confidence=confidence,
            git_satisfaction=_label_for(score, SATISFACTION_BANDS),
        )

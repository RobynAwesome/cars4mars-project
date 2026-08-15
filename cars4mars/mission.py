"""Deterministic mission logic for the ARC autonomous balloon sequence.

This module deliberately does not perform perception or path planning. It accepts
observations from a perception layer and enforces the mission ordering and dwell
criteria before allowing the target sequence to advance.

SOFTWARE EVIDENCE ONLY: passing these tests does not prove detection accuracy,
localisation accuracy, rover stopping distance, or autonomous navigation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math


class BalloonColor(str, Enum):
    BLACK = "black"
    WHITE = "white"
    PINK = "pink"
    YELLOW = "yellow"
    BLUE = "blue"


SEQUENCE = (
    BalloonColor.BLACK,
    BalloonColor.WHITE,
    BalloonColor.PINK,
    BalloonColor.YELLOW,
    BalloonColor.BLUE,
)


@dataclass(frozen=True)
class MissionDecision:
    target: BalloonColor | None
    should_hold_stop: bool
    completed: bool
    advanced: bool
    reason: str


class BalloonMissionController:
    """Gate autonomous target progression using rule-derived stop criteria."""

    def __init__(self, *, stop_radius_m: float = 1.5, dwell_ms: int = 5000) -> None:
        if stop_radius_m <= 0:
            raise ValueError("stop_radius_m must be positive")
        if dwell_ms <= 0:
            raise ValueError("dwell_ms must be positive")
        self.stop_radius_m = float(stop_radius_m)
        self.dwell_ms = int(dwell_ms)
        self._index = 0
        self._dwell_started_ms: int | None = None

    @property
    def target(self) -> BalloonColor | None:
        return None if self._index >= len(SEQUENCE) else SEQUENCE[self._index]

    @property
    def completed(self) -> bool:
        return self._index >= len(SEQUENCE)

    def observe(self, *, color: BalloonColor, distance_m: float, now_ms: int) -> MissionDecision:
        if not isinstance(now_ms, int) or now_ms < 0:
            raise ValueError("now_ms must be a non-negative integer")
        if not math.isfinite(distance_m) or distance_m < 0:
            raise ValueError("distance_m must be finite and non-negative")
        if self.completed:
            return MissionDecision(None, True, True, False, "mission already complete")

        target = self.target
        assert target is not None

        if color != target:
            self._dwell_started_ms = None
            return MissionDecision(target, False, False, False, "observation is not current target")

        if distance_m > self.stop_radius_m:
            self._dwell_started_ms = None
            return MissionDecision(target, False, False, False, "target outside stop radius")

        if self._dwell_started_ms is None:
            self._dwell_started_ms = now_ms
            return MissionDecision(target, True, False, False, "stop dwell started")

        elapsed = now_ms - self._dwell_started_ms
        if elapsed < self.dwell_ms:
            return MissionDecision(target, True, False, False, f"holding stop: {elapsed} ms")

        self._index += 1
        self._dwell_started_ms = None
        next_target = self.target
        return MissionDecision(
            next_target,
            True,
            self.completed,
            True,
            "target dwell accepted; sequence advanced",
        )

    def loss_of_target(self) -> MissionDecision:
        """Reset any active dwell when target lock is lost."""
        self._dwell_started_ms = None
        return MissionDecision(
            self.target,
            False,
            self.completed,
            False,
            "target lock lost; dwell reset",
        )

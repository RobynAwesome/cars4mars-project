"""Deterministic rover safety/control reference model for DFR-01.

This module is deliberately hardware-independent. It exists to make the DFR-01
control authority and fail-safe behavior executable and reviewable before Teensy
firmware and physical integration are complete.

It is SOFTWARE EVIDENCE only. Passing these tests does not validate the physical
rover, contactor wiring, motor drivers, radio links, or emergency-stop circuit.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
from typing import Optional


class CommandSource(str, Enum):
    MANUAL = "manual"
    AUTONOMY = "autonomy"


class SafetyState(str, Enum):
    SAFE_DISABLED = "safe_disabled"
    READY = "ready"
    MOTION = "motion"
    ESTOP_LATCHED = "estop_latched"
    FAULT = "fault"


@dataclass(frozen=True)
class ControlCommand:
    linear_mps: float
    angular_rad_s: float
    issued_ms: int
    source: CommandSource = CommandSource.MANUAL


@dataclass(frozen=True)
class ControlDecision:
    accepted: bool
    linear_mps: float
    angular_rad_s: float
    motor_enable: bool
    state: SafetyState
    reason: str


class SafetyController:
    """Reference implementation of the DFR-01 local safety boundary.

    Design intent:
    - The perception/AI layer can request motion but cannot bypass validation.
    - Invalid input immediately forces a safe disabled state.
    - A motion command expires unless refreshed within ``command_timeout_ms``.
    - If neither command nor heartbeat activity is seen within
      ``liveness_timeout_ms``, motor enable is removed.
    - E-stop is latched and requires an explicit reset.

    The distinction between command timeout and liveness timeout prevents a
    heartbeat from keeping stale non-zero motion alive indefinitely.
    """

    def __init__(
        self,
        *,
        max_linear_mps: float = 1.0,
        max_angular_rad_s: float = 2.0,
        command_timeout_ms: int = 500,
        liveness_timeout_ms: int = 500,
    ) -> None:
        if max_linear_mps <= 0 or max_angular_rad_s <= 0:
            raise ValueError("velocity limits must be positive")
        if command_timeout_ms <= 0 or liveness_timeout_ms <= 0:
            raise ValueError("timeouts must be positive")

        self.max_linear_mps = float(max_linear_mps)
        self.max_angular_rad_s = float(max_angular_rad_s)
        self.command_timeout_ms = int(command_timeout_ms)
        self.liveness_timeout_ms = int(liveness_timeout_ms)

        self._state = SafetyState.SAFE_DISABLED
        self._motor_enable = False
        self._linear_mps = 0.0
        self._angular_rad_s = 0.0
        self._last_valid_command_ms: Optional[int] = None
        self._last_liveness_ms: Optional[int] = None
        self._estop_latched = False
        self._fault_reason: Optional[str] = None

    @property
    def state(self) -> SafetyState:
        return self._state

    @property
    def motor_enable(self) -> bool:
        return self._motor_enable

    @property
    def velocity(self) -> tuple[float, float]:
        return (self._linear_mps, self._angular_rad_s)

    def heartbeat(self, now_ms: int) -> ControlDecision:
        self._validate_time(now_ms)
        if self._estop_latched:
            return self._decision(False, "heartbeat ignored: E-stop latched")

        self._last_liveness_ms = now_ms
        if self._state == SafetyState.SAFE_DISABLED and self._fault_reason is None:
            self._state = SafetyState.READY
        return self._decision(True, "heartbeat accepted")

    def apply_command(self, command: ControlCommand, now_ms: int) -> ControlDecision:
        self._validate_time(now_ms)

        if self._estop_latched:
            return self._decision(False, "command rejected: E-stop latched")

        if command.issued_ms > now_ms:
            return self._fault("command rejected: issued in the future")

        age_ms = now_ms - command.issued_ms
        if age_ms > self.command_timeout_ms:
            return self._fault("command rejected: stale")

        if not self._finite(command.linear_mps, command.angular_rad_s):
            return self._fault("command rejected: non-finite velocity")

        if abs(command.linear_mps) > self.max_linear_mps:
            return self._fault("command rejected: linear velocity outside bound")

        if abs(command.angular_rad_s) > self.max_angular_rad_s:
            return self._fault("command rejected: angular velocity outside bound")

        self._fault_reason = None
        self._last_valid_command_ms = now_ms
        self._last_liveness_ms = now_ms
        self._linear_mps = float(command.linear_mps)
        self._angular_rad_s = float(command.angular_rad_s)
        self._motor_enable = True
        self._state = (
            SafetyState.MOTION
            if (self._linear_mps != 0.0 or self._angular_rad_s != 0.0)
            else SafetyState.READY
        )
        return self._decision(True, f"{command.source.value} command accepted")

    def tick(self, now_ms: int) -> ControlDecision:
        """Advance watchdog logic without accepting a new command."""
        self._validate_time(now_ms)

        if self._estop_latched:
            return self._decision(False, "E-stop latched")

        # A heartbeat may prove liveness, but it may never keep stale motion alive.
        if self._last_valid_command_ms is not None:
            if now_ms - self._last_valid_command_ms > self.command_timeout_ms:
                self._zero_velocity()
                if self._motor_enable:
                    self._state = SafetyState.READY

        # If both command and heartbeat activity disappear, remove motor enable.
        if self._last_liveness_ms is None:
            return self._safe_disable("no liveness established")

        if now_ms - self._last_liveness_ms > self.liveness_timeout_ms:
            return self._safe_disable("liveness watchdog expired")

        return self._decision(True, "watchdog healthy")

    def emergency_stop(self) -> ControlDecision:
        self._estop_latched = True
        self._zero_velocity()
        self._motor_enable = False
        self._state = SafetyState.ESTOP_LATCHED
        self._fault_reason = "E-stop latched"
        return self._decision(False, self._fault_reason)

    def reset_estop(self) -> ControlDecision:
        """Explicitly clear the software latch.

        Physical reset policy must be implemented and tested on the real power
        stage. Clearing this software latch does not prove the physical E-stop.
        """
        self._estop_latched = False
        self._fault_reason = None
        self._zero_velocity()
        self._motor_enable = False
        self._last_valid_command_ms = None
        self._last_liveness_ms = None
        self._state = SafetyState.SAFE_DISABLED
        return self._decision(True, "E-stop software latch reset; re-arm required")

    def _fault(self, reason: str) -> ControlDecision:
        self._fault_reason = reason
        self._zero_velocity()
        self._motor_enable = False
        self._state = SafetyState.FAULT
        return self._decision(False, reason)

    def _safe_disable(self, reason: str) -> ControlDecision:
        self._zero_velocity()
        self._motor_enable = False
        self._state = SafetyState.SAFE_DISABLED
        return self._decision(False, reason)

    def _zero_velocity(self) -> None:
        self._linear_mps = 0.0
        self._angular_rad_s = 0.0

    def _decision(self, accepted: bool, reason: str) -> ControlDecision:
        return ControlDecision(
            accepted=accepted,
            linear_mps=self._linear_mps,
            angular_rad_s=self._angular_rad_s,
            motor_enable=self._motor_enable,
            state=self._state,
            reason=reason,
        )

    @staticmethod
    def _validate_time(now_ms: int) -> None:
        if not isinstance(now_ms, int) or now_ms < 0:
            raise ValueError("now_ms must be a non-negative integer")

    @staticmethod
    def _finite(*values: float) -> bool:
        return all(math.isfinite(value) for value in values)

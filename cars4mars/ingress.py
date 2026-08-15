"""Protocol ingress boundary for the deterministic embedded controller model.

This module joins the wire protocol to the DFR-01 safety controller. Sequence
freshness is enforced for commands, heartbeats, and E-stop reset. A valid E-stop
is deliberately accepted regardless of sequence age because a replayed stop is
safe; a replayed reset is not.
"""

from __future__ import annotations

from dataclasses import dataclass

from .control import CommandSource, ControlCommand, ControlDecision, SafetyController
from .protocol import DriveSource, MessageType, ProtocolError, decode_drive_payload, decode_frame


@dataclass(frozen=True)
class IngressResult:
    accepted: bool
    reason: str
    sequence: int | None
    control: ControlDecision | None


def is_newer_sequence(candidate: int, previous: int) -> bool:
    """RFC1982-style uint32 serial comparison for a bounded receive window."""
    delta = (candidate - previous) & 0xFFFFFFFF
    return 0 < delta < 0x80000000


class EmbeddedIngress:
    def __init__(self, controller: SafetyController | None = None) -> None:
        self.controller = controller or SafetyController()
        self._last_sequence: int | None = None

    @property
    def last_sequence(self) -> int | None:
        return self._last_sequence

    def handle(self, raw: bytes, *, now_ms: int) -> IngressResult:
        try:
            frame = decode_frame(raw)
        except ProtocolError as exc:
            return IngressResult(False, f"protocol rejected: {exc}", None, None)

        # Safety asymmetry: any valid stop packet may stop the rover, including a
        # duplicate/replayed one. Reset and motion packets must be fresh.
        if frame.message_type == MessageType.ESTOP:
            decision = self.controller.emergency_stop()
            return IngressResult(True, "E-stop accepted", frame.sequence, decision)

        if self._last_sequence is not None and not is_newer_sequence(frame.sequence, self._last_sequence):
            return IngressResult(False, "sequence replay/out-of-order rejected", frame.sequence, None)

        if frame.message_type == MessageType.HEARTBEAT:
            decision = self.controller.heartbeat(now_ms)
        elif frame.message_type == MessageType.DRIVE:
            try:
                payload = decode_drive_payload(frame.payload)
            except ProtocolError as exc:
                return IngressResult(False, f"drive payload rejected: {exc}", frame.sequence, None)
            source = CommandSource.MANUAL if payload.source == DriveSource.MANUAL else CommandSource.AUTONOMY
            decision = self.controller.apply_command(
                ControlCommand(
                    linear_mps=payload.linear_mps,
                    angular_rad_s=payload.angular_rad_s,
                    issued_ms=payload.issued_ms,
                    source=source,
                ),
                now_ms=now_ms,
            )
        elif frame.message_type == MessageType.RESET_ESTOP:
            decision = self.controller.reset_estop()
        else:
            return IngressResult(False, "message type not accepted on command ingress", frame.sequence, None)

        # Freshness advances only after a structurally valid message reaches the
        # control boundary. A safety-rejected drive still consumes its sequence so
        # the same hazardous request cannot be retried as if unseen.
        self._last_sequence = frame.sequence
        return IngressResult(decision.accepted, decision.reason, frame.sequence, decision)

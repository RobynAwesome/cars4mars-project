"""Jetson-side command packet construction for DFR-01.

The class in this module does not make autonomous decisions. It converts reviewed
manual or autonomy requests into versioned protocol frames that the deterministic
embedded controller can accept or reject.
"""

from __future__ import annotations

from dataclasses import dataclass
import socket
from typing import Protocol

from .protocol import (
    DrivePayload,
    DriveSource,
    MessageType,
    encode_drive_payload,
    encode_frame,
)


class DatagramTransport(Protocol):
    def send(self, payload: bytes) -> None: ...


@dataclass
class UdpTransport:
    host: str
    port: int

    def send(self, payload: bytes) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(payload, (self.host, self.port))


class RoverCommandClient:
    """Sequence-stamped command producer for the Jetson side."""

    def __init__(self, transport: DatagramTransport) -> None:
        self.transport = transport
        self._sequence = 0

    @property
    def next_sequence(self) -> int:
        return self._sequence

    def _send(self, message_type: MessageType, payload: bytes = b"") -> bytes:
        frame = encode_frame(message_type, self._sequence, payload)
        self.transport.send(frame)
        self._sequence = (self._sequence + 1) & 0xFFFFFFFF
        return frame

    def heartbeat(self) -> bytes:
        return self._send(MessageType.HEARTBEAT)

    def drive(
        self,
        *,
        linear_mps: float,
        angular_rad_s: float,
        issued_ms: int,
        source: DriveSource = DriveSource.MANUAL,
    ) -> bytes:
        linear_mm_s = round(linear_mps * 1000.0)
        angular_mrad_s = round(angular_rad_s * 1000.0)
        payload = encode_drive_payload(
            DrivePayload(
                linear_mm_s=linear_mm_s,
                angular_mrad_s=angular_mrad_s,
                issued_ms=issued_ms,
                source=source,
            )
        )
        return self._send(MessageType.DRIVE, payload)

    def emergency_stop(self) -> bytes:
        return self._send(MessageType.ESTOP)

    def reset_estop(self) -> bytes:
        return self._send(MessageType.RESET_ESTOP)

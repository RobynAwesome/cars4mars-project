"""DFR-01 rover wire protocol reference implementation.

This module defines the bytes exchanged between the Jetson-side command client and
an embedded control implementation. It is intentionally small, versioned, and
CRC-protected so the protocol can be reproduced on the Teensy without depending
on Python or an AI runtime.

SOFTWARE EVIDENCE ONLY: protocol tests do not prove radio reliability, serial
integrity, Teensy timing, motor-driver behavior, or physical fail-safe operation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
import struct


MAGIC = b"C4M1"
VERSION = 1
_HEADER = struct.Struct("!4sBBHI")  # magic, version, type, payload length, sequence
_CRC = struct.Struct("!H")
_DRIVE = struct.Struct("!hhIB")  # mm/s, mrad/s, issued_ms, source


class ProtocolError(ValueError):
    """Raised when a frame cannot be accepted as a valid C4M frame."""


class MessageType(IntEnum):
    HEARTBEAT = 1
    DRIVE = 2
    ESTOP = 3
    RESET_ESTOP = 4
    TELEMETRY = 5


class DriveSource(IntEnum):
    MANUAL = 1
    AUTONOMY = 2


@dataclass(frozen=True)
class Frame:
    message_type: MessageType
    sequence: int
    payload: bytes


@dataclass(frozen=True)
class DrivePayload:
    linear_mm_s: int
    angular_mrad_s: int
    issued_ms: int
    source: DriveSource

    @property
    def linear_mps(self) -> float:
        return self.linear_mm_s / 1000.0

    @property
    def angular_rad_s(self) -> float:
        return self.angular_mrad_s / 1000.0


def crc16_ccitt(data: bytes, *, initial: int = 0xFFFF) -> int:
    """CRC-16/CCITT-FALSE polynomial 0x1021, init 0xFFFF."""
    crc = initial & 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def encode_frame(message_type: MessageType, sequence: int, payload: bytes = b"") -> bytes:
    if not 0 <= sequence <= 0xFFFFFFFF:
        raise ValueError("sequence must fit uint32")
    if len(payload) > 0xFFFF:
        raise ValueError("payload too large")
    header = _HEADER.pack(MAGIC, VERSION, int(message_type), len(payload), sequence)
    body = header + payload
    return body + _CRC.pack(crc16_ccitt(body))


def decode_frame(raw: bytes) -> Frame:
    minimum = _HEADER.size + _CRC.size
    if len(raw) < minimum:
        raise ProtocolError("frame truncated")

    magic, version, raw_type, payload_len, sequence = _HEADER.unpack(raw[: _HEADER.size])
    expected_len = _HEADER.size + payload_len + _CRC.size
    if len(raw) != expected_len:
        raise ProtocolError("frame length mismatch")
    if magic != MAGIC:
        raise ProtocolError("bad magic")
    if version != VERSION:
        raise ProtocolError("unsupported version")

    try:
        message_type = MessageType(raw_type)
    except ValueError as exc:
        raise ProtocolError("unknown message type") from exc

    expected_crc = _CRC.unpack(raw[-_CRC.size :])[0]
    actual_crc = crc16_ccitt(raw[:-_CRC.size])
    if expected_crc != actual_crc:
        raise ProtocolError("CRC mismatch")

    payload = raw[_HEADER.size : -_CRC.size]
    return Frame(message_type=message_type, sequence=sequence, payload=payload)


def encode_drive_payload(payload: DrivePayload) -> bytes:
    if not -32768 <= payload.linear_mm_s <= 32767:
        raise ValueError("linear_mm_s must fit int16")
    if not -32768 <= payload.angular_mrad_s <= 32767:
        raise ValueError("angular_mrad_s must fit int16")
    if not 0 <= payload.issued_ms <= 0xFFFFFFFF:
        raise ValueError("issued_ms must fit uint32")
    return _DRIVE.pack(
        payload.linear_mm_s,
        payload.angular_mrad_s,
        payload.issued_ms,
        int(payload.source),
    )


def decode_drive_payload(raw: bytes) -> DrivePayload:
    if len(raw) != _DRIVE.size:
        raise ProtocolError("invalid drive payload length")
    linear_mm_s, angular_mrad_s, issued_ms, raw_source = _DRIVE.unpack(raw)
    try:
        source = DriveSource(raw_source)
    except ValueError as exc:
        raise ProtocolError("unknown drive source") from exc
    return DrivePayload(
        linear_mm_s=linear_mm_s,
        angular_mrad_s=angular_mrad_s,
        issued_ms=issued_ms,
        source=source,
    )

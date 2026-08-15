import unittest

from cars4mars.control import SafetyState
from cars4mars.ingress import EmbeddedIngress, is_newer_sequence
from cars4mars.jetson_client import RoverCommandClient
from cars4mars.protocol import MessageType, encode_frame


class MemoryTransport:
    def __init__(self):
        self.frames = []

    def send(self, payload: bytes) -> None:
        self.frames.append(payload)


class IngressTests(unittest.TestCase):
    def test_sequence_comparison_handles_wrap(self):
        self.assertTrue(is_newer_sequence(0, 0xFFFFFFFF))
        self.assertFalse(is_newer_sequence(10, 10))
        self.assertFalse(is_newer_sequence(9, 10))

    def test_replayed_drive_is_rejected(self):
        transport = MemoryTransport()
        client = RoverCommandClient(transport)
        raw = client.drive(linear_mps=0.2, angular_rad_s=0.0, issued_ms=100)
        ingress = EmbeddedIngress()

        first = ingress.handle(raw, now_ms=100)
        replay = ingress.handle(raw, now_ms=110)

        self.assertTrue(first.accepted)
        self.assertFalse(replay.accepted)
        self.assertIn("replay", replay.reason)

    def test_old_estop_still_stops(self):
        ingress = EmbeddedIngress()
        ingress.handle(encode_frame(MessageType.HEARTBEAT, 20), now_ms=0)
        old_estop = encode_frame(MessageType.ESTOP, 1)
        result = ingress.handle(old_estop, now_ms=1)
        self.assertTrue(result.accepted)
        self.assertEqual(result.control.state, SafetyState.ESTOP_LATCHED)
        self.assertFalse(result.control.motor_enable)

    def test_replayed_reset_cannot_clear_estop(self):
        ingress = EmbeddedIngress()
        ingress.handle(encode_frame(MessageType.HEARTBEAT, 10), now_ms=0)
        ingress.handle(encode_frame(MessageType.ESTOP, 1), now_ms=1)
        stale_reset = ingress.handle(encode_frame(MessageType.RESET_ESTOP, 9), now_ms=2)
        self.assertFalse(stale_reset.accepted)
        self.assertEqual(ingress.controller.state, SafetyState.ESTOP_LATCHED)

    def test_corrupt_frame_does_not_refresh_liveness(self):
        ingress = EmbeddedIngress()
        ingress.handle(encode_frame(MessageType.HEARTBEAT, 1), now_ms=0)
        corrupt = bytearray(encode_frame(MessageType.HEARTBEAT, 2))
        corrupt[-1] ^= 0xFF
        rejected = ingress.handle(bytes(corrupt), now_ms=400)
        self.assertFalse(rejected.accepted)
        decision = ingress.controller.tick(501)
        self.assertFalse(decision.motor_enable)
        self.assertEqual(decision.state, SafetyState.SAFE_DISABLED)


if __name__ == "__main__":
    unittest.main()

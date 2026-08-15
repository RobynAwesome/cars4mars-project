import unittest

from cars4mars.control import CommandSource, ControlCommand, SafetyController, SafetyState
from cars4mars.drive import mix_skid_steer
from cars4mars.jetson_client import RoverCommandClient
from cars4mars.protocol import DriveSource, MessageType, decode_drive_payload, decode_frame


class MemoryTransport:
    def __init__(self):
        self.frames = []

    def send(self, payload: bytes) -> None:
        self.frames.append(payload)


class SoftwareInLoopTests(unittest.TestCase):
    def test_manual_drive_frame_reaches_safe_drive_mix(self):
        transport = MemoryTransport()
        client = RoverCommandClient(transport)
        raw = client.drive(linear_mps=0.45, angular_rad_s=0.25, issued_ms=1000)

        frame = decode_frame(raw)
        self.assertEqual(frame.message_type, MessageType.DRIVE)
        payload = decode_drive_payload(frame.payload)

        controller = SafetyController()
        decision = controller.apply_command(
            ControlCommand(
                linear_mps=payload.linear_mps,
                angular_rad_s=payload.angular_rad_s,
                issued_ms=payload.issued_ms,
                source=CommandSource.MANUAL,
            ),
            now_ms=1000,
        )
        self.assertTrue(decision.accepted)
        self.assertTrue(decision.motor_enable)
        self.assertEqual(decision.state, SafetyState.MOTION)

        mix = mix_skid_steer(decision.linear_mps, decision.angular_rad_s)
        self.assertLess(mix.left_mps, mix.right_mps)
        self.assertTrue(all(-1.0 <= duty <= 1.0 for duty in mix.duty.as_tuple()))

    def test_autonomy_uses_same_safety_boundary(self):
        transport = MemoryTransport()
        client = RoverCommandClient(transport)
        raw = client.drive(
            linear_mps=0.3,
            angular_rad_s=-0.2,
            issued_ms=2000,
            source=DriveSource.AUTONOMY,
        )
        payload = decode_drive_payload(decode_frame(raw).payload)
        controller = SafetyController(max_linear_mps=0.25)
        decision = controller.apply_command(
            ControlCommand(
                linear_mps=payload.linear_mps,
                angular_rad_s=payload.angular_rad_s,
                issued_ms=payload.issued_ms,
                source=CommandSource.AUTONOMY,
            ),
            now_ms=2000,
        )
        self.assertFalse(decision.accepted)
        self.assertFalse(decision.motor_enable)
        self.assertEqual(decision.state, SafetyState.FAULT)

    def test_estop_dominates_subsequent_commands(self):
        controller = SafetyController()
        controller.heartbeat(0)
        controller.emergency_stop()
        decision = controller.apply_command(
            ControlCommand(0.2, 0.0, 10, CommandSource.MANUAL),
            now_ms=10,
        )
        self.assertFalse(decision.accepted)
        self.assertFalse(decision.motor_enable)
        self.assertEqual(decision.state, SafetyState.ESTOP_LATCHED)

    def test_client_sequence_increments_for_auditable_ordering(self):
        transport = MemoryTransport()
        client = RoverCommandClient(transport)
        client.heartbeat()
        client.heartbeat()
        first = decode_frame(transport.frames[0])
        second = decode_frame(transport.frames[1])
        self.assertEqual(first.sequence, 0)
        self.assertEqual(second.sequence, 1)


if __name__ == "__main__":
    unittest.main()

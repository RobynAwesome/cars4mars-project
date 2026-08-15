import math
import unittest

from cars4mars.control import (
    CommandSource,
    ControlCommand,
    SafetyController,
    SafetyState,
)


class SafetyControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.controller = SafetyController(
            max_linear_mps=1.0,
            max_angular_rad_s=2.0,
            command_timeout_ms=500,
            liveness_timeout_ms=500,
        )

    def test_initial_state_is_safe_disabled(self) -> None:
        self.assertEqual(self.controller.state, SafetyState.SAFE_DISABLED)
        self.assertFalse(self.controller.motor_enable)
        self.assertEqual(self.controller.velocity, (0.0, 0.0))

    def test_valid_manual_command_can_enable_motion(self) -> None:
        decision = self.controller.apply_command(
            ControlCommand(0.4, 0.2, issued_ms=100, source=CommandSource.MANUAL),
            now_ms=100,
        )
        self.assertTrue(decision.accepted)
        self.assertTrue(decision.motor_enable)
        self.assertEqual(decision.state, SafetyState.MOTION)
        self.assertEqual((decision.linear_mps, decision.angular_rad_s), (0.4, 0.2))

    def test_autonomy_has_no_safety_bypass(self) -> None:
        decision = self.controller.apply_command(
            ControlCommand(1.2, 0.0, issued_ms=100, source=CommandSource.AUTONOMY),
            now_ms=100,
        )
        self.assertFalse(decision.accepted)
        self.assertFalse(decision.motor_enable)
        self.assertEqual(decision.state, SafetyState.FAULT)
        self.assertEqual(self.controller.velocity, (0.0, 0.0))

    def test_stale_command_is_rejected_and_disables_motor(self) -> None:
        decision = self.controller.apply_command(
            ControlCommand(0.2, 0.0, issued_ms=0),
            now_ms=501,
        )
        self.assertFalse(decision.accepted)
        self.assertFalse(decision.motor_enable)
        self.assertEqual(decision.state, SafetyState.FAULT)

    def test_non_finite_command_fails_safe(self) -> None:
        decision = self.controller.apply_command(
            ControlCommand(math.nan, 0.0, issued_ms=100),
            now_ms=100,
        )
        self.assertFalse(decision.accepted)
        self.assertEqual(self.controller.velocity, (0.0, 0.0))
        self.assertFalse(self.controller.motor_enable)

    def test_angular_bound_violation_fails_safe(self) -> None:
        decision = self.controller.apply_command(
            ControlCommand(0.0, -2.1, issued_ms=100),
            now_ms=100,
        )
        self.assertFalse(decision.accepted)
        self.assertFalse(decision.motor_enable)
        self.assertEqual(self.controller.velocity, (0.0, 0.0))

    def test_command_lease_expires_even_if_heartbeat_remains_fresh(self) -> None:
        self.controller.apply_command(
            ControlCommand(0.5, 0.0, issued_ms=0),
            now_ms=0,
        )
        self.controller.heartbeat(now_ms=450)
        decision = self.controller.tick(now_ms=501)

        self.assertTrue(decision.accepted)
        self.assertTrue(decision.motor_enable)
        self.assertEqual((decision.linear_mps, decision.angular_rad_s), (0.0, 0.0))
        self.assertEqual(decision.state, SafetyState.READY)

    def test_liveness_watchdog_opens_motor_enable(self) -> None:
        self.controller.apply_command(
            ControlCommand(0.3, 0.0, issued_ms=0),
            now_ms=0,
        )
        decision = self.controller.tick(now_ms=501)

        self.assertFalse(decision.accepted)
        self.assertFalse(decision.motor_enable)
        self.assertEqual(self.controller.velocity, (0.0, 0.0))
        self.assertEqual(decision.state, SafetyState.SAFE_DISABLED)

    def test_heartbeat_never_creates_motion(self) -> None:
        decision = self.controller.heartbeat(now_ms=100)
        self.assertTrue(decision.accepted)
        self.assertEqual(self.controller.velocity, (0.0, 0.0))
        self.assertFalse(self.controller.motor_enable)
        self.assertEqual(decision.state, SafetyState.READY)

    def test_estop_is_latched_and_requires_explicit_reset(self) -> None:
        self.controller.apply_command(
            ControlCommand(0.3, 0.0, issued_ms=100),
            now_ms=100,
        )
        stop = self.controller.emergency_stop()
        self.assertFalse(stop.motor_enable)
        self.assertEqual(stop.state, SafetyState.ESTOP_LATCHED)
        self.assertEqual(self.controller.velocity, (0.0, 0.0))

        rejected = self.controller.apply_command(
            ControlCommand(0.1, 0.0, issued_ms=101),
            now_ms=101,
        )
        self.assertFalse(rejected.accepted)
        self.assertEqual(rejected.state, SafetyState.ESTOP_LATCHED)

        reset = self.controller.reset_estop()
        self.assertTrue(reset.accepted)
        self.assertFalse(reset.motor_enable)
        self.assertEqual(reset.state, SafetyState.SAFE_DISABLED)

    def test_future_timestamp_is_invalid(self) -> None:
        decision = self.controller.apply_command(
            ControlCommand(0.1, 0.0, issued_ms=101),
            now_ms=100,
        )
        self.assertFalse(decision.accepted)
        self.assertFalse(decision.motor_enable)
        self.assertEqual(decision.state, SafetyState.FAULT)


if __name__ == "__main__":
    unittest.main()

import unittest

from cars4mars.drive import DriveGeometry, mix_skid_steer


class DriveMixTests(unittest.TestCase):
    def test_straight_line_gives_equal_sides(self):
        mix = mix_skid_steer(0.4, 0.0)
        self.assertAlmostEqual(mix.left_mps, mix.right_mps)
        self.assertAlmostEqual(mix.duty.left_front, mix.duty.right_front)
        self.assertEqual(mix.duty.left_front, mix.duty.left_middle)
        self.assertEqual(mix.duty.left_middle, mix.duty.left_rear)
        self.assertEqual(mix.duty.right_front, mix.duty.right_middle)
        self.assertEqual(mix.duty.right_middle, mix.duty.right_rear)

    def test_positive_yaw_turns_left(self):
        mix = mix_skid_steer(0.4, 0.5)
        self.assertLess(mix.left_mps, mix.right_mps)

    def test_zero_linear_velocity_can_pivot(self):
        mix = mix_skid_steer(0.0, 1.0)
        self.assertLess(mix.left_mps, 0.0)
        self.assertGreater(mix.right_mps, 0.0)
        self.assertAlmostEqual(abs(mix.left_mps), abs(mix.right_mps))

    def test_saturation_preserves_side_ratio(self):
        geometry = DriveGeometry(track_width_m=0.56, wheel_radius_m=0.125, nominal_motor_rpm=60.0)
        raw = mix_skid_steer(0.5, 0.5, geometry)
        high = mix_skid_steer(2.0, 2.0, geometry)
        self.assertTrue(high.saturated)
        self.assertLessEqual(max(abs(high.left_rpm), abs(high.right_rpm)), 60.0)
        expected_ratio = (2.0 - 2.0 * 0.28) / (2.0 + 2.0 * 0.28)
        actual_ratio = high.left_mps / high.right_mps
        self.assertAlmostEqual(actual_ratio, expected_ratio)
        self.assertFalse(raw.saturated)

    def test_non_finite_input_is_rejected(self):
        with self.assertRaises(ValueError):
            mix_skid_steer(float("nan"), 0.0)


if __name__ == "__main__":
    unittest.main()

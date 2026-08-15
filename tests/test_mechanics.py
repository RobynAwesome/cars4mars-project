import math
import unittest

from cars4mars.mechanics import (
    MassPoint,
    center_of_mass_m,
    current_from_power_a,
    downslope_force_n,
    ideal_equal_share_torque_nm,
    ideal_total_wheel_torque_nm,
    minimum_friction_coefficient_for_static_slope,
    no_load_surface_speed_mps,
)


class MechanicsTests(unittest.TestCase):
    def test_dfr01_45_degree_downslope_force(self):
        # 30 * 9.81 * sin(45 deg) = 208.101525703... N.
        self.assertAlmostEqual(downslope_force_n(30.0, 45.0), 208.101526, places=6)

    def test_dfr01_45_degree_ideal_total_wheel_torque(self):
        torque = ideal_total_wheel_torque_nm(30.0, 45.0, 0.125)
        # 208.101525703... N * 0.125 m = 26.012690713... N.m.
        self.assertAlmostEqual(torque, 26.012691, places=6)

    def test_equal_share_is_arithmetic_not_load_transfer_model(self):
        torque = ideal_total_wheel_torque_nm(30.0, 45.0, 0.125)
        # Equal share is only arithmetic. Real rocker-bogie wheel loads are not assumed equal.
        self.assertAlmostEqual(
            ideal_equal_share_torque_nm(torque, 6), 4.335448, places=6
        )

    def test_45_degree_static_slope_needs_ideal_mu_one(self):
        self.assertAlmostEqual(minimum_friction_coefficient_for_static_slope(45.0), 1.0, places=9)

    def test_60_rpm_250_mm_wheel_geometric_speed(self):
        self.assertAlmostEqual(no_load_surface_speed_mps(60.0, 0.125), math.pi / 4, places=9)

    def test_power_current_arithmetic_is_not_motor_model(self):
        self.assertAlmostEqual(current_from_power_a(100.0, 24.0), 100.0 / 24.0, places=9)

    def test_center_of_mass_requires_real_mass_points(self):
        with self.assertRaises(ValueError):
            center_of_mass_m([])

    def test_center_of_mass_math(self):
        com = center_of_mass_m(
            [
                MassPoint(2.0, 0.0, 0.0, 0.1),
                MassPoint(2.0, 0.2, 0.0, 0.1),
            ]
        )
        self.assertEqual(com, (0.1, 0.0, 0.1))


if __name__ == "__main__":
    unittest.main()

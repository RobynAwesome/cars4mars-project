import unittest

from cars4mars.simulation import (
    GradeCase,
    HeartbeatLossCase,
    grade_forces,
    grade_sensitivity,
    simulate_grade,
    simulate_heartbeat_loss,
)


class SimulationTests(unittest.TestCase):
    def test_ideal_45_degree_lower_bound_is_grade_hold_only(self):
        case = GradeCase(
            mass_kg=30.0,
            slope_deg=45.0,
            wheel_radius_m=0.125,
            total_drive_torque_nm=26.012690712900116,
            drivetrain_efficiency=1.0,
            rolling_resistance_coeff=0.0,
            traction_mu=1.0,
        )
        result = grade_forces(case)
        self.assertAlmostEqual(result.net_uphill_force_n, 0.0, places=9)
        self.assertEqual(result.status, "ideal_grade_hold")
        self.assertFalse(result.traction_limited)

    def test_same_torque_with_loss_is_insufficient(self):
        case = GradeCase(
            mass_kg=30.0,
            slope_deg=45.0,
            wheel_radius_m=0.125,
            total_drive_torque_nm=26.012690712900116,
            drivetrain_efficiency=0.8,
            rolling_resistance_coeff=0.03,
            traction_mu=1.0,
        )
        result = grade_forces(case)
        self.assertLess(result.net_uphill_force_n, 0.0)
        self.assertEqual(result.status, "insufficient_uphill_force")

    def test_more_torque_can_still_be_traction_limited(self):
        case = GradeCase(
            mass_kg=30.0,
            slope_deg=45.0,
            wheel_radius_m=0.125,
            total_drive_torque_nm=45.0,
            drivetrain_efficiency=0.9,
            rolling_resistance_coeff=0.02,
            traction_mu=0.65,
        )
        result = grade_forces(case)
        self.assertTrue(result.traction_limited)
        self.assertLess(result.net_uphill_force_n, 0.0)

    def test_grade_trace_is_threejs_replay_ready(self):
        trace = simulate_grade(
            "ideal-lower-bound",
            GradeCase(
                mass_kg=30.0,
                slope_deg=45.0,
                wheel_radius_m=0.125,
                total_drive_torque_nm=26.012690712900116,
                drivetrain_efficiency=1.0,
                rolling_resistance_coeff=0.0,
                traction_mu=1.0,
            ),
            duration_s=1.0,
            dt_ms=100,
        ).to_dict()
        self.assertEqual(trace["schema"], "cars4mars.sim.trace.v1")
        self.assertEqual(len(trace["frames"]), 11)
        self.assertIn("truth_boundary", trace)
        for key in ("x_m", "y_m", "z_m", "pitch_rad", "linear_mps", "state"):
            self.assertIn(key, trace["frames"][0])

    def test_heartbeat_stop_envelope_is_analytic(self):
        trace = simulate_heartbeat_loss(
            "heartbeat-loss",
            HeartbeatLossCase(
                initial_speed_mps=0.5,
                command_timeout_ms=500,
                assumed_braking_deceleration_mps2=0.8,
            ),
            dt_ms=50,
        )
        self.assertAlmostEqual(trace.summary["timeout_distance_m"], 0.25, places=9)
        self.assertAlmostEqual(trace.summary["assumed_braking_distance_m"], 0.15625, places=9)
        self.assertAlmostEqual(trace.summary["assumed_total_stop_distance_m"], 0.40625, places=9)
        self.assertAlmostEqual(trace.summary["assumed_total_stop_time_s"], 1.125, places=9)
        self.assertEqual(trace.frames[-1].state, "stopped")
        self.assertFalse(trace.frames[-1].motor_enable)

    def test_sensitivity_sweep_is_deterministic(self):
        rows = grade_sensitivity(
            mass_kg=30.0,
            slope_deg=45.0,
            wheel_radius_m=0.125,
            torques_nm=[26.012690712900116, 40.0],
            efficiencies=[0.8, 1.0],
            traction_coefficients=[0.65, 1.0],
            rolling_resistance_coeff=0.02,
        )
        self.assertEqual(len(rows), 8)
        self.assertTrue(any(row["traction_limited"] for row in rows))
        self.assertTrue(any(row["status"] == "insufficient_uphill_force" for row in rows))


if __name__ == "__main__":
    unittest.main()

import unittest

from cars4mars.mission import BalloonColor, BalloonMissionController, SEQUENCE


class BalloonMissionTests(unittest.TestCase):
    def test_wrong_color_does_not_advance(self):
        mission = BalloonMissionController()
        decision = mission.observe(color=BalloonColor.WHITE, distance_m=1.0, now_ms=0)
        self.assertFalse(decision.advanced)
        self.assertEqual(mission.target, BalloonColor.BLACK)

    def test_target_outside_radius_does_not_start_dwell(self):
        mission = BalloonMissionController()
        decision = mission.observe(color=BalloonColor.BLACK, distance_m=1.51, now_ms=0)
        self.assertFalse(decision.should_hold_stop)
        self.assertFalse(decision.advanced)

    def test_five_second_dwell_advances_exactly_one_target(self):
        mission = BalloonMissionController()
        first = mission.observe(color=BalloonColor.BLACK, distance_m=1.0, now_ms=100)
        self.assertTrue(first.should_hold_stop)
        before = mission.observe(color=BalloonColor.BLACK, distance_m=1.0, now_ms=5099)
        self.assertFalse(before.advanced)
        accepted = mission.observe(color=BalloonColor.BLACK, distance_m=1.0, now_ms=5100)
        self.assertTrue(accepted.advanced)
        self.assertEqual(mission.target, BalloonColor.WHITE)

    def test_loss_of_target_resets_dwell(self):
        mission = BalloonMissionController()
        mission.observe(color=BalloonColor.BLACK, distance_m=1.0, now_ms=0)
        mission.loss_of_target()
        decision = mission.observe(color=BalloonColor.BLACK, distance_m=1.0, now_ms=5000)
        self.assertFalse(decision.advanced)
        self.assertEqual(decision.reason, "stop dwell started")

    def test_full_sequence_completes_only_in_rule_order(self):
        mission = BalloonMissionController()
        now = 0
        for color in SEQUENCE:
            mission.observe(color=color, distance_m=1.0, now_ms=now)
            now += 5000
            decision = mission.observe(color=color, distance_m=1.0, now_ms=now)
            self.assertTrue(decision.advanced)
            now += 1
        self.assertTrue(mission.completed)
        self.assertIsNone(mission.target)


if __name__ == "__main__":
    unittest.main()

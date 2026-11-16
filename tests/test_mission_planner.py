import unittest
from core.mission_planner import MissionPlanner, Waypoint

class TestMissionPlanner(unittest.TestCase):
    def setUp(self):
        self.planner = MissionPlanner()

    def test_add_and_advance(self):
        self.planner.add_waypoint(Waypoint(lat=-7.92, lon=110.54, alt_rel=10.0))
        self.planner.add_waypoint(Waypoint(lat=-7.91, lon=110.55, alt_rel=15.0))
        self.assertEqual(len(self.planner.waypoints), 2)
        self.assertEqual(self.planner.current_index, 0)
        has_more = self.planner.advance()
        self.assertTrue(has_more)
        self.assertEqual(self.planner.current_index, 1)
        has_more = self.planner.advance()
        self.assertFalse(has_more)

    def test_generate_lawnmower_grid(self):
        wps = self.planner.generate_lawnmower_grid(
            center_lat=-7.9255, center_lon=110.5485,
            width_m=50, height_m=50, line_spacing_m=25, altitude_m=15
        )
        self.assertTrue(len(wps) >= 4)

if __name__ == '__main__':
    unittest.main()

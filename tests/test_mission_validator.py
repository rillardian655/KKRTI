import unittest
from tools.validate_mission import validate_mission_data

class TestMissionValidator(unittest.TestCase):
    def test_valid_mission(self):
        data = {
            "waypoints": [
                {"lat": -7.92, "lon": 110.54, "alt": 20.0, "speed": 8.0}
            ]
        }
        issues = validate_mission_data(data)
        self.assertEqual(len(issues), 0)

    def test_invalid_altitude(self):
        data = {
            "waypoints": [
                {"lat": -7.92, "lon": 110.54, "alt": -5.0, "speed": 8.0}
            ]
        }
        issues = validate_mission_data(data)
        self.assertTrue(len(issues) > 0)

if __name__ == '__main__':
    unittest.main()

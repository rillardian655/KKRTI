import unittest
from tools.calc_endurance import calculate_endurance

class TestEndurance(unittest.TestCase):
    def test_endurance_calculation(self):
        mins = calculate_endurance(battery_mah=6000, cell_count=4, hover_current_amps=12.0, reserve_pct=20.0)
        self.assertAlmostEqual(mins, 24.0, places=1)

if __name__ == '__main__':
    unittest.main()

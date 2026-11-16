import unittest
from core.thermal_model import BatteryThermalModel

class TestThermal(unittest.TestCase):
    def test_thermal_rise_under_load(self):
        model = BatteryThermalModel(ambient_temp_c=25.0)
        # Heavy load 30A for 60s
        temp = model.update(current_amps=30.0, dt_sec=60.0)
        self.assertTrue(temp > 25.0)

if __name__ == '__main__':
    unittest.main()

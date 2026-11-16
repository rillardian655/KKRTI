import unittest
from core.energy_metrics import calculate_flight_energy

class TestEnergy(unittest.TestCase):
    def test_energy_calculation(self):
        ke, pe, total = calculate_flight_energy(mass_kg=2.0, groundspeed_m_s=10.0, altitude_agl_m=10.0)
        self.assertAlmostEqual(ke, 100.0, places=1)
        self.assertTrue(pe > 190.0)
        self.assertAlmostEqual(total, ke + pe, places=1)

if __name__ == '__main__':
    unittest.main()

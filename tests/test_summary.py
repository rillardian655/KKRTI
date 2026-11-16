import unittest
import os
from tools.flight_summary import generate_summary

class TestSummary(unittest.TestCase):
    def test_summary_calculation(self):
        csv_file = "tests/test_flight.csv"
        with open(csv_file, "w") as f:
            f.write("timestamp,mode,armed,lat,lon,alt_rel,groundspeed,roll,pitch,yaw,battery_pct,voltage\n")
            f.write("100.0,GUIDED,True,-7.92,110.54,12.5,4.0,0.0,0.0,0.0,100,16.8\n")
            f.write("110.0,GUIDED,True,-7.92,110.54,18.0,8.5,0.0,0.0,0.0,99,16.7\n")

        try:
            s = generate_summary(csv_file)
            self.assertEqual(s["records"], 2)
            self.assertAlmostEqual(s["duration_sec"], 10.0)
            self.assertAlmostEqual(s["max_altitude_m"], 18.0)
            self.assertAlmostEqual(s["max_speed_m_s"], 8.5)
        finally:
            if os.path.exists(csv_file):
                os.remove(csv_file)

if __name__ == '__main__':
    unittest.main()

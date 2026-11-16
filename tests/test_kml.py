import unittest
import os
from tools.csv_to_kml import convert_csv_to_kml

class TestKML(unittest.TestCase):
    def test_kml_generation(self):
        csv_file = "tests/dummy.csv"
        kml_file = "tests/dummy.kml"
        with open(csv_file, "w") as f:
            f.write("timestamp,mode,armed,lat,lon,alt_rel,groundspeed,roll,pitch,yaw,battery_pct,voltage\n")
            f.write("0.0,GUIDED,True,-7.92,110.54,10.0,0.0,0.0,0.0,0.0,100,16.8\n")

        try:
            convert_csv_to_kml(csv_file, kml_file)
            self.assertTrue(os.path.exists(kml_file))
        finally:
            if os.path.exists(csv_file): os.remove(csv_file)
            if os.path.exists(kml_file): os.remove(kml_file)

if __name__ == '__main__':
    unittest.main()

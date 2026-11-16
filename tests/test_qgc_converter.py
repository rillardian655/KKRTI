import unittest
import os
import json
from tools.csv_to_qgc import convert_to_qgc_plan

class TestQGCConverter(unittest.TestCase):
    def test_conversion(self):
        csv_file = "tests/test_pts.csv"
        plan_file = "tests/test.plan"
        with open(csv_file, "w") as f:
            f.write("lat,lon,alt_rel\n")
            f.write("-7.9255,110.5485,15.0\n")

        try:
            convert_to_qgc_plan(csv_file, plan_file)
            self.assertTrue(os.path.exists(plan_file))
            with open(plan_file, "r") as f:
                data = json.load(f)
            self.assertEqual(data["fileType"], "Plan")
        finally:
            if os.path.exists(csv_file): os.remove(csv_file)
            if os.path.exists(plan_file): os.remove(plan_file)

if __name__ == '__main__':
    unittest.main()

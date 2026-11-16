import unittest
from core.orientation import euler_to_quaternion, quaternion_to_euler

class TestOrientation(unittest.TestCase):
    def test_identity(self):
        w, x, y, z = euler_to_quaternion(0.0, 0.0, 0.0)
        self.assertAlmostEqual(w, 1.0, places=4)
        self.assertAlmostEqual(x, 0.0, places=4)

    def test_roundtrip_yaw(self):
        w, x, y, z = euler_to_quaternion(0.0, 0.0, 90.0)
        roll, pitch, yaw = quaternion_to_euler(w, x, y, z)
        self.assertAlmostEqual(yaw, 90.0, places=2)

if __name__ == '__main__':
    unittest.main()

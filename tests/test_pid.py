import unittest
from core.pid_controller import PIDController

class TestPID(unittest.TestCase):
    def test_proportional_response(self):
        pid = PIDController(kp=2.0, ki=0.0, kd=0.0, output_min=-10.0, output_max=10.0)
        out = pid.compute(target=5.0, current=0.0, dt=1.0)
        self.assertAlmostEqual(out, 10.0)

    def test_clamping(self):
        pid = PIDController(kp=10.0, ki=0.0, kd=0.0, output_min=-1.0, output_max=1.0)
        out = pid.compute(target=10.0, current=0.0, dt=1.0)
        self.assertEqual(out, 1.0)

    def test_reset(self):
        pid = PIDController(kp=1.0, ki=1.0, kd=0.0)
        pid.compute(target=5.0, current=0.0, dt=1.0)
        self.assertNotEqual(pid.integral, 0.0)
        pid.reset()
        self.assertEqual(pid.integral, 0.0)

if __name__ == '__main__':
    unittest.main()

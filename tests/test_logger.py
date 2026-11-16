import unittest
import os
import shutil
from core.telemetry_logger import TelemetryLogger
from core.telemetry import DroneTelemetry

class TestLogger(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/temp_logs"
        self.logger = TelemetryLogger(log_dir=self.test_dir)

    def tearDown(self):
        self.logger.close()
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_log_entry(self):
        t = DroneTelemetry()
        self.logger.log(t)
        self.assertTrue(os.path.exists(self.logger.file_path))

if __name__ == '__main__':
    unittest.main()

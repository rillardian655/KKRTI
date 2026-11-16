import unittest
import time
from simulator.sitl_runner import SITLRunner
from core.mavlink_bridge import MAVLinkBridge

class TestSITLIntegration(unittest.TestCase):
    def test_mock_sitl_connection(self):
        port = 14599
        runner = SITLRunner(mode="mock", port=port)
        runner.start()
        time.sleep(0.5)

        bridge = MAVLinkBridge(endpoint=f"udp:127.0.0.1:{port}")
        connected = bridge.connect(timeout=5)
        try:
            self.assertTrue(connected)
            snap = bridge.get_snapshot()
            self.assertTrue(snap.is_link_alive())
        finally:
            bridge.disconnect()
            runner.stop()

if __name__ == '__main__':
    unittest.main()

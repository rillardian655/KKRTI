import unittest
from unittest.mock import MagicMock
from core.emergency_stop import trigger_emergency_kill

class TestEmergencyStop(unittest.TestCase):
    def test_kill_switch_none(self):
        self.assertFalse(trigger_emergency_kill(None))

    def test_kill_switch_sends_disarm(self):
        mock_master = MagicMock()
        res = trigger_emergency_kill(mock_master)
        self.assertTrue(res)
        self.assertTrue(mock_master.mav.command_long_send.called)

if __name__ == '__main__':
    unittest.main()

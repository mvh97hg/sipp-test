from pathlib import Path
import signal
import subprocess
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sip_console.cli import main
from sip_console.runner import wait_sipp


class InterruptTests(unittest.TestCase):
    def test_main_keyboardinterrupt_returns_130(self):
        with patch("sip_console.cli.cmd_check", side_effect=KeyboardInterrupt):
            rc = main(["check"])
        self.assertEqual(rc, 130)

    def test_wait_sipp_interrupt_when_child_already_exited(self):
        proc = MagicMock()
        proc.wait.side_effect = KeyboardInterrupt
        proc.poll.return_value = 1
        self.assertEqual(wait_sipp(proc), 130)
        proc.send_signal.assert_not_called()

    def test_wait_sipp_interrupt_stops_running_child(self):
        proc = MagicMock()
        proc.wait.side_effect = [KeyboardInterrupt, 0]
        proc.poll.return_value = None
        self.assertEqual(wait_sipp(proc), 130)
        proc.send_signal.assert_called_once_with(signal.SIGINT)

from io import BytesIO
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sip_console.runner import finish_tee, spawn_sipp, wait_sipp


class LiveOutputTests(unittest.TestCase):
    def test_child_stdout_reaches_terminal_and_log(self):
        captured_out = BytesIO()
        captured_err = BytesIO()
        fake_out = MagicMock()
        fake_out.isatty.return_value = False
        fake_out.buffer = captured_out
        fake_err = MagicMock()
        fake_err.buffer = captured_err
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            stdout_log = cwd / "stdout.log"
            stderr_log = cwd / "stderr.log"
            with patch("sip_console.runner.sys.stdout", fake_out), patch(
                "sip_console.runner.sys.stderr", fake_err
            ):
                proc, workers, files = spawn_sipp(
                    [
                        sys.executable,
                        "-u",
                        "-c",
                        "import sys; print('LIVE-OK'); print('LIVE-ERR', file=sys.stderr)",
                    ],
                    cwd,
                    stdout_log,
                    stderr_log,
                )
                rc = wait_sipp(proc)
                finish_tee(proc, workers, files)
            self.assertEqual(rc, 0)
            self.assertIn(b"LIVE-OK", captured_out.getvalue())
            self.assertIn(b"LIVE-ERR", captured_err.getvalue())
            self.assertIn("LIVE-OK", stdout_log.read_text(encoding="utf-8"))
            self.assertIn("LIVE-ERR", stderr_log.read_text(encoding="utf-8"))

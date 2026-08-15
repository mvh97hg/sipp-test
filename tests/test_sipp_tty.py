from io import BytesIO
from pathlib import Path
import os
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sip_console.runner import attach_tty, run_sipp_child, tty_available


class TtyAttachTests(unittest.TestCase):
    def test_tty_available_requires_both_streams(self):
        stdin = MagicMock()
        stdout = MagicMock()
        stdin.isatty.return_value = True
        stdout.isatty.return_value = False
        with patch("sip_console.runner.sys.stdin", stdin), patch(
            "sip_console.runner.sys.stdout", stdout
        ):
            self.assertFalse(tty_available())
        stdout.isatty.return_value = True
        with patch("sip_console.runner.sys.stdin", stdin), patch(
            "sip_console.runner.sys.stdout", stdout
        ):
            self.assertTrue(tty_available())

    def test_keys_reach_child_tty(self):
        user_in_r, user_in_w = os.pipe()
        user_out_r, user_out_w = os.pipe()
        pid, master_fd = os.forkpty()
        if pid == 0:
            os.execv(
                sys.executable,
                [
                    sys.executable,
                    "-u",
                    "-c",
                    "import sys; c=sys.stdin.read(1); sys.stdout.write('GOT-'+c); sys.stdout.flush()",
                ],
            )
        log = BytesIO()

        def feed() -> None:
            time.sleep(0.15)
            os.write(user_in_w, b"q\n")

        threading.Thread(target=feed, daemon=True).start()
        try:
            rc = attach_tty(
                pid,
                master_fd,
                log,
                stdin_fd=user_in_r,
                stdout_fd=user_out_w,
                make_raw=False,
            )
        finally:
            for fd in (user_in_r, user_in_w, user_out_r, user_out_w):
                try:
                    os.close(fd)
                except OSError:
                    pass
        self.assertEqual(rc, 0)
        self.assertIn(b"GOT-q", log.getvalue())

    def test_run_sipp_child_uses_tty_when_interactive(self):
        stdin = MagicMock()
        stdout = MagicMock()
        stdin.isatty.return_value = True
        stdout.isatty.return_value = True
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            with patch("sip_console.runner.sys.stdin", stdin), patch(
                "sip_console.runner.sys.stdout", stdout
            ), patch("sip_console.runner.run_sipp_on_tty", return_value=0) as tty_run, patch(
                "sip_console.runner.spawn_sipp"
            ) as spawn:
                rc = run_sipp_child(["sipp"], cwd, cwd / "stdout.log", cwd / "stderr.log")
        self.assertEqual(rc, 0)
        tty_run.assert_called_once()
        spawn.assert_not_called()

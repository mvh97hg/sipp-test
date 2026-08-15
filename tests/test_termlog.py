from io import BytesIO
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sip_console.termlog import TermLog, render_sipp_stdout


class TermLogTests(unittest.TestCase):
    def test_plain_text_passes_through(self):
        buf = BytesIO()
        log = TermLog(buf, rows=24, cols=80)
        log.write(b"hello\nworld\n")
        log.flush()
        self.assertEqual(buf.getvalue().decode(), "hello\nworld\n")

    def test_cursor_updates_do_not_append_garbage(self):
        buf = BytesIO()
        log = TermLog(buf, rows=24, cols=80)
        log.write(b"\x1b[H\x1b[2JPort\x1b[3;14H1.00 s")
        log.flush()
        text = buf.getvalue().decode()
        self.assertNotIn("\x1b", text)
        self.assertIn("Port", text)
        self.assertIn("1.00 s", text)
        self.assertNotIn("Port1.00", text.replace(" ", ""))

    def test_real_sipp_curses_dump_is_readable(self):
        raw = (
            b"\x1b[?1049h\x1b[H\x1b[2J"
            b"------------------------------ Scenario Screen --------\n"
            b"\x1b[3;3H5060\x1b[14G0.00 s\x1b[3;32H0  UDP"
            b"\x1b[H\x1b[2J\x1b[?1049l\r"
            b"------------------------------ Scenario Screen --------\n"
            b"  Port   Total-time  Total-calls  Transport\n"
            b"  5060      22.86 s            0  UDP\n"
            b"------------------------------ Test Terminated --------------------------------\n"
        )
        text = render_sipp_stdout(raw)
        self.assertNotIn("\x1b", text)
        self.assertIn("22.86 s", text)
        self.assertIn("Test Terminated", text)
        self.assertIn("Total-calls", text)
        self.assertLess(text.count("Scenario Screen"), 3)

    def test_overwrite_file_stays_single_snapshot(self):
        buf = BytesIO()
        log = TermLog(buf, rows=24, cols=80)
        log.write(b"\x1b[H\x1b[2Jfirst")
        log.write(b"\x1b[H\x1b[2Jsecond")
        log.flush()
        text = buf.getvalue().decode()
        self.assertIn("second", text)
        self.assertNotIn("first", text)

    def test_existing_uas_run_log(self):
        path = Path("/home/code/sip-test-console/logs/20260815-091352-uas-answer/stdout.log")
        if not path.is_file():
            self.skipTest("sample log missing")
        text = render_sipp_stdout(path.read_bytes())
        self.assertNotIn("\x1b", text)
        self.assertIn("Statistics Screen", text)
        self.assertIn("Test Terminated", text)

from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sip_console.result import normalize_sipp_exit

HEADER = (
    "TotalCallCreated;CurrentCall;SuccessfulCall(P);SuccessfulCall(C);"
    "FailedCall(P);FailedCall(C)\n"
)


class NormalizeSippExitTests(unittest.TestCase):
    def _csv(self, td: str, body: str) -> Path:
        path = Path(td) / "statistics.csv"
        path.write_text(HEADER + body, encoding="utf-8")
        return path

    def test_zero_stays_zero(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._csv(td, "100;0;0;100;0;0\n")
            self.assertEqual(normalize_sipp_exit(0, path), 0)

    def test_segfault_after_all_calls_pass(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._csv(td, "100;0;0;100;0;0\n")
            self.assertEqual(normalize_sipp_exit(-11, path), 0)

    def test_segfault_with_failures_stays_error(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._csv(td, "100;0;0;80;0;20\n")
            self.assertEqual(normalize_sipp_exit(-11, path), -11)

    def test_segfault_while_calls_still_running(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._csv(td, "100;12;0;88;0;0\n")
            self.assertEqual(normalize_sipp_exit(-11, path), -11)

    def test_other_exit_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._csv(td, "100;0;0;100;0;0\n")
            self.assertEqual(normalize_sipp_exit(1, path), 1)

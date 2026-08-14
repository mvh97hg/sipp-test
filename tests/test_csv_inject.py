import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sip_console.csv_inject import normalize_rows, write_normalized_csv, target_host


class TargetHostTests(unittest.TestCase):
    def test_host_port(self):
        self.assertEqual(target_host("10.1.2.3:5060"), "10.1.2.3")

    def test_ipv6_literal(self):
        self.assertEqual(target_host("[2001:db8::1]:5060"), "2001:db8::1")


class NormalizeTests(unittest.TestCase):
    def test_pads_auth_from_env_fallbacks(self):
        rows = [["SEQUENTIAL"], ["1000", "2000", "pbx.example.com"]]
        out = normalize_rows(
            rows, target="210.211.122.104:5090",
            auth_user="alice", auth_pass="secret",
        )
        self.assertEqual(out[0], ["SEQUENTIAL"])
        self.assertEqual(out[1], ["1000", "2000", "pbx.example.com", "alice", "secret", ""])

    def test_csv_auth_wins_over_env(self):
        rows = [["SEQUENTIAL"], ["1000", "2000", "pbx.example.com", "bob", "p2"]]
        out = normalize_rows(rows, auth_user="alice", auth_pass="secret")
        self.assertEqual(out[1][3], "bob")
        self.assertEqual(out[1][4], "p2")

    def test_domain_fallback_chain(self):
        rows = [["SEQUENTIAL"], ["1000", "2000"]]
        out = normalize_rows(rows, domain="from.env", target="9.9.9.9:5060")
        self.assertEqual(out[1][2], "from.env")
        out2 = normalize_rows(rows, target="9.9.9.9:5060")
        self.assertEqual(out2[1][2], "9.9.9.9")

    def test_service_fallback(self):
        rows = [["SEQUENTIAL"], ["1000", ""]]
        out = normalize_rows(rows, service="2000", target="1.1.1.1:5060")
        self.assertEqual(out[1][1], "2000")

    def test_empty_auth_allowed(self):
        rows = [["SEQUENTIAL"], ["1000", "2000", "pbx.example.com"]]
        out = normalize_rows(rows, target="1.1.1.1:5060")
        self.assertEqual(out[1][3], "")
        self.assertEqual(out[1][4], "")

    def test_contact_is_not_field3(self):
        rows = [["SEQUENTIAL"], ["1000", "2000", "pbx.example.com"]]
        out = normalize_rows(rows, target="1.1.1.1:5060", auth_user="u")
        self.assertEqual(len(out[1]), 6)
        self.assertEqual(out[1][3], "u")
        self.assertEqual(out[1][5], "")

    def test_advertise_ip_is_field5(self):
        rows = [["SEQUENTIAL"], ["1000", "2000", "pbx.example.com"]]
        out = normalize_rows(rows, target="1.1.1.1:5060", advertise_ip="203.0.113.9")
        self.assertEqual(out[1][5], "203.0.113.9")

    def test_write_semicolon_file(self):
        with tempfile.TemporaryDirectory() as td:
            inp = Path(td) / "in.csv"
            out = Path(td) / "out.csv"
            inp.write_text("SEQUENTIAL\n1000;2000;pbx.example.com\n", encoding="utf-8")
            write_normalized_csv(
                inp, out, target="210.211.122.104:5090",
                auth_user="alice", auth_pass="x", advertise_ip="9.9.9.9",
            )
            text = out.read_text(encoding="utf-8")
            self.assertIn("1000;2000;pbx.example.com;alice;x;9.9.9.9", text)

    def test_missing_caller_raises(self):
        with self.assertRaises(SystemExit):
            normalize_rows([["SEQUENTIAL"], ["", "2000"]], target="1.1.1.1:5060")


if __name__ == "__main__":
    unittest.main()

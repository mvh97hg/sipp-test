from pathlib import Path
import os
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sip_console.envfile import load_env_file, parse_env_line


class ParseEnvLineTests(unittest.TestCase):
    def test_plain_and_quoted(self):
        self.assertEqual(parse_env_line("SIP_TARGET=10.0.0.1:5060"), ("SIP_TARGET", "10.0.0.1:5060"))
        self.assertEqual(parse_env_line('SIP_PASS="a b"'), ("SIP_PASS", "a b"))
        self.assertEqual(parse_env_line("SIP_PASS='secret'"), ("SIP_PASS", "secret"))
        self.assertEqual(parse_env_line("export SIP_SERVICE=1000"), ("SIP_SERVICE", "1000"))

    def test_skip_comments(self):
        self.assertIsNone(parse_env_line("# comment"))
        self.assertIsNone(parse_env_line(""))
        self.assertIsNone(parse_env_line("  "))


class LoadEnvFileTests(unittest.TestCase):
    def test_fills_missing_does_not_override(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / ".env"
            path.write_text(
                "SIP_TARGET=from-file:5060\nSIP_SERVICE=from-file\n",
                encoding="utf-8",
            )
            env = {"SIP_TARGET": "from-shell:5060"}
            loaded = load_env_file(path, environ=env)
            self.assertEqual(loaded, ["SIP_SERVICE"])
            self.assertEqual(env["SIP_TARGET"], "from-shell:5060")
            self.assertEqual(env["SIP_SERVICE"], "from-file")

    def test_missing_file_is_ok(self):
        self.assertEqual(load_env_file(Path("/no/such/.env"), environ={}), [])

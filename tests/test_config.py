import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sip_console.config import transport_mode, resolve_local_ip, is_uas, needs_media

class TransportTests(unittest.TestCase):
    def test_udp(self):
        self.assertEqual(transport_mode("udp"), "u1")
    def test_passthrough(self):
        self.assertEqual(transport_mode("tn"), "tn")
    def test_bad(self):
        with self.assertRaises(SystemExit):
            transport_mode("sctp")

class LocalIpTests(unittest.TestCase):
    def test_external_wins(self):
        self.assertEqual(
            resolve_local_ip({"SIP_EXTERNAL_IP": "1.2.3.4", "SIP_LOCAL_IP": "10.0.0.1"}),
            "1.2.3.4",
        )
    def test_contact_host_alias(self):
        self.assertEqual(
            resolve_local_ip({"SIP_CONTACT_HOST": "9.9.9.9", "SIP_LOCAL_IP": "10.0.0.1"}),
            "9.9.9.9",
        )
    def test_local_ip(self):
        self.assertEqual(resolve_local_ip({"SIP_LOCAL_IP": "10.0.0.1"}), "10.0.0.1")
    def test_default(self):
        self.assertEqual(resolve_local_ip({}), "127.0.0.1")

class ScenarioTests(unittest.TestCase):
    def test_uas(self):
        self.assertTrue(is_uas("uas-answer"))
        self.assertFalse(is_uas("uac-basic"))
    def test_media(self):
        self.assertTrue(needs_media("uac-basic"))
        self.assertTrue(needs_media("uas-answer"))

    def test_debug_flag(self):
        from sip_console.config import debug_enabled
        self.assertFalse(debug_enabled({}))
        self.assertTrue(debug_enabled({"SIP_DEBUG": "1"}))
        self.assertTrue(debug_enabled({}, True))


if __name__ == "__main__":
    unittest.main()

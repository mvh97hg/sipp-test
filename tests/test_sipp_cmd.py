from pathlib import Path
import sys, tempfile, unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sip_console.sipp_cmd import build_sipp_cmd

class BuildTests(unittest.TestCase):
    def setUp(self):
        self.root = Path("/home/code/sip-test-console")
        self.art = Path("/tmp/art")

    def test_uac_has_target_and_contact(self):
        cmd = build_sipp_cmd(
            root=self.root, scenario="uac-basic", target="10.0.0.5:5060",
            service="1000", transport="udp",             local_ip="1.2.3.4",
            local_port="", media_ip="1.2.3.4", media_port="6000",
            csv_path=Path("/tmp/u.csv"),
            artifact_dir=self.art, call_limit=1,
        )
        self.assertEqual(cmd[0], "sipp")
        self.assertEqual(cmd[1], "10.0.0.5:5060")
        self.assertEqual(cmd[cmd.index("-i") + 1], "1.2.3.4")
        self.assertIn("-inf", cmd)
        self.assertEqual(cmd[cmd.index("-t") + 1], "u1")
        self.assertEqual(cmd[cmd.index("-stf") + 1], "/tmp/art/statistics.csv")
        self.assertEqual(cmd[cmd.index("-shortmessage_file") + 1], "/tmp/art/shortmessages.log")
        self.assertEqual(cmd[cmd.index("-d") + 1], "5000")
        self.assertEqual(cmd[cmd.index("-recv_timeout") + 1], "5000")
        self.assertNotIn("-trace_msg", cmd)
        self.assertNotIn("-message_file", cmd)
        self.assertNotIn("-trace_calldebug", cmd)
        self.assertNotIn("-calldebug_file", cmd)

    def test_options_has_no_media_ports(self):
        cmd = build_sipp_cmd(
            root=self.root, scenario="uac-options", target="10.0.0.5:5060",
            service="1000", transport="udp", local_ip="1.2.3.4",
            local_port="", media_ip="1.2.3.4", media_port="6000",
            csv_path=Path("/tmp/u.csv"), artifact_dir=self.art, call_limit=1,
        )
        self.assertNotIn("-mp", cmd)
        self.assertNotIn("-mi", cmd)

    def test_debug_enables_calldebug_not_messages(self):
        cmd = build_sipp_cmd(
            root=self.root, scenario="uac-basic", target="10.0.0.5:5060",
            service="1000", transport="udp", local_ip="1.2.3.4",
            local_port="", media_ip="1.2.3.4", media_port="6000",
            csv_path=Path("/tmp/u.csv"),
            artifact_dir=self.art, call_limit=1, debug=True,
        )
        self.assertNotIn("-trace_msg", cmd)
        self.assertNotIn("-message_file", cmd)
        self.assertIn("-trace_calldebug", cmd)
        self.assertEqual(cmd[cmd.index("-calldebug_file") + 1], "/tmp/art/calldebug.log")

    def test_uas_has_no_remote_target(self):
        cmd = build_sipp_cmd(
            root=self.root, scenario="uas-answer", target="10.0.0.5:5060",
            service="", transport="udp", local_ip="10.0.0.9",
            local_port="5060", media_ip="10.0.0.9", media_port="6000",
            csv_path=None,
            artifact_dir=self.art, call_limit=1,
        )
        self.assertNotIn("10.0.0.5:5060", cmd)
        self.assertEqual(cmd[cmd.index("-p") + 1], "5060")
        self.assertNotIn("-inf", cmd)
        self.assertEqual(cmd[cmd.index("-i") + 1], "10.0.0.9")

    def test_uas_inf_when_csv(self):
        cmd = build_sipp_cmd(
            root=self.root, scenario="uas-answer", target="10.0.0.5:5060",
            service="", transport="udp", local_ip="10.0.0.9",
            local_port="5060", media_ip="203.0.113.1", media_port="6000",
            csv_path=Path("/tmp/u.csv"),
            artifact_dir=self.art, call_limit=1,
        )
        self.assertIn("-inf", cmd)
        self.assertEqual(cmd[cmd.index("-mi") + 1], "203.0.113.1")

    def test_refer_passes_key(self):
        cmd = build_sipp_cmd(
            root=self.root, scenario="uac-refer", target="10.0.0.5:5060",
            service="1000", transport="udp", local_ip="1.2.3.4",
            local_port="", media_ip="1.2.3.4", media_port="6000",
            csv_path=Path("/tmp/u.csv"), artifact_dir=self.art, call_limit=1,
            refer_to="sip:1001@example.com",
        )
        self.assertEqual(cmd[cmd.index("-key") + 1], "refer_to")
        self.assertEqual(cmd[cmd.index("-key") + 2], "sip:1001@example.com")

    def test_tls_flags_only_for_tls(self):
        udp = build_sipp_cmd(
            root=self.root, scenario="uac-options", target="10.0.0.5:5060",
            service="1000", transport="udp", local_ip="1.2.3.4",
            local_port="", media_ip="1.2.3.4", media_port="6000",
            csv_path=Path("/tmp/u.csv"), artifact_dir=self.art, call_limit=1,
            tls_cert="/tmp/cert.pem",
        )
        self.assertNotIn("-tls_cert", udp)
        tls = build_sipp_cmd(
            root=self.root, scenario="uac-options", target="10.0.0.5:5060",
            service="1000", transport="tls", local_ip="1.2.3.4",
            local_port="", media_ip="1.2.3.4", media_port="6000",
            csv_path=Path("/tmp/u.csv"), artifact_dir=self.art, call_limit=1,
            tls_cert="/tmp/cert.pem", tls_key="/tmp/key.pem", tls_ca="/tmp/ca.pem",
        )
        self.assertEqual(tls[tls.index("-tls_cert") + 1], "/tmp/cert.pem")
        self.assertEqual(tls[tls.index("-tls_key") + 1], "/tmp/key.pem")
        self.assertEqual(tls[tls.index("-tls_ca") + 1], "/tmp/ca.pem")


if __name__ == "__main__":
    unittest.main()

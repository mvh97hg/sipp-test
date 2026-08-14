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
        self.assertNotIn("-set", cmd)
        self.assertNotIn("-key", cmd)
        self.assertEqual(cmd[cmd.index("-i") + 1], "1.2.3.4")
        self.assertIn("-inf", cmd)
        self.assertEqual(cmd[cmd.index("-t") + 1], "u1")
        self.assertEqual(cmd[cmd.index("-stf") + 1], "/tmp/art/statistics.csv")
        self.assertEqual(cmd[cmd.index("-shortmessage_file") + 1], "/tmp/art/shortmessages.log")
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


if __name__ == "__main__":
    unittest.main()

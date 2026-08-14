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
            service="1000", transport="udp", local_ip="10.0.0.9",
            local_port="", media_ip="1.2.3.4", media_port="6000",
            contact_host="1.2.3.4", csv_path=Path("/tmp/u.csv"),
            artifact_dir=self.art, call_limit=1,
        )
        self.assertEqual(cmd[0], "sipp")
        self.assertEqual(cmd[1], "10.0.0.5:5060")
        self.assertIn("-set", cmd)
        i = cmd.index("-set")
        self.assertEqual(cmd[i:i+3], ["-set", "contact_host", "1.2.3.4"])
        self.assertIn("-inf", cmd)
        self.assertEqual(cmd[cmd.index("-t") + 1], "u1")

    def test_uas_has_no_remote_target(self):
        cmd = build_sipp_cmd(
            root=self.root, scenario="uas-answer", target="10.0.0.5:5060",
            service="", transport="udp", local_ip="10.0.0.9",
            local_port="5060", media_ip="10.0.0.9", media_port="6000",
            contact_host="10.0.0.9", csv_path=None,
            artifact_dir=self.art, call_limit=1,
        )
        self.assertNotIn("10.0.0.5:5060", cmd)
        self.assertEqual(cmd[cmd.index("-p") + 1], "5060")
        self.assertNotIn("-inf", cmd)
        i = cmd.index("-set")
        self.assertEqual(cmd[i : i + 3], ["-set", "contact_host", "10.0.0.9"])


if __name__ == "__main__":
    unittest.main()

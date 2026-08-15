from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sip_console.config import hold_ms
from sip_console.sipp_cmd import build_sipp_cmd

ROOT = Path(__file__).resolve().parents[1]
UAC_XML = [
    ROOT / "scenarios/uac/uac-basic.xml",
    ROOT / "scenarios/features/uac-auth.xml",
    ROOT / "scenarios/features/dtmf.xml",
    ROOT / "scenarios/media/rtp-echo.xml",
]


class HangupTests(unittest.TestCase):
    def test_uac_answers_peer_bye_instead_of_sending_bye(self):
        for path in UAC_XML:
            text = path.read_text(encoding="utf-8")
            self.assertIn('<recv request="BYE" ontimeout="local-bye', text, msg=path.name)
            self.assertIn("SIP/2.0 200 OK", text, msg=path.name)
            self.assertNotIn("CSeq: [last_CSeq:]", text, msg=path.name)
            self.assertIn("[last_CSeq:]", text, msg=path.name)
            self.assertIn("CSeq: [last_cseq_number+1] BYE", text, msg=path.name)

    def test_sipp_does_not_abort_on_in_dialog_noise(self):
        cmd = build_sipp_cmd(
            root=ROOT,
            scenario="uac-basic",
            target="10.0.0.5:5060",
            service="1000",
            transport="udp",
            local_ip="1.2.3.4",
            local_port="",
            media_ip="1.2.3.4",
            media_port="6000",
            csv_path=Path("/tmp/u.csv"),
            artifact_dir=Path("/tmp/art"),
            call_limit=1,
        )
        self.assertIn("-aa", cmd)
        i = cmd.index("-default_behaviors")
        self.assertEqual(cmd[i + 1], "all,-abortunexp")
        self.assertEqual(cmd[cmd.index("-recv_timeout") + 1], "5000")

    def test_uas_has_recv_timeout_equal_to_hold(self):
        hold = hold_ms({}, "uas-answer")
        cmd = build_sipp_cmd(
            root=ROOT,
            scenario="uas-answer",
            target="10.0.0.5:5060",
            service="",
            transport="udp",
            local_ip="10.0.0.9",
            local_port="5060",
            media_ip="10.0.0.9",
            media_port="6000",
            csv_path=None,
            artifact_dir=Path("/tmp/art"),
            call_limit=1,
            hold_ms=hold,
        )
        self.assertEqual(hold, 10000)
        self.assertEqual(cmd[cmd.index("-recv_timeout") + 1], "10000")

    def test_hangup_200_has_timeout(self):
        for path in UAC_XML:
            for line in path.read_text(encoding="utf-8").splitlines():
                if 'recv response="200"' not in line:
                    continue
                if "optional" in line or "rrs=" in line:
                    continue
                self.assertIn("timeout=", line, msg=f"{path.name}: {line}")

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
ROOT = Path(__file__).resolve().parents[1]


class NegativeAckTests(unittest.TestCase):
    def test_busy_acks_486(self):
        text = (ROOT / "scenarios/negative/uac-busy.xml").read_text(encoding="utf-8")
        self.assertIn('recv response="486"', text)
        self.assertIn("CSeq: 1 ACK", text)
        self.assertIn("CSeq: 2 ACK", text)
        idx_486 = text.find('recv response="486"')
        idx_ack = text.find("ACK sip:", idx_486)
        self.assertGreater(idx_ack, idx_486)

    def test_default_uac_does_not_advertise_100rel(self):
        for rel in (
            "scenarios/uac/uac-basic.xml",
            "scenarios/features/uac-auth.xml",
            "scenarios/features/dtmf.xml",
            "scenarios/media/rtp-echo.xml",
        ):
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertNotIn("100rel", text, msg=rel)

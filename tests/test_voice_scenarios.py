from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
ROOT = Path(__file__).resolve().parents[1]


class CancelXmlTests(unittest.TestCase):
    def test_cancel_then_487_ack(self):
        text = (ROOT / "scenarios/signaling/uac-cancel.xml").read_text(encoding="utf-8")
        self.assertIn("CANCEL", text)
        self.assertIn('recv response="487"', text)
        idx = text.find('recv response="487"')
        self.assertGreater(text.find("ACK sip:", idx), idx)


class HoldReinviteTests(unittest.TestCase):
    def test_hold_sendonly_then_sendrecv(self):
        text = (ROOT / "scenarios/features/uac-hold.xml").read_text(encoding="utf-8")
        self.assertIn("a=sendonly", text)
        self.assertIn("a=sendrecv", text)
        self.assertIn("INVITE [next_url]", text)


class PrackXmlTests(unittest.TestCase):
    def test_prack_has_100rel(self):
        text = (ROOT / "scenarios/features/uac-prack.xml").read_text(encoding="utf-8")
        self.assertIn("100rel", text)
        self.assertIn("PRACK", text)
        self.assertIn("RAck:", text)


class ReferXmlTests(unittest.TestCase):
    def test_refer_uses_next_url(self):
        text = (ROOT / "scenarios/features/uac-refer.xml").read_text(encoding="utf-8")
        self.assertIn("REFER [next_url]", text)
        self.assertIn("[refer_to]", text)

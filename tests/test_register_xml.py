from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
ROOT = Path(__file__).resolve().parents[1]


class RegisterXmlTests(unittest.TestCase):
    def test_register_then_unregister(self):
        text = (ROOT / "scenarios/signaling/uac-register.xml").read_text(encoding="utf-8")
        self.assertIn("REGISTER sip:[field2]", text)
        self.assertEqual(text.count("Expires: 3600"), 2)
        self.assertIn("Expires: 0", text)
        self.assertIn("[authentication username=[field3] password=[field4]]", text)
        self.assertIn("@[field5]", text)

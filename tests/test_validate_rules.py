import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sip_console.validate import validate_xml_text

GOOD_XML = """<?xml version="1.0" encoding="ISO-8859-1" ?>
<scenario name="fixture-ok">
  <recv response="401" auth="true" optional="true"/>
  <recv response="407" auth="true" optional="true"/>
  <send><![CDATA[
INVITE sip:[field1]@[field2] SIP/2.0
Contact: <sip:[field0]@[contact_host]:[local_port];transport=[transport]>
[authentication username=[field3] password=[field4]]
  ]]></send>
</scenario>
"""

BAD_CONTACT_XML = """<?xml version="1.0" encoding="ISO-8859-1" ?>
<scenario name="fixture-bad-contact">
  <recv response="401" auth="true" optional="true"/>
  <recv response="407" auth="true" optional="true"/>
  <send><![CDATA[
INVITE sip:[field1]@[field2] SIP/2.0
Contact: <sip:[field0]@[field3]:[local_port];transport=[transport]>
[authentication username=[field3] password=[field4]]
  ]]></send>
</scenario>
"""


class ValidateRulesTests(unittest.TestCase):
    def test_auth_present_fixture_passes(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ok.xml"
            path.write_text(GOOD_XML, encoding="utf-8")
            validate_xml_text(path.read_text(encoding="utf-8"), uas=False)

    def test_field3_in_contact_fails(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad.xml"
            path.write_text(BAD_CONTACT_XML, encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                validate_xml_text(path.read_text(encoding="utf-8"), uas=False)
            self.assertIn("field3", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()

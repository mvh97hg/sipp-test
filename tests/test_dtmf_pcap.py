from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sip_console.dtmf_pcap import write_rfc4733_digit_pcap


class DtmfPcapTests(unittest.TestCase):
    def test_pcap_is_ethernet_ipv4_udp_rtp(self):
        with tempfile.TemporaryDirectory() as td:
            path = write_rfc4733_digit_pcap(Path(td) / "d.pcap", digit=1)
            data = path.read_bytes()
            self.assertGreater(len(data), 64)
            self.assertEqual(data[:4], b"\xd4\xc3\xb2\xa1")

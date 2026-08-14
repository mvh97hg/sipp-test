import struct
import unittest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sip_console.net import (
    DEFAULT_STUN_SERVER,
    detect_local_ip,
    parse_stun_mapped_ipv4,
    resolve_bind_advertise,
    stun_server_host_port,
    target_host_port,
)

MAGIC = 0x2112A442


def _xor_mapped_packet(ip: str, port: int) -> bytes:
    txid = b"\x00" * 12
    header = struct.pack("!HHI", 0x0101, 12, MAGIC) + txid
    family = b"\x00\x01"
    xport = port ^ (MAGIC >> 16)
    ip_int = struct.unpack("!I", bytes(int(p) for p in ip.split(".")))[0]
    xip = ip_int ^ MAGIC
    attr = struct.pack("!HH", 0x0020, 8) + family + struct.pack("!HI", xport, xip)
    return header + attr


class TargetHostPortTests(unittest.TestCase):
    def test_host_port(self):
        self.assertEqual(target_host_port("10.1.2.3:5090"), ("10.1.2.3", 5090))

    def test_host_only(self):
        self.assertEqual(target_host_port("10.1.2.3"), ("10.1.2.3", 5060))


class StunParseTests(unittest.TestCase):
    def test_xor_mapped_address(self):
        pkt = _xor_mapped_packet("203.0.113.10", 3478)
        self.assertEqual(parse_stun_mapped_ipv4(pkt), "203.0.113.10")

    def test_too_short(self):
        self.assertIsNone(parse_stun_mapped_ipv4(b"short"))


class StunServerTests(unittest.TestCase):
    def test_default(self):
        self.assertEqual(stun_server_host_port({}), ("stun.l.google.com", 19302))
        self.assertEqual(DEFAULT_STUN_SERVER, "stun.l.google.com:19302")

    def test_override(self):
        self.assertEqual(
            stun_server_host_port({"SIP_STUN_SERVER": "stun.example.com:3478"}),
            ("stun.example.com", 3478),
        )


class DetectLocalIpTests(unittest.TestCase):
    def test_uses_getsockname(self):
        sock = MagicMock()
        sock.getsockname.return_value = ("192.168.1.50", 5555)
        with patch("sip_console.net.socket.socket", return_value=sock):
            ip = detect_local_ip("8.8.8.8", 5060)
        sock.connect.assert_called_once_with(("8.8.8.8", 5060))
        self.assertEqual(ip, "192.168.1.50")
        sock.close.assert_called_once()


class ResolveBindAdvertiseTests(unittest.TestCase):
    def test_env_external_skips_stun(self):
        with patch("sip_console.net.detect_local_ip", return_value="10.0.0.2"):
            with patch("sip_console.net.stun_public_ip") as stun:
                bind, adv = resolve_bind_advertise(
                    {
                        "SIP_LOCAL_IP": "10.0.0.2",
                        "SIP_EXTERNAL_IP": "198.51.100.9",
                    },
                    "10.1.1.1:5060",
                )
        stun.assert_not_called()
        self.assertEqual(bind, "10.0.0.2")
        self.assertEqual(adv, "198.51.100.9")

    def test_stun_when_target_is_public(self):
        with patch("sip_console.net.detect_local_ip", return_value="10.0.0.2"):
            with patch("sip_console.net.stun_public_ip", return_value="198.51.100.1"):
                bind, adv = resolve_bind_advertise({}, "8.8.8.8:5060")
        self.assertEqual(bind, "10.0.0.2")
        self.assertEqual(adv, "198.51.100.1")

    def test_lan_to_lan_skips_stun(self):
        with patch("sip_console.net.stun_public_ip") as stun:
            bind, adv = resolve_bind_advertise(
                {"SIP_LOCAL_IP": "172.16.30.110"},
                "172.16.30.15:5090",
            )
        stun.assert_not_called()
        self.assertEqual(bind, "172.16.30.110")
        self.assertEqual(adv, "172.16.30.110")

    def test_private_target_skips_stun(self):
        with patch("sip_console.net.stun_public_ip") as stun:
            bind, adv = resolve_bind_advertise(
                {"SIP_LOCAL_IP": "10.0.0.2"},
                "10.1.1.1:5060",
            )
        stun.assert_not_called()
        self.assertEqual((bind, adv), ("10.0.0.2", "10.0.0.2"))

    def test_stun_disabled(self):
        with patch("sip_console.net.detect_local_ip", return_value="10.0.0.2"):
            with patch("sip_console.net.stun_public_ip") as stun:
                bind, adv = resolve_bind_advertise({"SIP_STUN": "0"}, "10.1.1.1:5060")
        stun.assert_not_called()
        self.assertEqual(bind, "10.0.0.2")
        self.assertEqual(adv, "10.0.0.2")

    def test_stun_failure_falls_back_to_bind(self):
        with patch("sip_console.net.detect_local_ip", return_value="10.0.0.2"):
            with patch("sip_console.net.stun_public_ip", return_value=None):
                bind, adv = resolve_bind_advertise({}, "8.8.8.8:5060")
        self.assertEqual((bind, adv), ("10.0.0.2", "10.0.0.2"))


if __name__ == "__main__":
    unittest.main()

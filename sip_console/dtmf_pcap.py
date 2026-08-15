from __future__ import annotations

import struct
from pathlib import Path


def write_rfc4733_digit_pcap(path: Path, *, digit: int = 1, pt: int = 101) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Little-endian pcap: Ethernet / IPv4 / UDP / RTP / RFC4733
    gh = struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)
    rtp = struct.pack("!BBHII", 0x80, pt, 1, 160, 0x11111111)
    event = struct.pack("!BBH", digit & 0xFF, 0x80, 1600)
    payload = rtp + event
    udp = struct.pack("!HHHH", 4000, 5000, 8 + len(payload), 0) + payload
    ip_len = 20 + len(udp)
    ip = struct.pack(
        "!BBHHHBBH4s4s",
        0x45,
        0,
        ip_len,
        1,
        0,
        64,
        17,
        0,
        bytes([10, 0, 0, 1]),
        bytes([10, 0, 0, 2]),
    )
    frame = bytes([0xFF] * 12) + b"\x08\x00" + ip + udp
    rec = struct.pack("<IIII", 0, 0, len(frame), len(frame)) + frame
    path.write_bytes(gh + rec)
    return path

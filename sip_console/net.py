from __future__ import annotations

import os
import socket
import struct
from typing import Mapping

DEFAULT_STUN_SERVER = "stun.l.google.com:19302"
MAGIC_COOKIE = 0x2112A442
_STUN_BINDING_REQUEST = 0x0001
_STUN_XOR_MAPPED = 0x0020
_STUN_MAPPED = 0x0001


def target_host_port(target: str) -> tuple[str, int]:
    target = (target or "").strip() or "127.0.0.1:5060"
    if target.startswith("["):
        end = target.find("]")
        host = target[1:end] if end >= 0 else target
        rest = target[end + 1 :] if end >= 0 else ""
        if rest.startswith(":") and rest[1:].isdigit():
            return host, int(rest[1:])
        return host, 5060
    if target.count(":") == 1:
        host, port_s = target.rsplit(":", 1)
        if port_s.isdigit():
            return host, int(port_s)
    return target, 5060


def stun_server_host_port(env: Mapping[str, str]) -> tuple[str, int]:
    raw = (env.get("SIP_STUN_SERVER") or DEFAULT_STUN_SERVER).strip()
    return target_host_port(raw if ":" in raw else f"{raw}:3478")


def detect_local_ip(dest_host: str, dest_port: int) -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect((dest_host, dest_port))
        ip = sock.getsockname()[0]
    except OSError:
        ip = "127.0.0.1"
    finally:
        sock.close()
    return ip


def parse_stun_mapped_ipv4(packet: bytes) -> str | None:
    if len(packet) < 20:
        return None
    offset = 20
    total = len(packet)
    while offset + 4 <= total:
        atype, alen = struct.unpack_from("!HH", packet, offset)
        offset += 4
        value = packet[offset : offset + alen]
        offset += (alen + 3) & ~3
        if len(value) < 8:
            continue
        family = struct.unpack_from("!H", value, 0)[0]
        if family != 0x0001:
            continue
        port = struct.unpack_from("!H", value, 2)[0]
        addr = struct.unpack_from("!I", value, 4)[0]
        if atype == _STUN_XOR_MAPPED:
            addr ^= MAGIC_COOKIE
            port ^= MAGIC_COOKIE >> 16
        elif atype != _STUN_MAPPED:
            continue
        return socket.inet_ntoa(struct.pack("!I", addr))
    return None


def stun_public_ip(
    host: str = "stun.l.google.com",
    port: int = 19302,
    timeout: float = 2.0,
) -> str | None:
    txid = os.urandom(12)
    req = struct.pack("!HHI", _STUN_BINDING_REQUEST, 0, MAGIC_COOKIE) + txid
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(req, (host, port))
        data, _addr = sock.recvfrom(2048)
    except OSError:
        return None
    finally:
        sock.close()
    return parse_stun_mapped_ipv4(data)


def _truthy_disabled(value: str) -> bool:
    return value.strip().lower() in ("0", "false", "no", "off")


def resolve_bind_advertise(env: Mapping[str, str], target: str) -> tuple[str, str]:
    dest_host, dest_port = target_host_port(env.get("SIP_TARGET", target) or target)
    bind = (env.get("SIP_LOCAL_IP") or "").strip() or detect_local_ip(dest_host, dest_port)
    advertised = (env.get("SIP_EXTERNAL_IP") or env.get("SIP_CONTACT_HOST") or "").strip()
    if advertised:
        return bind, advertised
    stun_on = not _truthy_disabled(env.get("SIP_STUN", "1"))
    if stun_on:
        shost, sport = stun_server_host_port(env)
        mapped = stun_public_ip(shost, sport)
        if mapped:
            return bind, mapped
    return bind, bind

from __future__ import annotations
from pathlib import Path
from typing import Mapping

TRANSPORT = {
    "udp": "u1", "udp-per-call": "un", "udp_multi": "un", "udp-multi": "un",
    "tcp": "t1", "tcp-per-call": "tn", "tcp_multi": "tn", "tcp-multi": "tn",
    "tls": "l1", "tls-per-call": "ln", "tls_multi": "ln", "tls-multi": "ln",
    "u1": "u1", "un": "un", "t1": "t1", "tn": "tn", "l1": "l1", "ln": "ln",
}

# name -> (relative path from repo root, "uac"|"uas")
SCENARIOS = {
    "uac-basic": ("scenarios/uac/uac-basic.xml", "uac"),
    "uas-answer": ("scenarios/uas/uas-answer.xml", "uas"),
    "dtmf": ("scenarios/features/dtmf.xml", "uac"),
    "rtp-echo": ("scenarios/media/rtp-echo.xml", "uac"),
    "uac-auth": ("scenarios/features/uac-auth.xml", "uac"),
    "uac-busy": ("scenarios/negative/uac-busy.xml", "uac"),
    "uac-notfound": ("scenarios/negative/uac-notfound.xml", "uac"),
    "uac-service-unavailable": ("scenarios/negative/uac-service-unavailable.xml", "uac"),
}

MEDIA_SCENARIOS = {"uac-basic", "dtmf", "rtp-echo", "uas-answer", "uac-auth", "uac-busy", "uac-notfound", "uac-service-unavailable"}

# Seconds on hold after ACK (before local BYE), if nothing else is set.
SCENARIO_HOLD_S = {
    "uac-basic": 5,
    "uac-auth": 5,
    "rtp-echo": 10,
    "dtmf": 5,
    "uas-answer": 10,
}


def hold_ms(
    env: Mapping[str, str],
    scenario: str,
    duration_s: float | None = None,
) -> int:
    if duration_s is not None:
        return max(1, int(float(duration_s) * 1000))
    raw_ms = (env.get("SIP_HOLD_MS") or "").strip()
    if raw_ms:
        return max(1, int(raw_ms))
    raw_s = (env.get("SIP_CALL_DURATION") or "").strip()
    if raw_s:
        return max(1, int(float(raw_s) * 1000))
    return max(1, int(SCENARIO_HOLD_S.get(scenario, 5) * 1000))


def transport_mode(value: str) -> str:
    if value not in TRANSPORT:
        raise SystemExit(f"Unsupported SIP_TRANSPORT={value!r}")
    return TRANSPORT[value]


def resolve_local_ip(env: Mapping[str, str]) -> str:
    for key in ("SIP_EXTERNAL_IP", "SIP_CONTACT_HOST", "SIP_LOCAL_IP"):
        val = (env.get(key) or "").strip()
        if val:
            return val
    return "127.0.0.1"


def scenario_xml(root: Path, name: str) -> Path:
    spec = SCENARIOS.get(name)
    if not spec:
        raise SystemExit(f"Unknown scenario: {name}")
    return root / spec[0]


def is_uas(name: str) -> bool:
    spec = SCENARIOS.get(name)
    if not spec:
        raise SystemExit(f"Unknown scenario: {name}")
    return spec[1] == "uas"


def needs_media(name: str) -> bool:
    return name in MEDIA_SCENARIOS


def debug_enabled(env: Mapping[str, str], flag: bool | None = None) -> bool:
    if flag:
        return True
    v = (env.get("SIP_DEBUG") or "").strip().lower()
    return v in ("1", "true", "yes", "on")

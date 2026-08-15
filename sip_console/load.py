from __future__ import annotations

import re
from pathlib import Path

from sip_console.runner import run_sipp


def scalar(profile: str, key: str, default: str | None = None) -> str | None:
    m = re.search(rf"^\s*{re.escape(key)}:\s*(.+?)\s*$", profile, re.M)
    return m.group(1).strip().strip("\"'") if m else default


def parse_phases(profile: str) -> list[tuple[str, int, int, int, float | None]]:
    found = re.findall(
        r"- name:\s*([^\n]+)\n\s+cps:\s*(\d+)\n\s+max_concurrent:\s*(\d+)\n\s+calls:\s*(\d+)(?:\n\s+duration:\s*([0-9.]+))?",
        profile,
    )
    out: list[tuple[str, int, int, int, float | None]] = []
    for name, cps, conc, calls, dur in found:
        out.append(
            (
                name.strip(),
                int(cps),
                int(conc),
                int(calls),
                float(dur) if dur else None,
            )
        )
    return out


def run_load(root: Path, profile_path: Path, *, debug: bool | None = None) -> int:
    profile = Path(profile_path).read_text(encoding="utf-8")
    scenario = scalar(profile, "scenario", "uac-basic") or "uac-basic"
    cps = int(scalar(profile, "cps", "1") or "1")
    conc = int(scalar(profile, "max_concurrent", "1") or "1")
    calls = int(scalar(profile, "calls", "1") or "1")
    dur_raw = scalar(profile, "duration")
    duration_s = float(dur_raw) if dur_raw else None
    phases = parse_phases(profile)

    def run(name: str, rcps: int, rconc: int, rcalls: int, hold: float | None) -> int:
        return run_sipp(
            root,
            scenario,
            call_limit=rcalls,
            rate=rcps,
            max_concurrent=rconc,
            phase=f"load-{name}",
            duration_s=hold,
            debug=debug,
        )

    if phases:
        rc = 0
        for name, pcps, pconc, pcalls, pdur in phases:
            hold = pdur if pdur is not None else duration_s
            rc |= run(name, pcps, pconc, pcalls, hold)
        return rc
    return run("single", cps, conc, calls, duration_s)

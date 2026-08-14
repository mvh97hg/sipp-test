from __future__ import annotations

import re
from pathlib import Path

from sip_console.runner import run_sipp


def scalar(profile: str, key: str, default: str | None = None) -> str | None:
    m = re.search(rf"^\s*{re.escape(key)}:\s*(.+?)\s*$", profile, re.M)
    return m.group(1).strip().strip("\"'") if m else default


def parse_phases(profile: str) -> list[tuple[str, int, int, int]]:
    found = re.findall(
        r"- name:\s*([^\n]+)\n\s+cps:\s*(\d+)\n\s+max_concurrent:\s*(\d+)\n\s+calls:\s*(\d+)",
        profile,
    )
    return [(name.strip(), int(cps), int(conc), int(calls)) for name, cps, conc, calls in found]


def run_load(root: Path, profile_path: Path) -> int:
    profile = Path(profile_path).read_text(encoding="utf-8")
    scenario = scalar(profile, "scenario", "uac-basic") or "uac-basic"
    cps = int(scalar(profile, "cps", "1") or "1")
    conc = int(scalar(profile, "max_concurrent", "1") or "1")
    calls = int(scalar(profile, "calls", "1") or "1")
    phases = parse_phases(profile)

    def run(name: str, rcps: int, rconc: int, rcalls: int) -> int:
        return run_sipp(
            root,
            scenario,
            call_limit=rcalls,
            rate=rcps,
            max_concurrent=rconc,
            phase=f"load-{name}",
        )

    if phases:
        rc = 0
        for name, pcps, pconc, pcalls in phases:
            rc |= run(name, pcps, pconc, pcalls)
        return rc
    return run("single", cps, conc, calls)

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from sip_console.config import SCENARIOS
from sip_console.runner import run_sipp


def parse_regression_tests(text: str) -> list[tuple[str, str, bool]]:
    tests = []
    blocks = re.split(r"\n\s*-\s+name:\s*", text)[1:]
    for block in blocks:
        name = block.splitlines()[0].strip().strip("'\"")
        sm = re.search(r"^\s*scenario:\s*(.+)$", block, re.M)
        em = re.search(r"^\s*enabled:\s*(true|false)", block, re.M)
        if not sm:
            continue
        enabled = em.group(1) == "true" if em else True
        tests.append((name, sm.group(1).strip().strip("'\""), enabled))
    return tests


def run_regression(root: Path, profile_path: Path) -> int:
    text = Path(profile_path).read_text(encoding="utf-8")
    tests = parse_regression_tests(text)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    outroot = root / "artifacts" / f"{stamp}-regression"
    outroot.mkdir(parents=True, exist_ok=True)

    passed = failed = 0
    for name, scenario, enabled in tests:
        if not enabled:
            print(f"SKIP {name}")
            continue
        if scenario not in SCENARIOS:
            print(f"FAIL {name}: unknown scenario {scenario}")
            failed += 1
            continue
        rc = run_sipp(root, scenario, phase=name)
        if rc == 0:
            print(f"PASS {name}")
            passed += 1
        else:
            print(f"FAIL {name} exit={rc}")
            failed += 1

    summary = {"passed": passed, "failed": failed, "artifacts": str(outroot)}
    (outroot / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nPASS={passed} FAIL={failed}")
    print(f"Artifacts: {outroot}")
    return 1 if failed else 0

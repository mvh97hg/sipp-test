from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

SEGFAULT_CODES = {-11, 139, 245}


def last_sipp_stats(path: Path) -> dict[str, str] | None:
    path = Path(path)
    if not path.is_file():
        return None
    rows: list[dict[str, str]] = []
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=";")
        for row in reader:
            if row:
                rows.append(row)
    return rows[-1] if rows else None


def sipp_calls_passed(stats: dict[str, str] | None) -> bool:
    if not stats:
        return False
    try:
        created = int(stats.get("TotalCallCreated") or 0)
        current = int(stats.get("CurrentCall") or 0)
        ok = int(stats.get("SuccessfulCall(C)") or 0)
        failed = int(stats.get("FailedCall(C)") or 0)
    except ValueError:
        return False
    return created > 0 and current == 0 and failed == 0 and ok == created


def normalize_sipp_exit(rc: int, stats_path: Path) -> int:
    if rc == 0:
        return 0
    if rc not in SEGFAULT_CODES:
        return rc
    if sipp_calls_passed(last_sipp_stats(stats_path)):
        return 0
    return rc


def write_result(*, scenario: str, exit_code: int, out: Path) -> Path:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    obj = {
        "scenario": scenario,
        "exit_code": exit_code,
        "passed": exit_code == 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "artifacts": str(out.resolve()),
    }
    path = out / "result.json"
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    return path

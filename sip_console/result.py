from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


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

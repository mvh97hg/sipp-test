#!/usr/bin/env python3
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--scenario", required=True)
p.add_argument("--exit-code", type=int, required=True)
p.add_argument("--out", required=True)
a = p.parse_args()

out = Path(a.out)
out.mkdir(parents=True, exist_ok=True)
obj = {
    "scenario": a.scenario,
    "exit_code": a.exit_code,
    "passed": a.exit_code == 0,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "artifacts": str(out.resolve()),
}
(out / "result.json").write_text(json.dumps(obj, indent=2), encoding="utf-8")

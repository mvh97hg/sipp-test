#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
bash -n "$ROOT/scripts/run.sh"
python3 "$ROOT/tools/validate.py"
echo "OK: run.sh syntax and scenario validation passed"

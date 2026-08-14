#!/usr/bin/env bash
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROFILE="${1:-$ROOT/profiles/regression.yaml}"
python3 "$ROOT/tools/regression.py" "$PROFILE" "$ROOT"

#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROFILE="${1:?profile yaml required}"

python3 "$ROOT/tools/profile.py" "$PROFILE" "$ROOT"

#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
command -v sipp >/dev/null || { echo "ERROR: sipp not found"; exit 1; }
command -v python3 >/dev/null || { echo "ERROR: python3 not found"; exit 1; }
echo "SIPp:"
sipp -v | head -n 2
echo "Python:"
python3 --version
echo "Target: ${SIP_TARGET:-127.0.0.1:5060}"
echo "Service: ${SIP_SERVICE:-1000}"
echo "Scenario root: $ROOT/scenarios"

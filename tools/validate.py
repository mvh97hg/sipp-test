#!/usr/bin/env python3
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import re

root = Path(sys.argv[1])
failed = 0
count = 0

for path in sorted(root.rglob("*.xml")):
    count += 1
    try:
        text = path.read_text(encoding="utf-8")
        tree = ET.fromstring(text)
        if tree.tag != "scenario":
            raise ValueError(f"root element is {tree.tag!r}, expected 'scenario'")
        if not tree.get("name"):
            raise ValueError("missing scenario name")

        # RTD markers are intentionally forbidden in this release.
        # They are easy to leave unmatched across optional/error branches.
        if re.search(r'\b(?:start_rtd|stop_rtd)\s*=', text):
            raise ValueError(
                "start_rtd/stop_rtd is not allowed; use trace_rtt/stat collection"
            )

        # Basic keyword sanity.
        for token in re.findall(r'\[[A-Za-z0-9_]+\]', text):
            if token in ("[field0]", "[media_ip]", "[media_port]"):
                continue

        print(f"OK   {path}")
    except Exception as e:
        print(f"FAIL {path}: {e}")
        failed += 1

print(f"\nScenarios: {count}, failed: {failed}")
raise SystemExit(1 if failed else 0)

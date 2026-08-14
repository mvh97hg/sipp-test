from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from sip_console.config import SCENARIOS

AUTH_SNIPPET = "[authentication username=[field3] password=[field4]]"


def _contact_lines(text: str) -> list[str]:
    return [ln for ln in text.splitlines() if "Contact:" in ln]


def _local_tag(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _recv_has_auth(tree: ET.Element, code: str) -> bool:
    for el in tree.iter():
        if _local_tag(el.tag) != "recv":
            continue
        if el.get("response") == code and el.get("auth") == "true":
            return True
    return False


def validate_xml_text(text: str, *, uas: bool = False) -> None:
    tree = ET.fromstring(text)
    if tree.tag != "scenario":
        raise ValueError(f"root element is {tree.tag!r}, expected 'scenario'")
    if not tree.get("name"):
        raise ValueError("missing scenario name")

    # RTD markers are intentionally forbidden in this release.
    # They are easy to leave unmatched across optional/error branches.
    if re.search(r"\b(?:start_rtd|stop_rtd)\s*=", text):
        raise ValueError(
            "start_rtd/stop_rtd is not allowed; use trace_rtt/stat collection"
        )

    # Basic keyword sanity.
    for token in re.findall(r"\[[A-Za-z0-9_]+\]", text):
        if token in ("[field0]", "[media_ip]", "[media_port]"):
            continue

    if uas:
        contacts = _contact_lines(text)
        if not contacts:
            raise ValueError("Contact must contain @[field5]")
        for line in contacts:
            if "@[field5]" not in line:
                raise ValueError("Contact must contain @[field5]")
        return

    for code in ("401", "407"):
        if not _recv_has_auth(tree, code):
            raise ValueError(
                f'recv response="{code}" must also have auth="true" on the same element'
            )
    if AUTH_SNIPPET not in text:
        raise ValueError(
            "must contain [authentication username=[field3] password=[field4]]"
        )

    contacts = _contact_lines(text)
    if not contacts:
        raise ValueError("Contact must contain @[field5]")
    for line in contacts:
        if "@[field3]" in line:
            raise ValueError("Contact must not contain @[field3]")
        if "@[field5]" not in line:
            raise ValueError("Contact must contain @[field5]")


def _is_uas_path(path: Path, repo: Path) -> bool:
    resolved = path.resolve()
    for _name, (relpath, kind) in SCENARIOS.items():
        if (repo / relpath).resolve() == resolved:
            return kind == "uas"
    return "uas" in path.parts


def validate_scenarios(repo: Path) -> int:
    root = Path(repo)
    scenarios = root / "scenarios"
    failed = 0
    count = 0
    for path in sorted(scenarios.rglob("*.xml")):
        count += 1
        try:
            text = path.read_text(encoding="utf-8")
            validate_xml_text(text, uas=_is_uas_path(path, root))
            print(f"OK   {path}")
        except Exception as e:
            print(f"FAIL {path}: {e}")
            failed += 1
    print(f"\nScenarios: {count}, failed: {failed}")
    return 1 if failed else 0

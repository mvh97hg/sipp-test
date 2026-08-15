from __future__ import annotations

from pathlib import Path
from typing import MutableMapping


def parse_env_line(line: str) -> tuple[str, str] | None:
    raw = line.strip()
    if not raw or raw.startswith("#"):
        return None
    if raw.startswith("export "):
        raw = raw[7:].strip()
    if "=" not in raw or raw.startswith("="):
        return None
    key, value = raw.split("=", 1)
    key = key.strip()
    if not key or not key.replace("_", "").isalnum():
        return None
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    else:
        if " #" in value:
            value = value.split(" #", 1)[0].rstrip()
    return key, value


def load_env_file(
    path: Path,
    environ: MutableMapping[str, str] | None = None,
) -> list[str]:
    """Set keys from dotenv into environ. Existing keys are left unchanged."""
    import os

    env = os.environ if environ is None else environ
    path = Path(path)
    if not path.is_file():
        return []
    applied: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        parsed = parse_env_line(line)
        if parsed is None:
            continue
        key, value = parsed
        if key in env and env[key] != "":
            continue
        env[key] = value
        applied.append(key)
    return applied

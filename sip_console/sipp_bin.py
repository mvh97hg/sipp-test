from __future__ import annotations

import os
import shutil
import urllib.request
from pathlib import Path

SIPP_VERSION = "3.7.7"
SIPP_URL = f"https://github.com/SIPp/sipp/releases/download/v{SIPP_VERSION}/sipp"
MIN_SIPP_BYTES = 100_000


def _can_install(dest: Path) -> bool:
    parent = dest.parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        return False
    return os.access(parent, os.W_OK)


def install_paths(root: Path) -> list[Path]:
    return [Path(root) / "sipp", Path.home() / "sipp"]


def find_sipp(root: Path) -> Path | None:
    env = os.environ.get("SIP_SIPP", "").strip()
    candidates: list[Path] = []
    if env:
        candidates.append(Path(env).expanduser())
    which = shutil.which("sipp")
    if which:
        candidates.append(Path(which))
    candidates.extend(install_paths(root))
    seen: set[str] = set()
    for path in candidates:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        if path.is_file() and os.access(path, os.X_OK):
            return path
    return None


def download_sipp(dest: Path, url: str = SIPP_URL) -> Path:
    dest = Path(dest)
    tmp = dest.with_name(dest.name + ".tmp")
    try:
        with urllib.request.urlopen(url, timeout=120) as resp:
            data = resp.read()
    except OSError as exc:
        raise RuntimeError(f"failed to download SIPp from {url}: {exc}") from exc
    if len(data) < MIN_SIPP_BYTES or not data.startswith(b"\x7fELF"):
        raise RuntimeError(
            f"downloaded file is not a SIPp Linux binary ({len(data)} bytes)"
        )
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(data)
    tmp.chmod(0o755)
    tmp.replace(dest)
    return dest


def ensure_sipp(root: Path) -> Path:
    found = find_sipp(root)
    if found is not None:
        return found
    last_error: Exception | None = None
    for dest in install_paths(root):
        if not _can_install(dest):
            continue
        print(f"SIPp not found; downloading {SIPP_VERSION} to {dest}", flush=True)
        try:
            path = download_sipp(dest)
        except (OSError, RuntimeError) as exc:
            last_error = exc
            continue
        print(f"Installed SIPp: {path}", flush=True)
        return path
    detail = f" ({last_error})" if last_error else ""
    raise RuntimeError(
        "could not install SIPp to the project directory or home"
        f"{detail}. Download {SIPP_URL} yourself and set SIP_SIPP."
    )

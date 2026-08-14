#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path


def target_host(target: str) -> str:
    target = (target or "").strip()
    if target.startswith("["):
        end = target.find("]")
        if end >= 0:
            return target[1:end]
    if target.count(":") == 1:
        return target.rsplit(":", 1)[0]
    return target


def _pad(row: list[str], n: int = 5) -> list[str]:
    row = [x.strip() for x in row]
    if len(row) == 1 and ";" in row[0]:
        row = [x.strip() for x in row[0].split(";")]
    while len(row) < n:
        row.append("")
    return row[:n]


def normalize_rows(
    rows: list[list[str]],
    *,
    service: str = "",
    domain: str = "",
    target: str = "127.0.0.1:5060",
    auth_user: str = "",
    auth_pass: str = "",
) -> list[list[str]]:
    if not rows:
        raise SystemExit("empty injection CSV")
    mode = rows[0]
    data = rows[1:]
    domain_fallback = domain or target_host(target)
    out = [mode]
    for row in data:
        row = _pad(row)
        if not row[1]:
            row[1] = service
        if not row[2]:
            row[2] = domain_fallback
        if not row[3]:
            row[3] = auth_user
        if not row[4]:
            row[4] = auth_pass
        if not row[0]:
            raise SystemExit("field0/caller cannot be empty")
        if not row[1]:
            raise SystemExit("field1/service is empty and SIP_SERVICE fallback is not set")
        if not row[2]:
            raise SystemExit("field2/domain is empty and no SIP_DOMAIN/SIP_TARGET fallback exists")
        out.append(row)
    return out


def write_normalized_csv(
    input_path: Path,
    output_path: Path,
    *,
    service: str = "",
    domain: str = "",
    target: str = "127.0.0.1:5060",
    auth_user: str = "",
    auth_pass: str = "",
) -> Path:
    inp = Path(input_path)
    outp = Path(output_path)
    outp.parent.mkdir(parents=True, exist_ok=True)
    with inp.open(newline="", encoding="utf-8-sig") as fh:
        sample = fh.read(4096)
        fh.seek(0)
        reader = csv.reader(fh, delimiter=";") if ";" in sample else csv.reader(fh)
        rows = list(reader)
    normalized = normalize_rows(
        rows,
        service=service,
        domain=domain,
        target=target,
        auth_user=auth_user,
        auth_pass=auth_pass,
    )
    with outp.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        for row in normalized:
            w.writerow(row)
    return outp

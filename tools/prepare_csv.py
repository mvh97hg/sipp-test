#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path
from urllib.parse import urlsplit

def target_host(target: str) -> str:
    target = (target or "").strip()
    if target.startswith("["):
        end = target.find("]")
        if end >= 0:
            return target[1:end]
    if target.count(":") == 1:
        return target.rsplit(":", 1)[0]
    return target

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--service", default="")
    p.add_argument("--domain", default="")
    p.add_argument("--target", default="127.0.0.1:5060")
    p.add_argument("--contact-host", default="")
    args = p.parse_args()

    target_domain = target_host(args.target)
    domain_fallback = args.domain or target_domain
    contact_fallback = args.contact_host

    inp = Path(args.input)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    # SIPp injection files in this project use semicolon-separated data.
    # csv.reader defaults to comma, which would make "1000;2000;domain"
    # appear as one field and incorrectly trigger the field1 validation.
    with inp.open(newline="", encoding="utf-8-sig") as fh:
        sample = fh.read(4096)
        fh.seek(0)
        if ";" in sample:
            reader = csv.reader(fh, delimiter=";")
        else:
            reader = csv.reader(fh)
        rows = list(reader)
    if not rows:
        raise SystemExit("empty injection CSV")

    # SIPp injection files use a mode/header line such as SEQUENTIAL.
    mode = rows[0]
    data = rows[1:]

    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        w.writerow(mode)
        for row in data:
            row = [x.strip() for x in row]
            if len(row) == 1 and ";" in row[0]:
                row = [x.strip() for x in row[0].split(";")]
            while len(row) < 4:
                row.append("")
            if not row[1]:
                row[1] = args.service
            if not row[2]:
                row[2] = domain_fallback
            if not row[3]:
                row[3] = contact_fallback
            if not row[0]:
                raise SystemExit("field0/caller cannot be empty")
            if not row[1]:
                raise SystemExit("field1/service is empty and SIP_SERVICE fallback is not set")
            if not row[2]:
                raise SystemExit("field2/domain is empty and no SIP_DOMAIN/SIP_TARGET fallback exists")
            if not row[3]:
                # field3 is only used for Contact. Local IP is the safest default.
                row[3] = target_domain
            w.writerow(row)

if __name__ == "__main__":
    main()

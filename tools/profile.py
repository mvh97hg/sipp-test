#!/usr/bin/env python3
import re, subprocess, sys, datetime, os, shlex
from pathlib import Path

profile = Path(sys.argv[1]).read_text(encoding="utf-8")
root = Path(sys.argv[2])

def scalar(key, default=None):
    m = re.search(rf'^\s*{re.escape(key)}:\s*(.+?)\s*$', profile, re.M)
    return m.group(1).strip().strip('"\'') if m else default

scenario = scalar("scenario", "uac-basic")
cps = int(scalar("cps", "1"))
conc = int(scalar("max_concurrent", "1"))
calls = int(scalar("calls", "1"))

phases = re.findall(
    r'- name:\s*([^\n]+)\n\s+cps:\s*(\d+)\n\s+max_concurrent:\s*(\d+)\n\s+calls:\s*(\d+)',
    profile
)

def transport_arg():
    value = os.environ.get("SIP_TRANSPORT", "udp")
    mapping = {
        "udp": "u1", "udp-per-call": "un", "udp_multi": "un", "udp-multi": "un",
        "tcp": "t1", "tcp-per-call": "tn", "tcp_multi": "tn", "tcp-multi": "tn",
        "tls": "l1", "tls-per-call": "ln", "tls_multi": "ln", "tls-multi": "ln",
        "u1": "u1", "un": "un", "t1": "t1", "tn": "tn", "l1": "l1", "ln": "ln",
    }
    if value not in mapping:
        raise SystemExit(f"unsupported SIP_TRANSPORT={value!r}")
    return mapping[value]

def run(name, rcps, rconc, rcalls):
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    out = root / "artifacts" / f"{stamp}-load-{name}"
    out.mkdir(parents=True, exist_ok=True)

    target = os.environ.get("SIP_TARGET", "127.0.0.1:5060")
    service = os.environ.get("SIP_SERVICE", "")
    domain = os.environ.get("SIP_DOMAIN", "")
    local_ip = os.environ.get("SIP_LOCAL_IP", "")
    contact_host = os.environ.get("SIP_CONTACT_HOST", local_ip)
    csv_run = out / "users.normalized.csv"
    subprocess.run([
        sys.executable, str(root/"tools/prepare_csv.py"),
        "--input", str(csv_run),
        "--output", str(csv_run),
        "--service", service,
        "--domain", domain,
        "--target", target,
        "--contact-host", contact_host,
    ], check=True)
    media_ip = os.environ.get("SIP_MEDIA_IP", local_ip)
    media_port = os.environ.get("SIP_MEDIA_PORT", "6000")

    scmap = {
        "uac-basic": root/"scenarios/uac/uac-basic.xml",
        "dtmf": root/"scenarios/features/dtmf.xml",
        "rtp-echo": root/"scenarios/media/rtp-echo.xml",
    }
    sc = scmap.get(scenario)
    if not sc:
        raise SystemExit(f"unsupported load scenario: {scenario}")

    cmd = [
        "sipp", target,
        "-sf", str(sc),
        "-s", service,
        "-t", transport_arg(),
        "-r", str(rcps),
        "-l", str(rconc),
        "-m", str(rcalls),
        "-inf", str(csv_run),
        "-trace_msg", "-trace_err", "-trace_stat", "-trace_rtt",
        "-trace_shortmsg", "-trace_calldebug",
        "-message_file", str(out/"messages.log"),
        "-error_file", str(out/"errors.log"),
    ]

    if local_ip:
        cmd += ["-i", local_ip]
    if scenario in ("uac-basic", "dtmf", "rtp-echo"):
        if media_ip:
            cmd += ["-mi", media_ip]
        cmd += ["-mp", media_port]
    if scenario == "rtp-echo":
        cmd += ["-rtp_echo"]

    (out/"command.txt").write_text(" ".join(shlex.quote(x) for x in cmd), encoding="utf-8")
    print("RUN:", " ".join(shlex.quote(x) for x in cmd))
    with open(out/"stdout.log", "w") as so, open(out/"stderr.log", "w") as se:
        p = subprocess.run(cmd, stdout=so, stderr=se)

    # Always create a normalized result.
    result = {
        "scenario": scenario,
        "phase": name,
        "cps": rcps,
        "max_concurrent": rconc,
        "calls": rcalls,
        "exit_code": p.returncode,
        "passed": p.returncode == 0,
        "artifacts": str(out.resolve()),
    }
    import json
    (out/"result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return p.returncode

if phases:
    rc = 0
    for name, pcps, pconc, pcalls in phases:
        rc |= run(name.strip(), int(pcps), int(pconc), int(pcalls))
    raise SystemExit(rc)
else:
    raise SystemExit(run("single", cps, conc, calls))

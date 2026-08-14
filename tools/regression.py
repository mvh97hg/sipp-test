#!/usr/bin/env python3
import re, subprocess, sys, datetime, os
from pathlib import Path

profile_path = Path(sys.argv[1])
root = Path(sys.argv[2])
text = profile_path.read_text()

# Simple dependency-free YAML subset parser for the package format.
tests = []
blocks = re.split(r'\n\s*-\s+name:\s*', text)[1:]
for block in blocks:
    name = block.splitlines()[0].strip().strip("'\"")
    sm = re.search(r'^\s*scenario:\s*(.+)$', block, re.M)
    em = re.search(r'^\s*enabled:\s*(true|false)', block, re.M)
    if not sm:
        continue
    enabled = em.group(1) == "true" if em else True
    tests.append((name, sm.group(1).strip().strip("'\""), enabled))

target = os.environ.get("SIP_TARGET", "127.0.0.1:5060")
service = os.environ.get("SIP_SERVICE", "")
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
outroot = root/"artifacts"/f"{stamp}-regression"
outroot.mkdir(parents=True, exist_ok=True)

mapping = {
    "uac-basic": root/"scenarios/uac/uac-basic.xml",
    "uas-answer": root/"scenarios/uas/uas-answer.xml",
    "dtmf": root/"scenarios/features/dtmf.xml",
    "rtp-echo": root/"scenarios/media/rtp-echo.xml",
    "uac-busy": root/"scenarios/negative/uac-busy.xml",
    "uac-notfound": root/"scenarios/negative/uac-notfound.xml",
    "uac-service-unavailable": root/"scenarios/negative/uac-service-unavailable.xml",
}

passed = failed = 0
for name, scenario, enabled in tests:
    if not enabled:
        print(f"SKIP {name}")
        continue
    sc = mapping.get(scenario)
    if not sc:
        print(f"FAIL {name}: unknown scenario {scenario}")
        failed += 1
        continue
    out = outroot/name
    out.mkdir(parents=True, exist_ok=True)
    csv_run = out / "users.normalized.csv"
    prep = [
        sys.executable, str(root/"tools/prepare_csv.py"),
        "--input", str(csv_run),
        "--output", str(csv_run),
        "--service", service,
        "--domain", os.environ.get("SIP_DOMAIN", ""),
        "--target", target,
        "--contact-host", os.environ.get("SIP_CONTACT_HOST", os.environ.get("SIP_LOCAL_IP", "")),
    ]
    subprocess.run(prep, check=True)
    transport = os.environ.get("SIP_TRANSPORT", "udp")
    tmap = {"udp":"u1", "udp-per-call":"un", "udp_multi":"un", "udp-multi":"un",
            "tcp":"t1", "tcp-per-call":"tn", "tcp_multi":"tn", "tcp-multi":"tn",
            "tls":"l1", "tls-per-call":"ln", "tls_multi":"ln", "tls-multi":"ln",
            "u1":"u1", "un":"un", "t1":"t1", "tn":"tn", "l1":"l1", "ln":"ln"}
    if transport not in tmap:
        print(f"FAIL {name}: unsupported SIP_TRANSPORT={transport}")
        failed += 1
        continue

    cmd = ["sipp", target, "-sf", str(sc), "-s", service,
           "-t", tmap[transport], "-m", "1", "-inf", str(csv_run),
           "-trace_msg", "-trace_err", "-trace_stat", "-trace_rtt",
           "-trace_shortmsg", "-trace_calldebug",
           "-message_file", str(out/"messages.log"),
           "-error_file", str(out/"errors.log")]

    local_ip = os.environ.get("SIP_LOCAL_IP", "")
    media_ip = os.environ.get("SIP_MEDIA_IP", local_ip)
    if local_ip:
        cmd += ["-i", local_ip]
    if scenario in ("uac-basic", "dtmf", "rtp-echo", "uas-answer"):
        if media_ip:
            cmd += ["-mi", media_ip]
        cmd += ["-mp", os.environ.get("SIP_MEDIA_PORT", "6000")]
    if scenario == "rtp-echo":
        cmd += ["-rtp_echo"]
    (out/"command.txt").write_text(" ".join(cmd), encoding="utf-8")
    with open(out/"stdout.log","w") as so, open(out/"stderr.log","w") as se:
        rc = subprocess.run(cmd, stdout=so, stderr=se).returncode
    if rc == 0:
        print(f"PASS {name}")
        passed += 1
    else:
        print(f"FAIL {name} exit={rc}")
        failed += 1

summary = {"passed": passed, "failed": failed, "artifacts": str(outroot)}
(outroot/"summary.json").write_text(__import__("json").dumps(summary, indent=2))
print(f"\nPASS={passed} FAIL={failed}")
print(f"Artifacts: {outroot}")
raise SystemExit(1 if failed else 0)

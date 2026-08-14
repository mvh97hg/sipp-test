from __future__ import annotations

import os
import shlex
import subprocess
from datetime import datetime
from pathlib import Path

from sip_console.config import is_uas
from sip_console.csv_inject import write_normalized_csv
from sip_console.net import resolve_bind_advertise
from sip_console.result import write_result
from sip_console.sipp_cmd import build_sipp_cmd


def run_sipp(
    root: Path,
    scenario: str,
    extra: list[str] | None = None,
    *,
    call_limit: int = 1,
    rate: int | None = None,
    max_concurrent: int | None = None,
    phase: str | None = None,
    local_port: str | None = None,
    artifact_dir: Path | None = None,
) -> int:
    env = os.environ
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = artifact_dir if artifact_dir is not None else (
        root / "logs" / f"{stamp}-{phase or scenario}"
    )
    out.mkdir(parents=True, exist_ok=True)
    csv_run = out / "users.normalized.csv"
    target = env.get("SIP_TARGET", "127.0.0.1:5060")
    bind_ip, advertise_ip = resolve_bind_advertise(env, target)
    print(f"NAT: bind={bind_ip} advertise={advertise_ip}", flush=True)
    if not is_uas(scenario) and (root / "data/users.csv").is_file():
        write_normalized_csv(
            root / "data/users.csv",
            csv_run,
            service=env.get("SIP_SERVICE", ""),
            domain=env.get("SIP_DOMAIN", ""),
            target=target,
            auth_user=env.get("SIP_AUTH_USER", ""),
            auth_pass=env.get("SIP_AUTH_PASS", ""),
            advertise_ip=advertise_ip,
        )
    elif is_uas(scenario):
        csv_run.write_text(f"SEQUENTIAL\nuas;;;;;{advertise_ip}\n", encoding="utf-8")
    else:
        csv_run = None
    port = local_port if local_port is not None else env.get("SIP_LOCAL_PORT", "")
    cmd = build_sipp_cmd(
        root=root,
        scenario=scenario,
        target=target,
        service=env.get("SIP_SERVICE", ""),
        transport=env.get("SIP_TRANSPORT", "udp"),
        local_ip=bind_ip,
        local_port=port,
        media_ip=env.get("SIP_MEDIA_IP", "") or advertise_ip,
        media_port=env.get("SIP_MEDIA_PORT", "6000"),
        csv_path=csv_run,
        artifact_dir=out,
        call_limit=call_limit,
        rate=rate,
        max_concurrent=max_concurrent,
        extra=extra,
    )
    (out / "command.txt").write_text(shlex.join(cmd) + "\n", encoding="utf-8")
    with open(out / "stdout.log", "w") as so, open(out / "stderr.log", "w") as se:
        rc = subprocess.run(cmd, stdout=so, stderr=se, cwd=out).returncode
    write_result(scenario=scenario, exit_code=rc, out=out)
    print(f"Artifacts: {out}")
    return rc

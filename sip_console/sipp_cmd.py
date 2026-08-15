from __future__ import annotations

from pathlib import Path

from sip_console.config import is_uas, needs_media, scenario_xml, transport_mode


def build_sipp_cmd(
    *,
    root: Path,
    scenario: str,
    target: str,
    service: str,
    transport: str,
    local_ip: str,
    local_port: str,
    media_ip: str,
    media_port: str,
    csv_path: Path | None,
    artifact_dir: Path,
    call_limit: int = 1,
    rate: int | None = None,
    max_concurrent: int | None = None,
    extra: list[str] | None = None,
    hold_ms: int = 5000,
    debug: bool = False,
    sipp_bin: str = "sipp",
) -> list[str]:
    xml = str(scenario_xml(root, scenario))
    mode = transport_mode(transport)
    cmd = [sipp_bin]
    uas = is_uas(scenario)
    if not uas:
        cmd.append(target)
    cmd += ["-sf", xml]
    if uas:
        cmd += ["-p", local_port or "5060"]
    cmd += ["-t", mode]
    if not uas:
        if service:
            cmd += ["-s", service]
        if local_port:
            cmd += ["-p", local_port]
    if csv_path is not None:
        cmd += ["-inf", str(csv_path)]
    cmd += ["-m", str(call_limit)]
    if rate is not None:
        cmd += ["-r", str(rate)]
    if max_concurrent is not None:
        cmd += ["-l", str(max_concurrent)]
    if local_ip:
        cmd += ["-i", local_ip]
    if needs_media(scenario):
        if media_ip:
            cmd += ["-mi", media_ip]
        if media_port:
            cmd += ["-mp", media_port]
    if scenario == "rtp-echo":
        cmd += ["-rtp_echo"]
    cmd += ["-recv_timeout", str(max(1, int(hold_ms)))]
    cmd += ["-d", str(max(1, int(hold_ms)))]
    cmd += [
        "-aa",
        "-default_behaviors",
        "all,-abortunexp",
        "-trace_err",
        "-trace_stat",
        "-trace_rtt",
        "-trace_shortmsg",
        "-error_file",
        str(Path(artifact_dir) / "errors.log"),
        "-stf",
        str(Path(artifact_dir) / "statistics.csv"),
        "-shortmessage_file",
        str(Path(artifact_dir) / "shortmessages.log"),
    ]
    if debug:
        cmd += [
            "-trace_calldebug",
            "-calldebug_file",
            str(Path(artifact_dir) / "calldebug.log"),
        ]
    if extra:
        cmd += extra
    return cmd

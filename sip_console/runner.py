from __future__ import annotations

import fcntl
import os
import select
import shlex
import signal
import struct
import subprocess
import sys
import termios
import threading
import tty
from datetime import datetime
from pathlib import Path
from typing import IO

from sip_console.config import debug_enabled, hold_ms, is_uas
from sip_console.csv_inject import write_normalized_csv
from sip_console.net import resolve_bind_advertise
from sip_console.result import normalize_sipp_exit, write_result
from sip_console.sipp_bin import ensure_sipp
from sip_console.sipp_cmd import build_sipp_cmd
from sip_console.termlog import TermLog

INTERRUPT_EXIT = 130


def _write_console(stream, chunk: bytes) -> None:
    raw = getattr(stream, "buffer", None)
    if raw is not None:
        raw.write(chunk)
        raw.flush()
        return
    stream.write(chunk.decode("utf-8", "replace"))
    stream.flush()


def _tee_bytes(src: IO[bytes], log: IO[bytes], console) -> None:
    try:
        while True:
            chunk = src.read(4096)
            if not chunk:
                break
            log.write(chunk)
            log.flush()
            _write_console(console, chunk)
    except (ValueError, OSError):
        pass


def tty_available() -> bool:
    try:
        return bool(sys.stdin.isatty() and sys.stdout.isatty())
    except (AttributeError, ValueError, OSError):
        return False


def _copy_winsize(src_fd: int, dst_fd: int) -> None:
    packed = fcntl.ioctl(src_fd, termios.TIOCGWINSZ, struct.pack("HHHH", 0, 0, 0, 0))
    fcntl.ioctl(dst_fd, termios.TIOCSWINSZ, packed)


def _tty_size(fd: int) -> tuple[int, int]:
    try:
        rows, cols, _, _ = struct.unpack(
            "HHHH",
            fcntl.ioctl(fd, termios.TIOCGWINSZ, struct.pack("HHHH", 0, 0, 0, 0)),
        )
        return (rows or 24, cols or 80)
    except OSError:
        return 24, 80


def _drain_master(master_fd: int, stdout_fd: int, log: IO[bytes]) -> None:
    while True:
        readable, _, _ = select.select([master_fd], [], [], 0)
        if master_fd not in readable:
            break
        try:
            data = os.read(master_fd, 8192)
        except OSError:
            break
        if not data:
            break
        os.write(stdout_fd, data)
        log.write(data)


def attach_tty(
    pid: int,
    master_fd: int,
    log: IO[bytes],
    *,
    stdin_fd: int | None = None,
    stdout_fd: int | None = None,
    make_raw: bool | None = None,
) -> int:
    if stdin_fd is None:
        stdin_fd = sys.stdin.fileno()
    if stdout_fd is None:
        stdout_fd = sys.stdout.fileno()
    if make_raw is None:
        make_raw = os.isatty(stdin_fd)
    old_term = None
    if make_raw:
        old_term = termios.tcgetattr(stdin_fd)
        tty.setraw(stdin_fd)

    def on_winch(_signum=None, _frame=None) -> None:
        try:
            _copy_winsize(stdout_fd, master_fd)
        except OSError:
            pass

    prev_winch = signal.getsignal(signal.SIGWINCH)
    signal.signal(signal.SIGWINCH, on_winch)
    rows, cols = _tty_size(stdout_fd)
    term = TermLog(log, rows=rows, cols=cols)
    status = None
    try:
        on_winch()
        while True:
            try:
                readable, _, _ = select.select([master_fd, stdin_fd], [], [], 0.25)
            except InterruptedError:
                continue
            if stdin_fd in readable:
                try:
                    data = os.read(stdin_fd, 1024)
                except OSError:
                    data = b""
                if data:
                    try:
                        os.write(master_fd, data)
                    except OSError:
                        break
            if master_fd in readable:
                try:
                    data = os.read(master_fd, 8192)
                except OSError:
                    data = b""
                if not data:
                    break
                os.write(stdout_fd, data)
                term.write(data)
            waited_pid, waited_status = os.waitpid(pid, os.WNOHANG)
            if waited_pid == pid:
                status = waited_status
                _drain_master(master_fd, stdout_fd, term)
                break
        if status is None:
            _waited_pid, status = os.waitpid(pid, 0)
        return os.waitstatus_to_exitcode(status)
    finally:
        term.flush()
        signal.signal(signal.SIGWINCH, prev_winch)
        if old_term is not None:
            termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_term)
        try:
            os.close(master_fd)
        except OSError:
            pass


def run_sipp_on_tty(cmd: list[str], cwd: Path, stdout_path: Path, stderr_path: Path) -> int:
    Path(stderr_path).write_bytes(b"")
    pid, master_fd = os.forkpty()
    if pid == 0:
        try:
            os.chdir(cwd)
            os.execvp(cmd[0], cmd)
        except OSError:
            os._exit(127)
    with open(stdout_path, "wb") as log:
        return attach_tty(pid, master_fd, log)


def run_sipp_child(cmd: list[str], cwd: Path, stdout_path: Path, stderr_path: Path) -> int:
    if tty_available():
        print(
            "SIPp TTY attached — keys go to SIPp (q quit, 1-4 screens, +/- rate).",
            flush=True,
        )
        return run_sipp_on_tty(cmd, cwd, stdout_path, stderr_path)
    print("SIPp running (live output, no TTY)...", flush=True)
    proc, workers, logs = spawn_sipp(cmd, cwd, stdout_path, stderr_path)
    try:
        return wait_sipp(proc)
    finally:
        finish_tee(proc, workers, logs)


def spawn_sipp(
    cmd: list[str],
    cwd: Path,
    stdout_path: Path,
    stderr_path: Path,
) -> tuple[subprocess.Popen[bytes], list[threading.Thread], list[IO[bytes]]]:
    so = TermLog(open(stdout_path, "wb"))
    se = open(stderr_path, "wb")
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        bufsize=0,
    )
    workers = [
        threading.Thread(
            target=_tee_bytes,
            args=(proc.stdout, so, sys.stdout),
            daemon=True,
        ),
        threading.Thread(
            target=_tee_bytes,
            args=(proc.stderr, se, sys.stderr),
            daemon=True,
        ),
    ]
    for worker in workers:
        worker.start()
    return proc, workers, [so, se]


def finish_tee(
    proc: subprocess.Popen[bytes],
    workers: list[threading.Thread],
    files: list[IO[bytes]],
) -> None:
    for worker in workers:
        worker.join(timeout=5)
    for stream in (proc.stdout, proc.stderr):
        if stream is not None:
            stream.close()
    for fh in files:
        fh.close()


def wait_sipp(proc: subprocess.Popen[bytes]) -> int:
    try:
        return int(proc.wait())
    except KeyboardInterrupt:
        print("Stopped.", flush=True)
        if proc.poll() is None:
            proc.send_signal(signal.SIGINT)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
        return INTERRUPT_EXIT


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
    duration_s: float | None = None,
    debug: bool | None = None,
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
    hold = hold_ms(env, scenario, duration_s)
    dbg = debug_enabled(env, debug)
    print(f"Duration: {hold}ms", flush=True)
    try:
        sipp_bin = str(ensure_sipp(root))
    except RuntimeError as exc:
        print(f"ERROR: {exc}", flush=True)
        return 1
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
        hold_ms=hold,
        debug=dbg,
        sipp_bin=sipp_bin,
    )
    (out / "command.txt").write_text(shlex.join(cmd) + "\n", encoding="utf-8")
    rc = run_sipp_child(cmd, out, out / "stdout.log", out / "stderr.log")
    raw = rc
    rc = normalize_sipp_exit(rc, out / "statistics.csv")
    if raw != 0 and rc == 0:
        print("SIPp crashed after all calls passed; reporting success.", flush=True)
    write_result(scenario=scenario, exit_code=rc, out=out)
    print(f"Artifacts: {out}")
    return rc

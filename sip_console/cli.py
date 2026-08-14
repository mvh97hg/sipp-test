from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from sip_console.config import SCENARIOS
from sip_console.load import run_load
from sip_console.regression import run_regression
from sip_console.runner import run_sipp
from sip_console.validate import validate_scenarios


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def cmd_check(root: Path) -> int:
    if not shutil.which("sipp"):
        print("ERROR: sipp not found")
        return 1
    if not shutil.which("python3"):
        print("ERROR: python3 not found")
        return 1
    print("SIPp:")
    proc = subprocess.run(["sipp", "-v"], capture_output=True, text=True)
    version_text = proc.stdout or proc.stderr
    print("\n".join(version_text.splitlines()[:2]))
    print("Python:")
    py = subprocess.run(["python3", "--version"], capture_output=True, text=True)
    print((py.stdout or py.stderr).strip())
    print(f"Target: {os.environ.get('SIP_TARGET', '127.0.0.1:5060')}")
    print(f"Service: {os.environ.get('SIP_SERVICE', '1000')}")
    print(f"Scenario root: {root / 'scenarios'}")
    return 0


def cmd_list(root: Path) -> int:
    for path in sorted((root / "scenarios").rglob("*.xml")):
        print(path)
    return 0


def cmd_validate(root: Path) -> int:
    return validate_scenarios(root)


def cmd_run(root: Path, scenario: str | None, listen: str | None, extra: list[str]) -> int:
    if not scenario:
        print("usage: python3 -m sip_console run <scenario>", file=sys.stderr)
        return 2
    if scenario not in SCENARIOS:
        print(f"Unknown scenario: {scenario}", file=sys.stderr)
        return 2
    extra_args = extra
    if extra_args and extra_args[0] == "--":
        extra_args = extra_args[1:]
    return run_sipp(root, scenario, extra_args or None, local_port=listen)


def main(argv: list[str] | None = None) -> int:
    root = repo_root()
    p = argparse.ArgumentParser(prog="python3 -m sip_console")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("check")
    sub.add_parser("list")
    sub.add_parser("validate")

    run_p = sub.add_parser("run")
    run_p.add_argument("scenario", nargs="?")
    run_p.add_argument("--listen")

    load_p = sub.add_parser("load")
    load_p.add_argument("profile")

    reg_p = sub.add_parser("regression")
    reg_p.add_argument("profile", nargs="?", default=str(root / "profiles/regression.yaml"))

    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["run"]:
        args, extra = p.parse_known_args(argv)
        return cmd_run(root, args.scenario, args.listen, extra)
    args = p.parse_args(argv)
    if args.cmd == "check":
        return cmd_check(root)
    if args.cmd == "list":
        return cmd_list(root)
    if args.cmd == "validate":
        return cmd_validate(root)
    if args.cmd == "load":
        return run_load(root, Path(args.profile))
    if args.cmd == "regression":
        return run_regression(root, Path(args.profile))
    p.print_help()
    return 2

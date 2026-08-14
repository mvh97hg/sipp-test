#!/usr/bin/env python3
import os
import sys

def target_host(target: str) -> str:
    target = target.strip()
    if target.startswith("["):
        end = target.find("]")
        return target[1:end] if end >= 0 else target
    if target.count(":") == 1:
        return target.rsplit(":", 1)[0]
    return target

def resolve_domain(field2=None, env=None):
    env = env or os.environ
    if field2:
        return field2
    if env.get("SIP_DOMAIN"):
        return env["SIP_DOMAIN"]
    return target_host(env.get("SIP_TARGET", "127.0.0.1"))

if __name__ == "__main__":
    print(resolve_domain(sys.argv[1] if len(sys.argv) > 1 else ""))

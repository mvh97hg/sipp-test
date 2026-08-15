# Load and ramp

Start small. Load can knock over a production PBX or carrier.

```bash
python3 -m sip_console load profiles/load-10cps.yaml
python3 -m sip_console load profiles/load-100cps.yaml
python3 -m sip_console load profiles/ramp.yaml
```

Profile shape:

```yaml
name: basic-10cps
scenario: uac-basic
cps: 10
max_concurrent: 50
calls: 100
duration: 10
```

Ramp (`profiles/ramp.yaml`) is a list of phases (`name`, `cps`, `max_concurrent`, `calls`, optional `duration`). Each phase gets its own `logs/` directory.

Suggested CPS steps: 1 → 10 → 25 → 50 → 100 → 250 → 500. At each step record answer/fail rate, retransmits, SIPp statistics, RTP loss/jitter if you capture it, and PBX CPU/memory.

Regression:

```bash
python3 -m sip_console regression profiles/regression.yaml
```

A case passes on SIPp exit 0 (including the “segfault after all calls OK” remap). See [scenarios.md](scenarios.md) for which tests are enabled by default.

# SIP Test Console

Python CLI around **SIPp** for SIP/voice tests. This repo does not implement a SIP stack.

```bash
cp .env.example .env          # edit SIP_TARGET, auth, …
python3 -m sip_console check  # installs SIPp 3.7.7 to ./sipp or ~/sipp if missing
make basic                    # one outbound INVITE
```

Linux + `python3`. No extra Python packages. Load tests can overload a live PBX — use a test trunk.

## Commands

| Make | CLI | Purpose |
|---|---|---|
| `make check` | `python3 -m sip_console check` | SIPp, Python, target |
| `make list` | `… list` | scenario XML files |
| `make validate` | `… validate` | XML rules |
| `make basic` | `… run uac-basic` | outbound call |
| `make uas` | `… run uas-answer --listen 5060` | inbound answer |
| `make load` | `… load profiles/load-10cps.yaml` | CPS load |
| `make regression` | `… regression profiles/regression.yaml` | enabled suite |

`python3 -m sip_console run <scenario> [--duration SEC] [--debug]`

Artifacts: `logs/<timestamp>-<name>/` (`result.json`, `statistics.csv`, `stdout.log`). Debug: `--debug` or `SIP_DEBUG=1`.

## Docs

| Doc | Contents |
|---|---|
| [docs/usage.md](docs/usage.md) | `.env`, duration, UAS, TLS, artifacts |
| [docs/scenarios.md](docs/scenarios.md) | Scenario matrix (REGISTER, DTMF, hold, …) |
| [docs/csv-fields.md](docs/csv-fields.md) | CSV columns, NAT/STUN, auth |
| [docs/load.md](docs/load.md) | Load/ramp profiles, how to scale CPS |
| [docs/architecture.md](docs/architecture.md) | Address resolution examples |
| [docs/changelog.md](docs/changelog.md) | Version history |
| [examples/cdr-correlation.md](examples/cdr-correlation.md) | CDR correlation |

Shell equivalent of `.env`: [examples/env.sh](examples/env.sh).

# Usage

## Setup

```bash
cp .env.example .env
python3 -m sip_console check
```

`check` uses SIPp from `SIP_SIPP`, then `./sipp`, then `~/sipp`, then `PATH`. If none exist it downloads [SIPp 3.7.7](https://github.com/SIPp/sipp/releases/download/v3.7.7/sipp) into the repo or home (not `/usr/local/bin`).

The CLI loads `.env` on every command. Shell variables already set are not overwritten. `SIP_ENV_FILE` can point to another file.

```bash
SIP_TARGET=10.10.0.10:5060
SIP_SERVICE=1000
SIP_AUTH_USER=1234
SIP_AUTH_PASS=secret
SIP_CALL_DURATION=30
```

One-off: `export SIP_TARGET=…` then run the CLI. Full variable list: `.env.example`. CSV/NAT mapping: [csv-fields.md](csv-fields.md).

`SIP_TRANSPORT` is `udp` (default), `tcp`, or `tls`. TLS needs `SIP_TLS_CERT` (and usually `SIP_TLS_KEY` / `SIP_TLS_CA`).

## Outbound call

```bash
python3 -m sip_console run uac-basic
python3 -m sip_console run uac-basic --duration 30
```

Hold after ACK (first match): `--duration` (seconds) → `SIP_CALL_DURATION` → `SIP_HOLD_MS` → scenario default (basic/auth/dtmf 5s, rtp-echo/UAS 10s). Peer BYE during hold is answered with 200.

Load YAML may set `duration:` on the profile or a phase.

## Inbound UAS

```bash
python3 -m sip_console run uas-answer --listen 5060
```

Originate from the PBX toward this host. If the peer never sends BYE, the UAS sends BYE after the hold timeout.

## Debug and logs

```text
logs/YYYYMMDD-HHMMSS-<name>/
  command.txt
  stdout.log          # SIPp screen, ANSI stripped
  stderr.log
  errors.log
  statistics.csv
  shortmessages.log
  result.json
  calldebug.log       # --debug or SIP_DEBUG=1
  users.normalized.csv
```

`result.json`: `scenario`, `exit_code`, `passed`, `created_at`, `artifacts`. SIPp segfault after all calls succeed is reported as pass.

Do not share `users.normalized.csv` — it can contain digest passwords.

## Validation

```bash
python3 -m sip_console validate
```

Fails on missing Contact `@[field5]`, unpaired 401/407 `auth="true"`, in-dialog BYE without `[next_url]`, or `start_rtd`/`stop_rtd`.

# Changelog

## 1.1.0

Breaking: CSV `[field3]` / `[field4]` are auth username and password
(`SIP_AUTH_USER` / `SIP_AUTH_PASS`). Contact host is no longer a CSV column;
the runner sets SIPp `[contact_host]` from
`SIP_EXTERNAL_IP` → `SIP_CONTACT_HOST` → `SIP_LOCAL_IP` → `127.0.0.1`.

- Control plane is `python3 -m sip_console`. Bash is not a required runtime.
- Required tools: `python3` and `sipp`.
- Optional 401/407 then authenticated re-INVITE on UAC scenarios.
- Shared SIPp argv builder; UAS listen mode; regression/load CSV injection.

## 1.0.8

- Fixed semicolon-separated `users.csv` parsing.
- Added a regression test for `field0;field1;field2`.
- `run.sh` no longer passes an empty `-s` argument when `SIP_SERVICE` is unset.

## 1.0.7

- Fixed `MODE` initialization under `set -u`.

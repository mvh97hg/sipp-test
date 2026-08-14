# Changelog

## 1.0.8

- Fixed semicolon-separated `users.csv` parsing.
- Added a regression test for `field0;field1;field2`.
- `run.sh` no longer passes an empty `-s` argument when `SIP_SERVICE` is unset.

## 1.0.7

- Fixed `MODE` initialization under `set -u`.

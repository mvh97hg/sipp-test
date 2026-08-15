# Address resolution examples

```bash
export SIP_TARGET=10.10.0.10:5060
export SIP_DOMAIN=pbx.example.com
export SIP_AUTH_USER=1234
export SIP_AUTH_PASS=secret
export SIP_EXTERNAL_IP=123.24.143.114
```

CSV (`SEQUENTIAL` + three columns; auth from env):

```text
1000;2000;tenant-a.example.com
```

becomes caller `1000`, Request-URI `sip:2000@tenant-a.example.com`. If the row is only `1000;2000`, domain is `SIP_DOMAIN` (`pbx.example.com`), else the host of `SIP_TARGET`.

Via uses bind IP (`-i`). Contact/SDP use `[field5]` / `-mi` as in [csv-fields.md](csv-fields.md).

The CLI builds SIPp argv, normalizes CSV, and writes `logs/`. SIPp owns SIP and RTP. Scenarios must not use `start_rtd` / `stop_rtd` (unbalanced on optional branches); use `-trace_rtt` / `-trace_stat` instead.

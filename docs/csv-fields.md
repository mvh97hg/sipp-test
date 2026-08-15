# CSV fields and NAT

```text
[field0] = caller
[field1] = destination / service     → SIP_SERVICE
[field2] = SIP domain                → SIP_DOMAIN → host(SIP_TARGET)
[field3] = auth username             → SIP_AUTH_USER
[field4] = auth password             → SIP_AUTH_PASS
[field5] = advertised Contact/SDP host (filled by the runner)
```

`data/users.csv` stays `SEQUENTIAL` plus three-column rows. Auth is filled from the environment when field3/field4 are empty. Do not commit real passwords.

`SIP_TARGET` is the network destination. It is only the last fallback for the SIP domain.

## NAT

```text
bind (-i / Via [local_ip])  = SIP_LOCAL_IP → UDP connect toward SIP_TARGET
advertise ([field5], -mi)   = SIP_EXTERNAL_IP → SIP_CONTACT_HOST
                              → STUN if SIP_TARGET is a public IP
                              → bind IP (private/LAN targets skip STUN)
```

`SIP_STUN=0` disables STUN. `SIP_STUN_SERVER` defaults to `stun.l.google.com:19302`.

In-dialog ACK/BYE/INFO use `[next_url]` and `[routes]` from the dialog 200 (`rrs="true"`).

## Other env

| Variable | Role |
|---|---|
| `SIP_TRANSPORT` | `udp` / `tcp` / `tls` → SIPp `u1` / `t1` / `l1` |
| `SIP_REFER_TO` | Refer-To URI for `uac-refer` |
| `SIP_TLS_CERT` / `SIP_TLS_KEY` / `SIP_TLS_CA` | required for `tls` |
| `SIP_SIPP` | pin SIPp binary |

Worked CSV examples: [architecture.md](architecture.md).

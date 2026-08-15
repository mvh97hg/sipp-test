# CSV fields

```text
[field0] = caller
[field1] = destination / service     → SIP_SERVICE
[field2] = SIP domain                → SIP_DOMAIN → host(SIP_TARGET)
[field3] = auth username             → SIP_AUTH_USER
[field4] = auth password             → SIP_AUTH_PASS
[field5] = advertised Contact/SDP host (filled by runner)
```

`data/users.csv` stays `SEQUENTIAL` plus three-column rows. Auth is filled from
`SIP_AUTH_USER` / `SIP_AUTH_PASS` when field3/field4 are empty. Do not put real
passwords in the committed CSV.

NAT (softphone-style):

```text
bind (-i / Via [local_ip])  = SIP_LOCAL_IP → UDP route to SIP_TARGET
advertise ([field5], -mi)   = SIP_EXTERNAL_IP → SIP_CONTACT_HOST
                              → STUN if SIP_TARGET is a public IP
                              → bind IP (LAN/private destinations skip STUN)
```

`SIP_STUN=0` disables STUN. `SIP_STUN_SERVER` overrides the default STUN host.

`SIP_REFER_TO` is the Refer-To URI for `uac-refer`. TLS uses `SIP_TLS_CERT` / `SIP_TLS_KEY` / `SIP_TLS_CA`.

`SIP_TARGET` remains the network destination. It is only used as the final
fallback for the SIP domain.

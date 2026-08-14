# Address resolution

Example environment:

```bash
export SIP_TARGET=10.10.0.10:5060
export SIP_DOMAIN=pbx.example.com
export SIP_AUTH_USER=1234
export SIP_AUTH_PASS=secret
export SIP_EXTERNAL_IP=123.24.143.114
# SIP_CONTACT_HOST still works as alias for SIP_EXTERNAL_IP
```

CSV (`SEQUENTIAL` + three columns; auth from env):

```text
1000;2000;tenant-a.example.com
```

The call uses:

```text
caller     = 1000
service    = 2000
domain     = tenant-a.example.com
auth user  = SIP_AUTH_USER (field3)
auth pass  = SIP_AUTH_PASS (field4)
```

If CSV contains only:

```text
1000;2000
```

domain becomes:

```text
pbx.example.com
```

If `SIP_DOMAIN` is unset, domain becomes:

```text
10.10.0.10
```

`SIP_TARGET` is still the transport destination.

Contact uses SIPp `[field5]` (advertised host). Via uses `[local_ip]` (`-i` bind).

```text
bind (-i)     = SIP_LOCAL_IP → auto NIC toward SIP_TARGET
advertise     = SIP_EXTERNAL_IP → SIP_CONTACT_HOST → STUN (public SIP_TARGET only) → bind
```

Default STUN server: `stun.l.google.com:19302`. Set `SIP_STUN=0` to disable.

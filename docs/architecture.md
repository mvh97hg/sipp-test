# Address resolution

Example environment:

```bash
export SIP_TARGET=10.10.0.10:5060
export SIP_DOMAIN=pbx.example.com
```

CSV:

```text
1000;2000;tenant-a.example.com
```

The call uses:

```text
caller  = 1000
service = 2000
domain  = tenant-a.example.com
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

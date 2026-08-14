# CSV fields

```text
[field0] = caller
[field1] = destination / service
[field2] = SIP domain
```

Resolution:

```text
service = field1
          -> SIP_SERVICE fallback

domain  = field2
          -> SIP_DOMAIN
          -> host extracted from SIP_TARGET
```

Examples:

```csv
SEQUENTIAL
1000;2000;tenant-a.example.com
1001;2001;tenant-b.example.com
```

`SIP_TARGET` remains the network destination. It is only used as the final
fallback for the SIP domain.

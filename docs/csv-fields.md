# CSV fields

```text
[field0] = caller
[field1] = destination / service     → SIP_SERVICE
[field2] = SIP domain                → SIP_DOMAIN → host(SIP_TARGET)
[field3] = auth username             → SIP_AUTH_USER
[field4] = auth password             → SIP_AUTH_PASS

contact_host (SIPp -set, not CSV):
  SIP_EXTERNAL_IP → SIP_CONTACT_HOST → SIP_LOCAL_IP → 127.0.0.1
```

`data/users.csv` stays `SEQUENTIAL` plus three-column rows. Auth is filled from
`SIP_AUTH_USER` / `SIP_AUTH_PASS` when field3/field4 are empty. Do not put real
passwords in the committed CSV.

`SIP_TARGET` remains the network destination. It is only used as the final
fallback for the SIP domain.

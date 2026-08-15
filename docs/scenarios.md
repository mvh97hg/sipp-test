# Scenarios

One XML file should prove one behavior. Layout:

```text
scenarios/uac/  features/  media/  negative/  signaling/  uas/
```

Default `make regression` enables options, basic, auth, rtp-echo, and INFO DTMF. Turn others on in `profiles/regression.yaml` when the PBX supports them.

| Scenario | Command | What it proves | PBX need |
|---|---|---|---|
| `uac-options` | `make options` | OPTIONS | any SIP UA |
| `uac-register` | `make register` | REGISTER then Expires 0 | extension/AOR |
| `uac-basic` | `make basic` | INVITE → 200 → ACK → BYE | trunk or registered peer |
| `uac-auth` | `python3 -m sip_console run uac-auth` | digest 401/407 | challenge |
| `rtp-echo` | `make rtp` | RTP (`-rtp_echo`) | media path |
| `dtmf` | `make dtmf` | SIP INFO DTMF | INFO IVR |
| `dtmf-rfc4733` | `make dtmf-rtp` | RFC 4733 in RTP | telephone-event |
| `uac-hold` | `make hold` | re-INVITE `sendonly` | hold |
| `uac-cancel` | `make cancel` | CANCEL / 487 | cancel while ringing |
| `uac-prack` | `make prack` | 100rel PRACK | 100rel |
| `uac-refer` | `make refer` | blind REFER | set `SIP_REFER_TO` |
| `uas-answer` | `make uas` | inbound 200 | originate toward SIPp |
| `uac-busy` / `uac-notfound` / `uac-service-unavailable` | `python3 -m sip_console run uac-busy` | 486/404/503 + ACK | matching cause |

`uac-basic` is signaling-first. Use `rtp-echo` to prove audio. Default UAC scenarios do not advertise `100rel` (only `uac-prack`).

Negative tests expect that SIP code in the XML (`<recv response="486"/>`). Wrong code → SIPp fail. Enable them in the regression profile when the dialplan is ready.

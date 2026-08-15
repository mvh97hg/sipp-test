# Changelog

## 1.1.x (current)

Python-only CLI (`python3 -m sip_console`). SIPp auto-install to `./sipp` or `~/sipp`. Interactive SIPp TTY, readable `stdout.log`, segfault-after-success treated as pass.

CSV: field3/field4 are digest auth; field5 is advertised Contact (STUN / `SIP_EXTERNAL_IP` / bind). LAN targets skip STUN.

Voice scenarios: OPTIONS, REGISTER, RFC4733 DTMF, CANCEL, SIP hold, PRACK, blind REFER, TLS env. Default UAC XML does not advertise `100rel`. Negative 4xx/5xx send ACK.

Hold after ACK is `--duration` / `SIP_CALL_DURATION` / `SIP_HOLD_MS`. Peer BYE is answered.

## 1.0.x

Older notes (bash `scripts/`, `tools/prepare_csv.py`, Contact in field3) are obsolete. Historical fixes: SIPp `-t u1` mapping, UAS listen mode, semicolon CSV, no RTD markers, in-dialog `[next_url]`.

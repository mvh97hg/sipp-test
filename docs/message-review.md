# SIP message review

The scenarios are modeled after a normal Zoiper-style INVITE, while avoiding
client-specific headers that are not needed for SIP protocol testing.

Typical generated INVITE:

```text
INVITE sip:1234@demo.example.com:5090;transport=UDP SIP/2.0
Via: SIP/2.0/UDP <bind-ip>:<port>;branch=...;rport
Max-Forwards: 70
Contact: <sip:1001@<contact-host>:<port>;transport=UDP>
To: <sip:1234@demo.example.com:5090>
From: <sip:1001@demo.example.com>;tag=...
Call-ID: ...
CSeq: 1 INVITE
Allow: ...
Supported: ...
User-Agent: Sip-Console/1.1.0
Content-Type: application/sdp
Content-Length: ...

v=0
o=sip-test-console ...
s=SIP-Test-Console
c=IN IP4 <media-ip>
t=0 0
m=audio <media-port> RTP/AVP 0 101 8
a=rtpmap:0 PCMU/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-16
a=rtpmap:8 PCMA/8000
a=sendrecv
```

The following Zoiper-specific headers are intentionally not copied:
`X-cisco-serviceuri`, `Allow-Events`, and the exact Zoiper `User-Agent`.
They are application-specific rather than mandatory for a baseline INVITE.

For NAT, set `SIP_EXTERNAL_IP` so the runner passes it as SIPp `-i`. Contact, Via, and From then use built-in `[local_ip]`. `SIP_CONTACT_HOST` is still accepted as an alias for `SIP_EXTERNAL_IP`.

If the UAS challenges with 401/407, the scenario ACKs and re-INVITEs with
`[authentication username=[field3] password=[field4]]`. Those CSV fields
fall back to `SIP_AUTH_USER` / `SIP_AUTH_PASS`.

SIPp supports `[field0-n]` injection variables and the standard `[local_ip]`,
`[remote_ip]`, `[remote_port]`, `[transport]`, `[peer_tag_param]`, etc.

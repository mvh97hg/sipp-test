# SIP Test Console 1.1.0

A complete CLI-first SIP/Asterisk test harness built around SIPp.

It covers:

- outbound UAC tests
- inbound UAS tests
- multi-call/load tests
- ramp-up / steady / ramp-down load profiles
- negative SIP response tests
- DTMF
- RTP echo
- WAV/PCAP media hooks
- SIP authentication scenario template
- scenario validation
- automated regression
- JSON result summaries
- CDR correlation helpers
- reproducible artifacts

The package intentionally does **not** implement a SIP stack. SIPp is the SIP/RTP execution engine; this project is the control, scenario, load and regression layer.

## 1. Requirements

Linux recommended.

Required:

```bash
sipp -v
python3
```

Optional:

- `ffmpeg` for inspecting/creating media fixtures
- `tcpdump` or `tshark` for packet capture
- Asterisk 18/20/22/23 or a compatible SIP server

Check:

```bash
python3 -m sip_console check
```

## 2. Configuration

Set the target:

```bash
export SIP_TARGET=10.10.0.10:5060
export SIP_SERVICE=1000
export SIP_LOCAL_IP=10.10.0.20
export SIP_AUTH_USER=1234
export SIP_AUTH_PASS=secret
export SIP_EXTERNAL_IP=123.24.143.114
# SIP_CONTACT_HOST still works as alias for SIP_EXTERNAL_IP
```

For a different SIP transport:

```bash
export SIP_TRANSPORT=udp
```

Most scenarios use the SIPp `[local_ip]` / `[media_ip]` variables, so explicit local IP is optional when SIPp can determine it correctly.

## 3. Basic outbound call

```bash
python3 -m sip_console run uac-basic
```

The scenario:

```text
INVITE
  -> 100/180/183
  -> 200 OK
  -> ACK
  -> 5 sec media period
  -> BYE
  -> 200 OK
```

## 4. Inbound UAS

Start the test server:

```bash
python3 -m sip_console run uas-answer --listen 5060
```

Then originate from Asterisk toward the SIPp host.

The UAS scenario answers the INVITE and keeps the call alive for 10 seconds.

## 5. Load test

```bash
python3 -m sip_console load profiles/load-100cps.yaml
```

Example profile:

```yaml
name: basic-100cps
scenario: uac-basic
cps: 100
max_concurrent: 1000
calls: 10000
```

For a safer first test:

```bash
python3 -m sip_console load profiles/load-10cps.yaml
```

## 6. Ramp test

```bash
python3 -m sip_console load profiles/ramp.yaml
```

The runner uses SIPp's rate control and records each phase as a separate artifact.

## 7. Regression

```bash
python3 -m sip_console regression profiles/regression.yaml
```

The suite runs:

- basic outbound answer
- busy
- not found
- service unavailable
- DTMF
- RTP echo

The exact availability of a negative test depends on the Asterisk dialplan. Therefore the regression profile lets you enable/disable tests.

## 8. DTMF

Scenario:

```text
INVITE
 -> 200
 -> ACK
 -> INFO DTMF 1
 -> INFO DTMF 2
 -> INFO DTMF 3
 -> BYE
```

Run:

```bash
python3 -m sip_console run dtmf
```

This tests SIP INFO DTMF signaling. If your system uses RFC2833/4733, use a media-oriented DTMF scenario instead.

## 9. RTP echo

Run:

```bash
python3 -m sip_console run rtp-echo
```

The scenario uses SIPp media variables and enables RTP echo where supported by the installed SIPp build.

Verify your build:

```bash
sipp -v
sipp -help | grep -i rtp
```

If RTP echo is unavailable in the distribution build, use the PCAP/WAV scenarios or install a SIPp build with media support.

## 10. Media

Media scenarios are templates because the actual codec/audio requirements depend on your environment.

Put fixtures under:

```text
media/
```

Then adapt:

```text
scenarios/media/play-pcap.xml
```

and use a valid SIPp PCAP path.

Do not assume PCAP payload compatibility across codecs. For deterministic regression, PCMU/8000 is a good starting point.

## 11. Authentication

`scenarios/features/uac-auth.xml` is a REGISTER/INVITE authentication template.

Set:

```bash
export SIP_AUTH_USER=1234
export SIP_AUTH_PASS=secret
```

CSV `[field3]` / `[field4]` carry those credentials (env fallback if the CSV
row has only three columns). A 401/407 challenge ACKs and re-INVITEs with
SIPp `[authentication username=[field3] password=[field4]]`. Exact credentials
and realm must match Asterisk.

## 12. Results

Every test creates:

```text
artifacts/
  YYYYMMDD-HHMMSS-test-name/
    command.txt
    stdout.log
    stderr.log
    messages.log
    errors.log
    statistics.csv
    rtt.csv
    result.json
```

The JSON summary contains:

```json
{
  "scenario": "uac-basic",
  "exit_code": 0,
  "passed": true,
  "started_at": "...",
  "ended_at": "...",
  "artifacts": "..."
}
```

## 13. CDR correlation

The test runner records:

- test run ID
- SIPp scenario
- SIPp call number
- SIP Call-ID when available in message traces

If your Asterisk CDR has an internal UUIDv7 `call_id`, correlate it externally.

Recommended correlation:

```text
test_run_id
    |
SIPp Call-ID
    |
Asterisk CDR
    |
internal UUIDv7
```

Do not replace SIP Call-ID merely to make the test runner work.

## 14. Scenario conventions

Keep scenarios small.

Recommended:

```text
scenarios/
  uac/
  uas/
  media/
  features/
  negative/
```

A scenario should test one behavior.

Avoid putting business logic into SIPp XML.

## 15. Building a regression suite

Edit:

```text
profiles/regression.yaml
```

Example:

```yaml
name: asterisk-regression
tests:
  - name: basic
    scenario: uac-basic
    enabled: true

  - name: dtmf
    scenario: dtmf
    enabled: true

  - name: busy
    scenario: uac-busy
    enabled: false
```

A test is expected to return SIPp exit code 0.

For stricter assertions, put the expected response directly in the scenario:

```xml
<recv response="486"/>
```

Then a wrong SIP response causes the scenario to fail.

## 16. Production test methodology

Do not immediately start at 1000 CPS.

Recommended:

```text
1 CPS
10 CPS
25 CPS
50 CPS
100 CPS
250 CPS
500 CPS
```

At every step record:

- CPS
- concurrent calls
- answer rate
- failed calls
- retransmissions
- response time
- RTP packet loss
- jitter
- Asterisk CPU
- Asterisk memory
- RTP port usage
- network bandwidth
- CDR insert latency

## 17. Future UI

This package is intentionally UI-free.

The future UI should not execute arbitrary XML directly. Instead use a scenario schema:

```text
Scenario
  -> steps
     -> SEND
     -> RECV
     -> PAUSE
     -> PLAY
     -> DTMF
     -> BRANCH
     -> LABEL
```

Then compile the schema into SIPp XML.

That keeps the UI independent from the SIPp engine.

## 18. Safety

Load testing can overload a production PBX or carrier.

Use a dedicated Asterisk instance or explicit test tenant/trunk.

Start small and verify:

```bash
python3 -m sip_console check
```

before running load.



## 19. 1.0.1 fixes

This release fixes the following issues found in 1.0.0:

- `SIP_TRANSPORT=udp` was incorrectly passed as `-t udp`. It is now mapped to SIPp `-t u1`.
- TCP/TLS aliases are mapped to SIPp `t1/tn/l1/ln`.
- UAS mode no longer passes the Asterisk target as a remote destination; it starts as a SIPp server with a local listen port.
- UAC/load runs now inject `data/users.csv`, because `uac-basic.xml` uses `[field0]`.
- Media scenarios now configure `-mi` and `-mp`.
- RTP echo explicitly enables `-rtp_echo`.
- `result.py` now correctly writes `result.json` into the artifact directory.
- Added `scripts/validate.sh` for XML structure validation.
- Regression and load runners now use the same transport/media conventions as the single-call runner.

SIPp documents `u1` as UDP with one socket, `un` as UDP one socket per call, `t1/tn` as TCP, and `l1/ln` as TLS. citeturn0search0turn0search12

For RTP echo, SIPp uses `-mp` as the local RTP echo port and `[media_port]` in SDP; `-mi` controls the media IP. citeturn1search7


## 1.0.3 RTD fix

The scenarios no longer use SIPp `start_rtd` / `stop_rtd` markers.

This is deliberate: an RTD marker can remain open when a call takes an
optional/error/timeout branch, causing SIPp to print:

```text
You have started Response Time Duration 1, but have never stopped it!
```

For this package, latency is collected from SIPp's `-trace_rtt` and
`-trace_stat` artifacts instead. This avoids an unbalanced RTD state inside
the scenario while preserving the raw timing data for later reporting.

`python3 -m sip_console validate` now fails if any scenario contains `start_rtd=` or
`stop_rtd=`.


## 1.0.4 CSV service/domain resolution

UAC and load scenarios now use:

```text
[field0] = caller
[field1] = service / destination
[field2] = SIP domain
```

Fallback order:

```text
service = field1 -> SIP_SERVICE
domain  = field2 -> SIP_DOMAIN -> host from SIP_TARGET
```

For example:

```bash
export SIP_TARGET=10.10.0.10:5060
export SIP_DOMAIN=pbx.example.com
```

and:

```text
1000;2000;tenant-a.example.com
```

uses:

```text
sip:2000@tenant-a.example.com
```

If `field2` is absent, `SIP_DOMAIN` is used. If that is also absent,
the host part of `SIP_TARGET` is used.

`SIP_TARGET` remains the actual SIP network/transport destination.


## 1.0.5 message and CSV review

The UAC scenarios were reviewed against a typical Zoiper INVITE.

CSV fields are normalized before SIPp starts:

```text
[field0] = caller
[field1] = service/destination
[field2] = domain
[field3] = Contact host   (superseded in 1.1.0: field3/field4 are auth)
```

Fallbacks (1.0.5; see 1.1.0 for current Contact / auth mapping):

```text
service      = field1 -> SIP_SERVICE
domain       = field2 -> SIP_DOMAIN -> SIP_TARGET host
contact host = field3 -> SIP_CONTACT_HOST -> SIP_LOCAL_IP
```

This is important because SIPp itself cannot express the environment fallback
inside `[field2]`; the runner now generates `users.normalized.csv` for each
test run.

For NAT:

```bash
export SIP_LOCAL_IP=192.168.88.28
export SIP_CONTACT_HOST=123.24.143.114
export SIP_MEDIA_IP=123.24.143.114
```

This allows the Via/bind address and the Contact/SDP advertised address to be
different.

The UAC INVITE now includes the common baseline headers and SDP codecs
PCMU/PCMA/telephone-event. The package does not blindly copy Zoiper-specific
headers.

SIPp's scenario language supports injected CSV fields and the standard SIP
keywords used by these scenarios. citeturn0search0


## 1.0.6

Fixed `scripts/run.sh` startup ordering. `MODE` is now initialized from the
first positional argument before any `set -u` access.

Run:

```bash
python3 -m sip_console run uac-basic
```

A missing scenario now prints:

```text
usage: python3 -m sip_console run <scenario>
```

You can also run scenario validation:

```bash
python3 -m sip_console validate
```


## 1.0.7

Fixed the previous startup fix: `MODE` is initialized from `$1` before `set -u` can reject access to it. The scenario case no longer overwrites `MODE`.


## 1.0.8

Fixed a CSV parsing bug in `prepare_csv.py`. The input file is semicolon
separated (`field0;field1;field2`), but the previous implementation used
Python's default comma delimiter, so the complete row was treated as
`field0` and `field1` appeared empty.

The normalizer now detects semicolon-separated SIPp CSV and produces:

```text
SEQUENTIAL
1000;2000;pbx.example.com;...
```

A regression test is included:

```bash
python3 tools/test_prepare_csv.py
```


## 1.1.0

Breaking change: the control plane is Python-only (`python3 -m sip_console`).
Bash is not a required runtime. Required tools are `python3` and `sipp`.

CSV fields:

```text
[field0] = caller
[field1] = destination / service     → SIP_SERVICE
[field2] = SIP domain                → SIP_DOMAIN → host(SIP_TARGET)
[field3] = auth username             → SIP_AUTH_USER
[field4] = auth password             → SIP_AUTH_PASS

contact_host (SIPp `-key`, not CSV):
  SIP_EXTERNAL_IP → SIP_CONTACT_HOST → SIP_LOCAL_IP → 127.0.0.1
```

`data/users.csv` remains `SEQUENTIAL` plus three-column rows. Auth comes from
the environment when field3/field4 are empty.

Example:

```bash
python3 -m sip_console run uac-basic
python3 -m sip_console validate
python3 -m sip_console check
```

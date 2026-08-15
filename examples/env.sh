#!/usr/bin/env bash
export SIP_TARGET=127.0.0.1:5060
export SIP_SERVICE=1000
export SIP_TRANSPORT=udp
export SIP_AUTH_USER=1234
export SIP_AUTH_PASS=secret
# Optional: pin bind address. Otherwise the NIC toward SIP_TARGET is used.
# export SIP_LOCAL_IP=192.168.88.28
# Optional: skip STUN and advertise this IP in Contact/SDP.
# export SIP_EXTERNAL_IP=123.24.143.114
# export SIP_STUN=0
# export SIP_STUN_SERVER=stun.l.google.com:19302
# Hold after ACK before local BYE (seconds). Per-run: --duration 30
# export SIP_CALL_DURATION=30

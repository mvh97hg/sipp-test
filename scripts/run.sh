#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "$MODE" ]]; then
  echo "usage: $0 <scenario>" >&2
  exit 2
fi
SCENARIO="${1:?scenario required}"
shift || true

TARGET="${SIP_TARGET:-127.0.0.1:5060}"
SERVICE="${SIP_SERVICE:-}"
LOCAL_IP="${SIP_LOCAL_IP:-}"
LOCAL_PORT="${SIP_LOCAL_PORT:-}"
MEDIA_IP="${SIP_MEDIA_IP:-$LOCAL_IP}"
MEDIA_PORT="${SIP_MEDIA_PORT:-6000}"
TRANSPORT="${SIP_TRANSPORT:-udp}"
OUT="${ROOT}/artifacts/$(date +%Y%m%d-%H%M%S)-${SCENARIO}"
mkdir -p "$OUT"

CSV_SRC="$ROOT/data/users.csv"
CSV_RUN="$OUT/users.normalized.csv"
if [[ "$MODE" != "uas" && -f "$CSV_SRC" ]]; then
  python3 "$ROOT/tools/prepare_csv.py" \
    --input "$CSV_SRC" \
    --output "$CSV_RUN" \
    --service "$SERVICE" \
    --domain "${SIP_DOMAIN:-}" \
    --target "$TARGET" \
    --contact-host "${SIP_CONTACT_HOST:-$LOCAL_IP}" || exit 2
fi

case "$SCENARIO" in
  uac-basic) SC="$ROOT/scenarios/uac/uac-basic.xml";;
  uas-answer) SC="$ROOT/scenarios/uas/uas-answer.xml";;
  dtmf) SC="$ROOT/scenarios/features/dtmf.xml";;
  rtp-echo) SC="$ROOT/scenarios/media/rtp-echo.xml";;
  uac-auth) SC="$ROOT/scenarios/features/uac-auth.xml";;
  uac-busy) SC="$ROOT/scenarios/negative/uac-busy.xml";;
  uac-notfound) SC="$ROOT/scenarios/negative/uac-notfound.xml";;
  uac-service-unavailable) SC="$ROOT/scenarios/negative/uac-service-unavailable.xml";;
  *) echo "Unknown scenario: $SCENARIO"; exit 2 ;;
esac

# SIPp does not accept "udp"/"tcp"/"tls" as -t values.
# It expects transport modes such as u1, un, t1, tn, l1, ln.
case "$TRANSPORT" in
  udp) SIP_T="u1" ;;
  udp-per-call|udp_multi|udp-multi) SIP_T="un" ;;
  tcp) SIP_T="t1" ;;
  tcp-per-call|tcp_multi|tcp-multi) SIP_T="tn" ;;
  tls) SIP_T="l1" ;;
  tls-per-call|tls_multi|tls-multi) SIP_T="ln" ;;
  u1|un|t1|tn|l1|ln) SIP_T="$TRANSPORT" ;;
  *) echo "Unsupported SIP_TRANSPORT='$TRANSPORT'"; exit 2 ;;
esac

CMD=(sipp)

if [[ "$MODE" == "uas" ]]; then
  # Server/UAS mode: no remote target is required.
  CMD+=(-sf "$SC" -p "${LOCAL_PORT:-5060}" -t "$SIP_T" -m 1)
else
  CMD+=("$TARGET" -sf "$SC" -t "$SIP_T" -m 1)
  if [[ -n "$SERVICE" ]]; then CMD+=(-s "$SERVICE"); fi
  if [[ -n "$LOCAL_PORT" ]]; then
    CMD+=(-p "$LOCAL_PORT")
  fi
  if [[ -f "$ROOT/data/users.csv" ]]; then
    CMD+=(-inf "$CSV_RUN")
  fi
fi

if [[ -n "$LOCAL_IP" ]]; then
  CMD+=(-i "$LOCAL_IP")
fi

# Media scenarios need a local media address/port.
if [[ "$SCENARIO" == "uac-basic" || "$SCENARIO" == "dtmf" || "$SCENARIO" == "rtp-echo" || "$SCENARIO" == "uas-answer" ]]; then
  if [[ -n "$MEDIA_IP" ]]; then
    CMD+=(-mi "$MEDIA_IP")
  fi
  CMD+=(-mp "$MEDIA_PORT")
fi

if [[ "$SCENARIO" == "rtp-echo" ]]; then
  CMD+=(-rtp_echo)
fi

CMD+=(
  -trace_msg
  -trace_err
  -trace_stat
  -trace_rtt
  -trace_shortmsg
  -trace_calldebug
  -message_file "$OUT/messages.log"
  -error_file "$OUT/errors.log"
)

printf '%q ' "${CMD[@]}" > "$OUT/command.txt"
printf '\n' >> "$OUT/command.txt"

echo "Running: ${CMD[*]}"
"${CMD[@]}" "$@" >"$OUT/stdout.log" 2>"$OUT/stderr.log"
RC=$?

python3 "$ROOT/tools/result.py" \
  --scenario "$SCENARIO" \
  --exit-code "$RC" \
  --out "$OUT"

echo "Artifacts: $OUT"
exit "$RC"

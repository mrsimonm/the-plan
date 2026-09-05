#!/usr/bin/env bash
# Smoke gate for Potting Bench — beta checklist gate 10 (refs R4/R7).
#
# One command:   tools/smoke/smoke.sh
#
# 1. Extracts the inline <script> from index.html and runs `node --check` on it.
# 2. Serves the repo over localhost, boots the app in a fresh (in-memory)
#    playwright-cli profile at 360x732, opens every app/view, and fails on any
#    console error, uncaught exception, unhandled rejection, or failed
#    same-origin request. Prints a per-view table; exits non-zero on failure.
#
# Uses the repo's existing playwright-cli tooling (session logs land in
# .playwright-cli/ like every other run). No installs, no writes to app files.

set -u
cd "$(dirname "$0")/../.."

PORT="${SMOKE_PORT:-8137}"
SESSION="${SMOKE_SESSION:-smoke}"
PW() { playwright-cli -s="$SESSION" "$@"; }
# playwright-cli prints an update banner and blank lines around values, and
# JSON-quotes string results — pweval returns just the bare value.
pweval() { PW --raw eval "$1" 2>/dev/null | grep -v '[║╔╚]' | grep -v '^$' | tail -1 | sed 's/^"//;s/"$//'; }
TMP="${TMPDIR:-/tmp}/pb-smoke.$$"
mkdir -p "$TMP"
FAIL=0
SERVER_PID=""

cleanup() {
  PW close >/dev/null 2>&1 || true
  if [ -n "$SERVER_PID" ]; then
    { kill "$SERVER_PID" && wait "$SERVER_PID"; } >/dev/null 2>&1
  fi
  rm -rf "$TMP"
}
trap cleanup EXIT

# ---------- 1 · syntax gate ----------
echo "== syntax gate =="
if ! node tools/smoke/extract-inline-js.mjs index.html "$TMP/inline.js"; then
  echo "RESULT: FAIL (could not extract inline script)"; exit 1
fi
if node --check "$TMP/inline.js" 2>"$TMP/checkerr"; then
  echo "node --check: OK"
else
  echo "node --check: FAIL"; cat "$TMP/checkerr"
  echo "RESULT: FAIL (syntax)"; exit 1
fi

# ---------- 2 · boot the web build ----------
echo "== browser gate =="
python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
SERVER_PID=$!
for i in $(seq 1 20); do
  curl -s -o /dev/null "http://127.0.0.1:$PORT/index.html" && break
  sleep 0.25
done

PW close >/dev/null 2>&1 || true      # fresh in-memory profile
PW open "http://127.0.0.1:$PORT/index.html" >/dev/null 2>&1
PW resize 360 732 >/dev/null 2>&1

# wait for the app's own boot (show/setApp exist once the big script ran)
BOOTED=no
for i in $(seq 1 40); do
  r=$(pweval "typeof show==='function' && typeof setApp==='function'")
  [ "$r" = "true" ] && { BOOTED=yes; break; }
  sleep 0.25
done
if [ "$BOOTED" != "yes" ]; then
  echo "app failed to boot within 10s"; echo "RESULT: FAIL (boot)"; exit 1
fi

# console errors that happened during boot, before our hooks existed.
# /favicon.ico is auto-requested by the browser and absent from the repo; its
# 404 is counted separately so the gate stays useful (see IGNORED line below).
PW console error > "$TMP/boot-console.txt" 2>/dev/null || true
BOOT_ERRS=$(grep -c '^\[ERROR\]' "$TMP/boot-console.txt" 2>/dev/null | tr -d ' ')
BOOT_IGN=$(grep '^\[ERROR\]' "$TMP/boot-console.txt" 2>/dev/null | grep -c 'favicon\.ico' | tr -d ' ')
BOOT_ERRS=$((${BOOT_ERRS:-0} - ${BOOT_IGN:-0}))

# in-page hooks: uncaught exceptions, unhandled rejections, console.error
PW --raw eval "(()=>{window.__smoke={n:0,msgs:[]};const push=m=>{__smoke.n++;__smoke.msgs.push(String(m).slice(0,300))};addEventListener('error',e=>push('uncaught: '+e.message));addEventListener('unhandledrejection',e=>push('unhandledrejection: '+((e.reason&&e.reason.message)||e.reason)));const ce=console.error.bind(console);console.error=(...a)=>{push('console.error: '+a.map(String).join(' '));ce(...a)};return 'hooked'})()" >/dev/null 2>&1

# ---------- 3 · walk every app/view ----------
# label|js — the same calls the real tab/menu buttons make
VIEWS_FILE="$TMP/views.txt"
cat > "$VIEWS_FILE" <<'EOF_VIEWS'
bench:garden|setApp("bench");show("garden")
bench:mix|show("mix")
bench:cuttings|show("cuttings")
bench:plan|show("plan")
bench:library|show("library")
bench:stats|show("stats")
library:plants|show("plants")
library:academy|show("academy")
library:shelf|show("shelf")
library:log|show("log")
planner|setApp("planner")
hours|setApp("hours")
teachbench|setApp("teachbench")
teachbench-student|setApp("teachbench-student")
notes|setApp("notes")
settings|show("settings")
EOF_VIEWS

TABLE="$TMP/table.txt"
printf "%-20s %-6s %s\n" "VIEW" "SHOWN" "NEW-ERRORS" > "$TABLE"
printf "%-20s %-6s %s\n" "boot" "yes" "$BOOT_ERRS" >> "$TABLE"
[ "${BOOT_ERRS:-0}" -gt 0 ] && FAIL=1

prev=0
while IFS='|' read -r label js; do
  [ -z "$label" ] && continue
  PW --raw eval "(()=>{ $js })()" >/dev/null 2>&1   # IIFE: eval only takes expressions
  sleep 0.6
  view="${label##*:}"
  shown=$(pweval "(()=>{const el=document.getElementById('view-$view');return el?String(!el.hidden):'missing'})()")
  n=$(pweval "window.__smoke.n")
  case "$n" in ''|*[!0-9]*) n=$prev;; esac
  delta=$((n - prev)); prev=$n
  ok="yes"
  if [ "$shown" != "true" ]; then ok="NO"; FAIL=1; fi
  if [ "$delta" -gt 0 ]; then FAIL=1; fi
  printf "%-20s %-6s %s\n" "$label" "$ok" "$delta" >> "$TABLE"
done < "$VIEWS_FILE"

# ---------- 4 · network + final console sweep ----------
PW requests --static > "$TMP/requests.txt" 2>/dev/null || true
grep "127.0.0.1:$PORT" "$TMP/requests.txt" 2>/dev/null | grep -E '=> \[(4[0-9]{2}|5[0-9]{2})\]|failed' > "$TMP/netfail.txt" || true
NETIGN=$(grep -c 'favicon\.ico' "$TMP/netfail.txt" | tr -d ' ')
NETFAIL=$(( $(grep -c . "$TMP/netfail.txt" | tr -d ' ') - ${NETIGN:-0} ))
PW console error > "$TMP/console.txt" 2>/dev/null || true
pweval "JSON.stringify(window.__smoke.msgs)" > "$TMP/msgs.json" || true

# ---------- 5 · report ----------
cat "$TABLE"
printf "%-20s %-6s %s\n" "network(same-origin)" "-" "$NETFAIL"
IGN=$(( ${BOOT_IGN:-0} + ${NETIGN:-0} ))
[ "$IGN" -gt 0 ] && echo "(ignored: $IGN favicon.ico 404 — browser auto-request, no favicon.ico in repo)"
[ "${NETFAIL:-0}" -gt 0 ] && FAIL=1

if [ "$FAIL" -ne 0 ]; then
  echo ""
  echo "-- error detail --"
  grep '^\[ERROR\]' "$TMP/console.txt" 2>/dev/null | sed -n '1,40p'
  [ -s "$TMP/msgs.json" ] && cat "$TMP/msgs.json"
  sed -n '1,20p' "$TMP/netfail.txt" 2>/dev/null
  echo "RESULT: FAIL"
  exit 1
fi
echo "RESULT: PASS"

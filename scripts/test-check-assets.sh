#!/usr/bin/env bash
# Test harness for check-assets.py. Runs in a temp dir; touches no repo state.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKER="$HERE/check-assets.py"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
fail=0
check() { # name expected_exit html_body setup_cmd
  local name="$1" want="$2" body="$3" setup="${4:-true}"
  rm -rf "${TMP:?}/case"; mkdir -p "$TMP/case"
  ( cd "$TMP/case" && eval "$setup" && printf '%s' "$body" > index.html )
  set +e; ( cd "$TMP/case" && python3 "$CHECKER" index.html >/dev/null 2>&1 ); local got=$?; set -e
  if [ "$got" -ne "$want" ]; then echo "FAIL: $name (want exit $want, got $got)"; fail=1
  else echo "ok: $name"; fi
}

check "literal space resolves" 0 \
  '<img src="images/HDS Logo.png">' 'mkdir -p images && touch "images/HDS Logo.png"'
check "percent-encoded space resolves" 0 \
  '<img src="images/HDS%20Logo.png">' 'mkdir -p images && touch "images/HDS Logo.png"'
check "missing file fails" 1 \
  '<img src="images/nope.png">' 'mkdir -p images'
check "external http skipped" 0 \
  '<a href="https://how-soon.app">x</a>'
check "mailto skipped" 0 \
  '<a href="mailto:scientists@homeforderangedscientists.net">x</a>'
check "anchor skipped" 0 '<a href="#top">x</a>'
check "root-relative resolves" 0 \
  '<link href="/style.css">' 'touch style.css'
check "query string resolves" 0 \
  '<link href="style.css?v=2">' 'touch style.css'
check "fragment resolves" 0 \
  '<a href="style.css#section">x</a>' 'touch style.css'
check "protocol-relative skipped" 0 \
  '<script src="//cdn.example.com/lib.js"></script>'
check "missing file with query string fails" 1 \
  '<link href="nope.css?v=2">'

exit "$fail"

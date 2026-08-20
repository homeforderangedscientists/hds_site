#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUARD="$HERE/check-htaccess.sh"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
fail=0
check() { local name="$1" want="$2" file="$3"
  set +e; bash "$GUARD" "$file" >/dev/null 2>&1; local got=$?; set -e
  if [ "$got" -ne "$want" ]; then echo "FAIL: $name (want $want, got $got)"; fail=1
  else echo "ok: $name"; fi
}
printf 'RewriteEngine On\nRewriteRule x - [F,L]\n' > "$TMP/good"
: > "$TMP/empty"
printf '# no rewrite directive here\n' > "$TMP/norewrite"
check "valid htaccess passes"     0 "$TMP/good"
check "empty file fails"          1 "$TMP/empty"
check "missing directive fails"   1 "$TMP/norewrite"
check "absent file fails"         1 "$TMP/does-not-exist"

printf '# RewriteEngine On\nRewriteRule x - [F,L]\n' > "$TMP/commented"
check "commented-out directive fails" 1 "$TMP/commented"

printf 'RewriteEngine off\nRewriteRule x - [F,L]\n' > "$TMP/off"
check "RewriteEngine off fails"   1 "$TMP/off"

printf 'RewriteEngine on\nRewriteRule x - [F,L]\n' > "$TMP/lowercase"
check "lowercase RewriteEngine on passes" 0 "$TMP/lowercase"

printf 'RewriteEngine  On\nRewriteRule x - [F,L]\n' > "$TMP/extraspace"
check "extra-whitespace RewriteEngine  On passes" 0 "$TMP/extraspace"

printf '  RewriteEngine On\nRewriteRule x - [F,L]\n' > "$TMP/indented"
check "leading-whitespace-indented directive passes" 0 "$TMP/indented"

printf 'RewriteEngine On\r\nRewriteRule x - [F,L]\r\n' > "$TMP/crlf"
check "CRLF file passes"          0 "$TMP/crlf"

printf 'RewriteEngine On\nRewriteRule x - [F,L]\n' > "$TMP/unreadable"
chmod 000 "$TMP/unreadable"
if [ "$(id -u)" -eq 0 ]; then
  echo "skip: unreadable file fails with readability message (running as root)"
else
  set +e; out="$(bash "$GUARD" "$TMP/unreadable" 2>&1)"; got=$?; set -e
  if [ "$got" -ne 1 ]; then
    echo "FAIL: unreadable file fails with readability message (want exit 1, got $got)"; fail=1
  elif ! printf '%s' "$out" | grep -q 'not readable'; then
    echo "FAIL: unreadable file fails with readability message (message: $out)"; fail=1
  else
    echo "ok: unreadable file fails with readability message"
  fi
fi
chmod 644 "$TMP/unreadable"

exit "$fail"

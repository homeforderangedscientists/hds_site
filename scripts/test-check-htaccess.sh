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
exit "$fail"

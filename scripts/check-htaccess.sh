#!/usr/bin/env bash
# Assert .htaccess is present and plausible before deploying.
# The repo is public, so this file is not a secrecy control - but it is the
# only rewrite config the site has, and losing it silently is a real outcome
# of an editing mistake. Nothing else in the pipeline would notice.
set -euo pipefail

FILE="${1:-.htaccess}"

if [ ! -f "$FILE" ]; then
    echo "FAIL: $FILE does not exist" >&2
    exit 1
fi
if [ ! -s "$FILE" ]; then
    echo "FAIL: $FILE is empty" >&2
    exit 1
fi
if ! grep -q 'RewriteEngine On' "$FILE"; then
    echo "FAIL: $FILE is missing 'RewriteEngine On'" >&2
    exit 1
fi

echo "OK: $FILE present ($(wc -c < "$FILE" | tr -d ' ') bytes, RewriteEngine On)"

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
if [ ! -r "$FILE" ]; then
    echo "FAIL: $FILE is not readable" >&2
    exit 1
fi
# Match an ACTIVE "RewriteEngine on" directive line: optional leading
# whitespace, the directive, one or more whitespace, the "on" flag, then
# only whitespace (which also absorbs a trailing \r from CRLF files) to
# end of line. Case-insensitive for both the directive and the flag, so a
# line whose first non-whitespace character is "#" can never match (it
# starts with a byte outside the pattern), and "RewriteEngine off" cannot
# match (the flag isn't "on").
if ! grep -Eiq '^[[:space:]]*RewriteEngine[[:space:]]+on[[:space:]]*$' "$FILE"; then
    echo "FAIL: $FILE is missing an active 'RewriteEngine on' directive" >&2
    exit 1
fi

echo "OK: $FILE present ($(wc -c < "$FILE" | tr -d ' ') bytes, RewriteEngine On)"

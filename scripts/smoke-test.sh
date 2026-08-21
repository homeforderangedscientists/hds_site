#!/usr/bin/env bash
# Verify the deploy landed, from outside, against the public URL.
#
# Checks 1 and 2 pass just as happily against a stale cached copy of last
# month's site. Check 3 - comparing the served commit to the one we just
# deployed - is the only one that distinguishes "a website exists" from
# "my deploy landed". Do not drop it.
set -euo pipefail

BASE_URL="${1:?usage: smoke-test.sh <base-url> <expected-sha> <expected-string>}"
EXPECTED_SHA="${2:?missing expected sha}"
EXPECTED_STRING="${3:?missing expected string}"

BASE_URL="${BASE_URL%/}"
ATTEMPTS=6
SLEEP=5

HOME_BODY="$(mktemp)"
BUILD_INFO_BODY="$(mktemp)"
cleanup() {
    rm -f "$HOME_BODY" "$BUILD_INFO_BODY"
}
trap cleanup EXIT

echo "==> Smoke testing $BASE_URL (expecting commit $EXPECTED_SHA)"

for attempt in $(seq 1 "$ATTEMPTS"); do
    echo "--- attempt $attempt/$ATTEMPTS"
    ok=1

    # 1. Homepage responds 200.
    code="$(curl -sS -o "$HOME_BODY" -w '%{http_code}' \
             -H 'Cache-Control: no-cache' "$BASE_URL/" || true)"
    if [ "$code" != "200" ]; then
        echo "    homepage: HTTP $code (want 200)"; ok=0
    else
        echo "    homepage: HTTP 200"
    fi

    # 2. Body contains the expected marker string.
    if [ "$ok" = "1" ]; then
        if grep -qF "$EXPECTED_STRING" "$HOME_BODY"; then
            echo "    content:  found '$EXPECTED_STRING'"
        else
            echo "    content:  MISSING '$EXPECTED_STRING'"; ok=0
        fi
    fi

    # 3. /ethos/ clean URL resolves via DirectoryIndex.
    if [ "$ok" = "1" ]; then
        ethos_code="$(curl -sS -o /dev/null -w '%{http_code}' \
                 -H 'Cache-Control: no-cache' "$BASE_URL/ethos/" || true)"
        if [ "$ethos_code" != "200" ]; then
            echo "    ethos:    HTTP $ethos_code (want 200) for $BASE_URL/ethos/"; ok=0
        else
            echo "    ethos:    HTTP 200 for $BASE_URL/ethos/"
        fi
    fi

    # 4. /playbook/ clean URL resolves via DirectoryIndex.
    if [ "$ok" = "1" ]; then
        playbook_code="$(curl -sS -o /dev/null -w '%{http_code}' \
                 -H 'Cache-Control: no-cache' "$BASE_URL/playbook/" || true)"
        if [ "$playbook_code" != "200" ]; then
            echo "    playbook: HTTP $playbook_code (want 200) for $BASE_URL/playbook/"; ok=0
        else
            echo "    playbook: HTTP 200 for $BASE_URL/playbook/"
        fi
    fi

    # 5. Docs stylesheet is served.
    if [ "$ok" = "1" ]; then
        docs_css_code="$(curl -sS -o /dev/null -w '%{http_code}' \
                 -H 'Cache-Control: no-cache' "$BASE_URL/assets/docs.css" || true)"
        if [ "$docs_css_code" != "200" ]; then
            echo "    docs.css: HTTP $docs_css_code (want 200) for $BASE_URL/assets/docs.css"; ok=0
        else
            echo "    docs.css: HTTP 200 for $BASE_URL/assets/docs.css"
        fi
    fi

    # 6. The served build stamp matches the commit we just deployed.
    if [ "$ok" = "1" ]; then
        info_code="$(curl -sS -o "$BUILD_INFO_BODY" -w '%{http_code}' \
                   -H 'Cache-Control: no-cache' \
                   "$BASE_URL/build-info.json?_cb=$EXPECTED_SHA" || true)"
        if [ "$info_code" != "200" ]; then
            echo "    commit:   build-info.json HTTP $info_code (want 200)"
        else
            served="$(jq -r '.commit // "unparseable"' "$BUILD_INFO_BODY" 2>/dev/null || echo unparseable)"
            if [ "$served" = "$EXPECTED_SHA" ]; then
                echo "    commit:   $served (matches)"
                echo "==> Smoke test PASSED"
                exit 0
            fi
            echo "    commit:   served '$served', expected '$EXPECTED_SHA'"
        fi
    fi

    if [ "$attempt" -lt "$ATTEMPTS" ]; then
        echo "    retrying in ${SLEEP}s..."
        sleep "$SLEEP"
    fi
done

echo "==> Smoke test FAILED after $ATTEMPTS attempts" >&2
echo "    The rsync may have succeeded while the site did not update." >&2
echo "    Check the docroot path, then consider restoring a snapshot (docs/DEPLOY.md)." >&2
exit 1

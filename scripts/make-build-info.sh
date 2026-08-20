#!/usr/bin/env bash
# Stamp the deployed commit into the payload so verification can prove which
# commit is live. Without this, a smoke test can only prove that *a* site
# responds - not that *this* deploy landed.
set -euo pipefail

COMMIT="${1:?usage: make-build-info.sh <commit> <ref> <actor> <run-id> [html]}"
REF="${2:?missing ref}"
ACTOR="${3:?missing actor}"
RUN_ID="${4:?missing run id}"
HTML="${5:-index.html}"

SHORT="${COMMIT:0:7}"
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

cat > build-info.json <<JSON
{
  "commit": "$COMMIT",
  "ref": "$REF",
  "deployed_at": "$NOW",
  "deployed_by": "$ACTOR",
  "run_id": "$RUN_ID"
}
JSON

# Validate the heredoc actually produced JSON. A shell-quoting bug here would
# otherwise ship a corrupt file and break verification in a confusing way.
python3 -m json.tool build-info.json > /dev/null || {
    echo "FAIL: build-info.json is not valid JSON" >&2
    exit 1
}

if [ ! -f "$HTML" ]; then
    echo "FAIL: $HTML not found" >&2
    exit 1
fi

STAMP="<!-- build: $SHORT $NOW -->"
python3 - "$HTML" "$STAMP" <<'PY'
import sys
path, stamp = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8") as fh:
    html = fh.read()
if "</head>" not in html:
    sys.exit("FAIL: no </head> in %s" % path)
with open(path, "w", encoding="utf-8") as fh:
    fh.write(html.replace("</head>", "    %s\n</head>" % stamp, 1))
PY

grep -q "build: $SHORT" "$HTML" || {
    echo "FAIL: stamp not injected into $HTML" >&2
    exit 1
}

echo "OK: stamped $SHORT into $HTML and build-info.json"

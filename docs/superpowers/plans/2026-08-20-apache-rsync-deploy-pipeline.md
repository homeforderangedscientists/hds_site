# Apache rsync Deploy Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A push to `main` publishes this static site to the existing Apache host over rsync and fails loudly unless the live URL is confirmed serving that exact commit.

**Architecture:** One workflow, `.github/workflows/deploy.yml`, with two jobs. `checks` runs secret-free validation (actionlint, HTML validity, asset resolution, `.htaccess` guard) on every push and PR. `deploy` runs only on `main`, stamps the commit into `build-info.json` and `index.html`, preflights the remote docroot, snapshots it, dry-runs rsync with a blast-radius guard, rsyncs with `--delete --delay-updates`, then smoke-tests the public URL and asserts the served commit equals `github.sha`.

**Tech Stack:** GitHub Actions (ubuntu-latest), bash, rsync 3.x, OpenSSH, curl, jq, Python 3 (stdlib only, preinstalled on the runner), `html-validate` via npx, `rhysd/actionlint` container.

**Spec:** `docs/superpowers/specs/2026-08-20-apache-rsync-deploy-pipeline-design.md`

## Global Constraints

- All third-party actions **SHA-pinned** to a 40-char commit SHA with the human version in a trailing comment (e.g. `uses: actions/checkout@<sha> # v4.2.2`).
- Workflow-level `permissions: contents: read`. No job requests more.
- The `checks` job **must not reference any secret** — it runs on PRs from untrusted refs.
- `.htaccess` is **never** excluded from deploy. The exclude list is enumerated explicitly; no blanket dotfile pattern.
- Every bash step in the workflow starts with `set -euo pipefail`.
- Scripts live in `scripts/`, are `chmod +x`, and are runnable locally with the same arguments CI uses.
- Secrets referenced by exact name: `SSH_PRIVATE_KEY`, `SSH_KNOWN_HOSTS`, `SSH_HOST`, `SSH_USER`, `SSH_PORT`, `DEPLOY_PATH`. Variable: `SITE_URL`.
- `build-info.json` is generated at deploy time and **never committed** (gitignored).
- The blast-radius threshold is **10 deletions**; exceeding it fails the job unless the `force_delete` dispatch input is `true`.
- Snapshot retention on the server is the **3 most recent** archives.

---

## File Structure

| File | Responsibility |
|---|---|
| `scripts/check-assets.py` | Parse `index.html`, resolve local `src`/`href` targets against disk. Pure validation, no CI coupling. |
| `scripts/check-htaccess.sh` | Assert `.htaccess` exists, non-empty, contains `RewriteEngine On`. |
| `scripts/make-build-info.sh` | Emit `build-info.json` and stamp `index.html`. Takes SHA/ref/actor/run-id as args. |
| `scripts/smoke-test.sh` | Given a base URL and expected SHA, assert 200 + known string + `build-info.json` commit match, with retries. |
| `.deployignore` | Enumerated rsync exclude list. |
| `.htmlvalidate.json` | html-validate ruleset, shared by CI and local runs. |
| `.github/workflows/deploy.yml` | Orchestration only — calls the scripts above. |
| `docs/DEPLOY.md` | Setup runbook: keypair generation, secret population, rollback procedure. |

Scripts hold the logic; the workflow holds the wiring. This keeps every check runnable locally, which is what makes the verification tasks at the end possible without pushing to `main` repeatedly.

---

### Task 1: Asset checker

**Files:**
- Create: `scripts/check-assets.py`
- Test: `scripts/test-check-assets.sh`

**Interfaces:**
- Produces: `scripts/check-assets.py <html-file>` — exit 0 if all local refs resolve, exit 1 otherwise. Prints one line per reference: `OK`, `MISSING`, or `SKIP (external)`.

- [ ] **Step 1: Write the failing test**

```bash
cat > scripts/test-check-assets.sh <<'EOF'
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

exit "$fail"
EOF
chmod +x scripts/test-check-assets.sh
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./scripts/test-check-assets.sh`
Expected: FAIL — every case errors because `scripts/check-assets.py` does not exist yet (python3 exits 2, which does not match the wanted 0/1). Output shows `FAIL:` lines.

- [ ] **Step 3: Write minimal implementation**

```bash
cat > scripts/check-assets.py <<'EOF'
#!/usr/bin/env python3
"""Verify every local asset/link reference in an HTML file resolves on disk.

Percent-encoded and literal-space paths are both valid HTML; this repo uses a
literal space (images/HDS Logo.png), so try the decoded form first and fall
back to the raw string. External and non-file schemes are skipped, not failed:
network flake is not a code defect.
"""
import os
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlparse

SKIP_SCHEMES = {"http", "https", "mailto", "tel", "data", "javascript"}
ATTRS = ("src", "href")


class RefCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ATTRS and value:
                self.refs.append(value)


def resolve(base_dir, ref):
    """Return True if a local ref resolves. Tries decoded then raw."""
    path = ref.lstrip("/")
    for candidate in (unquote(path), path):
        if os.path.isfile(os.path.join(base_dir, candidate)):
            return True
    return False


def main():
    if len(sys.argv) != 2:
        print("usage: check-assets.py <html-file>", file=sys.stderr)
        return 2
    html_path = sys.argv[1]
    base_dir = os.path.dirname(os.path.abspath(html_path)) or "."
    with open(html_path, encoding="utf-8") as fh:
        parser = RefCollector()
        parser.feed(fh.read())

    missing = 0
    for ref in parser.refs:
        scheme = urlparse(ref).scheme.lower()
        if scheme in SKIP_SCHEMES:
            print(f"SKIP (external) {ref}")
        elif ref.startswith("#") or not ref.strip():
            print(f"SKIP (anchor)   {ref}")
        elif resolve(base_dir, ref):
            print(f"OK              {ref}")
        else:
            print(f"MISSING         {ref}")
            missing += 1

    if missing:
        print(f"\n{missing} unresolved local reference(s)", file=sys.stderr)
        return 1
    print(f"\nAll {len(parser.refs)} reference(s) accounted for.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
EOF
chmod +x scripts/check-assets.py
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./scripts/test-check-assets.sh`
Expected: PASS — seven `ok:` lines, no `FAIL:` lines, exit 0.

- [ ] **Step 5: Run against the real page**

Run: `python3 scripts/check-assets.py index.html`
Expected: exit 0. `OK` for `images/HDS Logo.png`; `SKIP (external)` for the three `https://` product links and the `mailto:` address.

- [ ] **Step 6: Commit**

```bash
git add scripts/check-assets.py scripts/test-check-assets.sh
git commit -m "feat: add asset reference checker with tests"
```

---

### Task 2: `.htaccess` guard

**Files:**
- Create: `scripts/check-htaccess.sh`
- Test: `scripts/test-check-htaccess.sh`

**Interfaces:**
- Produces: `scripts/check-htaccess.sh <path>` — exit 0 if the file exists, is non-empty, and contains `RewriteEngine On`; exit 1 otherwise.

- [ ] **Step 1: Write the failing test**

```bash
cat > scripts/test-check-htaccess.sh <<'EOF'
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
EOF
chmod +x scripts/test-check-htaccess.sh
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./scripts/test-check-htaccess.sh`
Expected: FAIL — `check-htaccess.sh` does not exist, so bash exits 127 for every case; four `FAIL:` lines.

- [ ] **Step 3: Write minimal implementation**

```bash
cat > scripts/check-htaccess.sh <<'EOF'
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
EOF
chmod +x scripts/check-htaccess.sh
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./scripts/test-check-htaccess.sh`
Expected: PASS — four `ok:` lines, exit 0.

- [ ] **Step 5: Run against the real file**

Run: `./scripts/check-htaccess.sh .htaccess`
Expected: `OK: .htaccess present (575 bytes, RewriteEngine On)`, exit 0.

- [ ] **Step 6: Commit**

```bash
git add scripts/check-htaccess.sh scripts/test-check-htaccess.sh
git commit -m "feat: add .htaccess presence guard with tests"
```

---

### Task 3: Build stamp generator

**Files:**
- Create: `scripts/make-build-info.sh`
- Modify: `.gitignore` (append `build-info.json`)
- Test: manual, shown in Step 4

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `scripts/make-build-info.sh <commit-sha> <ref> <actor> <run-id> [html-file]` — writes `build-info.json` in the CWD with keys `commit`, `ref`, `deployed_at`, `deployed_by`, `run_id`; injects `<!-- build: <short-sha> <iso8601> -->` before `</head>` in the HTML file (default `index.html`). Exit non-zero if the JSON does not parse or the stamp is not injected.

- [ ] **Step 1: Write the implementation**

```bash
cat > scripts/make-build-info.sh <<'EOF'
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
EOF
chmod +x scripts/make-build-info.sh
```

- [ ] **Step 2: Gitignore the generated file**

```bash
printf '\n# Generated at deploy time, never committed\nbuild-info.json\n' >> .gitignore
```

- [ ] **Step 3: Verify it refuses bad input**

Run: `./scripts/make-build-info.sh abc123 refs/heads/main tester 42 /nonexistent.html; echo "exit=$?"`
Expected: `FAIL: /nonexistent.html not found` and `exit=1`.

- [ ] **Step 4: Verify the happy path, then restore index.html**

```bash
cp index.html /tmp/index.html.bak
./scripts/make-build-info.sh deadbeefcafe1234 refs/heads/main tester 42
cat build-info.json
python3 -c "import json;print(json.load(open('build-info.json'))['commit'])"
grep -n 'build: deadbee' index.html
cp /tmp/index.html.bak index.html   # undo the local stamp
rm -f build-info.json
git status --short                   # must show no modification to index.html
```

Expected: valid JSON printed; `deadbeefcafe1234` echoed; one `grep` hit showing the comment before `</head>`; after restore, `git status --short` shows no change to `index.html` and no `build-info.json`.

- [ ] **Step 5: Commit**

```bash
git add scripts/make-build-info.sh .gitignore
git commit -m "feat: add deploy-time build stamp generator"
```

---

### Task 4: Smoke test

**Files:**
- Create: `scripts/smoke-test.sh`

**Interfaces:**
- Consumes: `build-info.json` as produced by `scripts/make-build-info.sh` (Task 3) — specifically its `commit` key.
- Produces: `scripts/smoke-test.sh <base-url> <expected-sha> <expected-string>` — exit 0 only if the live URL returns 200, the body contains the expected string, and the served `build-info.json`'s `commit` equals `<expected-sha>`. Retries for ~30 s.

- [ ] **Step 1: Write the implementation**

```bash
cat > scripts/smoke-test.sh <<'EOF'
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

echo "==> Smoke testing $BASE_URL (expecting commit $EXPECTED_SHA)"

for attempt in $(seq 1 "$ATTEMPTS"); do
    echo "--- attempt $attempt/$ATTEMPTS"
    ok=1

    # 1. Homepage responds 200.
    code="$(curl -sS -o /tmp/smoke-body.html -w '%{http_code}' \
             -H 'Cache-Control: no-cache' "$BASE_URL/" || echo 000)"
    if [ "$code" != "200" ]; then
        echo "    homepage: HTTP $code (want 200)"; ok=0
    else
        echo "    homepage: HTTP 200"
    fi

    # 2. Body contains the expected marker string.
    if [ "$ok" = "1" ]; then
        if grep -qF "$EXPECTED_STRING" /tmp/smoke-body.html; then
            echo "    content:  found '$EXPECTED_STRING'"
        else
            echo "    content:  MISSING '$EXPECTED_STRING'"; ok=0
        fi
    fi

    # 3. The served build stamp matches the commit we just deployed.
    if [ "$ok" = "1" ]; then
        served="$(curl -sS -H 'Cache-Control: no-cache' \
                   "$BASE_URL/build-info.json?_cb=$EXPECTED_SHA" \
                   | jq -r '.commit // "unparseable"' 2>/dev/null || echo unreachable)"
        if [ "$served" = "$EXPECTED_SHA" ]; then
            echo "    commit:   $served (matches)"
            echo "==> Smoke test PASSED"
            exit 0
        fi
        echo "    commit:   served '$served', expected '$EXPECTED_SHA'"
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
EOF
chmod +x scripts/smoke-test.sh
```

- [ ] **Step 2: Verify it fails against a URL that does not serve this site**

Run: `./scripts/smoke-test.sh https://example.com deadbeef "Home for Deranged Scientists"; echo "exit=$?"`
Expected: retries 6 times, reports `content:  MISSING 'Home for Deranged Scientists'` (example.com returns 200 but not our page), ends with `Smoke test FAILED` and `exit=1`. This proves the check can actually go red — a verification step that has never failed is not known to work.

- [ ] **Step 3: Verify it fails on commit mismatch specifically**

Run: `./scripts/smoke-test.sh https://example.com deadbeef "Example Domain"; echo "exit=$?"`
Expected: homepage 200 and content found, then `commit:   served 'unreachable', expected 'deadbeef'`, ending `FAILED`, `exit=1`. This proves check 3 is load-bearing and not silently skipped when checks 1–2 pass.

- [ ] **Step 4: Commit**

```bash
git add scripts/smoke-test.sh
git commit -m "feat: add post-deploy smoke test asserting served commit"
```

---

### Task 5: Deploy exclude list and html-validate config

**Files:**
- Create: `.deployignore`
- Create: `.htmlvalidate.json`

**Interfaces:**
- Produces: `.deployignore` for `rsync --exclude-from`; `.htmlvalidate.json` consumed by `npx html-validate`.

- [ ] **Step 1: Write the exclude list**

```bash
cat > .deployignore <<'EOF'
# rsync --exclude-from list for deploys to the Apache docroot.
#
# Enumerated deliberately. A blanket dotfile pattern (.*) would exclude
# .htaccess, which is the site's only rewrite config - so patterns are listed
# one by one and .htaccess is never among them.
.git/
.github/
.gitignore
.deployignore
.htmlvalidate.json
.DS_Store
docs/
scripts/
CLAUDE.md
EOF
```

- [ ] **Step 2: Confirm .htaccess is NOT excluded**

Run: `grep -vE '^\s*(#|$)' .deployignore | grep -c 'htaccess'`
Expected: `0`.

The comment lines must be stripped BEFORE grepping. The file's header comment
deliberately names `.htaccess` — that warning is the whole point of the comment,
and an assertion over the raw file would force the warning to be reworded into
uselessness. Only *pattern* lines matter here. If this is ever non-zero, the
deploy will silently strip the site's rewrite rules.

- [ ] **Step 3: Confirm the exclude list behaves under rsync**

```bash
rsync -avn --delete --exclude-from=.deployignore ./ /tmp/deploy-preview/ | tee /tmp/rsync-preview.txt
grep -E '^(\.htaccess|index\.html)$' /tmp/rsync-preview.txt
grep -E '^(CLAUDE\.md|docs/|scripts/)' /tmp/rsync-preview.txt && echo "UNEXPECTED: excluded path present" || echo "OK: excluded paths absent"
```

Expected: `.htaccess` and `index.html` appear in the transfer list; `CLAUDE.md`, `docs/`, and `scripts/` do not, printing `OK: excluded paths absent`.

- [ ] **Step 4: Write the html-validate config**

```bash
cat > .htmlvalidate.json <<'EOF'
{
  "extends": ["html-validate:recommended"],
  "rules": {
    "void-style": "off",
    "no-inline-style": "off",
    "require-sri": "off"
  }
}
EOF
```

Rationale, corrected after review: all three rules are **already off** under
`html-validate:recommended`, so these lines are explicit no-ops, not loosenings —
they are kept to pin intent if the preset's defaults ever change. Note that
`no-inline-style` targets `style=""` **attributes**, not `<style>` blocks; the
real reason it must stay off is that `index.html` contains an inline
`<p style="margin-top: 1rem;">`. `require-sri` does not apply to a page with no
external scripts.

- [ ] **Step 5: Run html-validate locally and fix any real findings**

Run: `npx --yes html-validate@9 index.html`
Expected: exit 0. If it reports genuine errors (e.g. a missing `alt` attribute), **fix `index.html`** rather than disabling the rule — the point of the gate is to catch these. Record what was fixed in the commit message.

- [ ] **Step 6: Commit**

```bash
git add .deployignore .htmlvalidate.json index.html
git commit -m "feat: add deploy exclude list and html-validate config"
```

---

### Task 6: The `checks` job

**Files:**
- Create: `.github/workflows/deploy.yml`

**Interfaces:**
- Consumes: `scripts/check-assets.py` (Task 1), `scripts/check-htaccess.sh` (Task 2), `.htmlvalidate.json` (Task 5).
- Produces: a `checks` job that later tasks reference via `needs: checks`.

- [ ] **Step 1: Write the workflow with only the checks job**

```yaml
name: Deploy

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:
    inputs:
      force_delete:
        description: "Allow rsync to delete more than 10 files"
        type: boolean
        default: false
      first_deploy:
        description: "Skip the 'docroot already has index.html' preflight check"
        type: boolean
        default: false

permissions:
  contents: read

concurrency:
  group: deploy-production
  cancel-in-progress: false

jobs:
  checks:
    name: Checks
    runs-on: ubuntu-latest
    steps:
      - name: Check out
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2

      - name: Lint workflows
        run: |
          set -euo pipefail
          docker run --rm -v "$PWD:/repo" -w /repo \
            rhysd/actionlint:1.7.7 -color

      - name: Validate HTML
        run: |
          set -euo pipefail
          npx --yes html-validate@9 index.html

      - name: Check asset references
        run: |
          set -euo pipefail
          python3 scripts/check-assets.py index.html

      - name: Guard .htaccess
        run: |
          set -euo pipefail
          ./scripts/check-htaccess.sh .htaccess
```

- [ ] **Step 2: Verify the workflow parses before pushing**

Run: `docker run --rm -v "$PWD:/repo" -w /repo rhysd/actionlint:1.7.7 -color`
Expected: no output, exit 0.

If Docker is unavailable locally, install actionlint directly rather than
skipping the check — `brew install actionlint && actionlint`. Do not fall back to
a plain YAML parse: `pyyaml` is **not** installed on this machine (verified), and
a YAML parse would not catch the shell and expression bugs actionlint exists to
find.

- [ ] **Step 3: Verify each check step passes locally**

```bash
npx --yes html-validate@9 index.html && echo "html ok"
python3 scripts/check-assets.py index.html && echo "assets ok"
./scripts/check-htaccess.sh .htaccess && echo "htaccess ok"
```

Expected: `html ok`, `assets ok`, `htaccess ok` — each preceded by its own output, all exit 0.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/deploy.yml
git commit -m "feat: add CI checks job for HTML, assets, and .htaccess"
```

---

### Task 7: The `deploy` job

**Files:**
- Modify: `.github/workflows/deploy.yml` (append the `deploy` job)

**Interfaces:**
- Consumes: `checks` job (Task 6); `scripts/make-build-info.sh` (Task 3); `scripts/smoke-test.sh` (Task 4); `.deployignore` (Task 5).
- Produces: the complete pipeline. No later task depends on new symbols.

- [ ] **Step 1: Append the deploy job**

Append to `.github/workflows/deploy.yml`, at the same indent level as `checks:`:

```yaml
  deploy:
    name: Deploy to Apache
    needs: checks
    if: github.ref == 'refs/heads/main' && github.event_name != 'pull_request'
    runs-on: ubuntu-latest
    environment:
      name: production
      url: ${{ vars.SITE_URL }}
    steps:
      - name: Check out
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2

      - name: Generate build stamp
        run: |
          set -euo pipefail
          ./scripts/make-build-info.sh \
            "${{ github.sha }}" \
            "${{ github.ref }}" \
            "${{ github.actor }}" \
            "${{ github.run_id }}"

      - name: Configure SSH
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
          SSH_KNOWN_HOSTS: ${{ secrets.SSH_KNOWN_HOSTS }}
        run: |
          set -euo pipefail
          mkdir -p ~/.ssh
          chmod 700 ~/.ssh
          printf '%s\n' "$SSH_PRIVATE_KEY" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          printf '%s\n' "$SSH_KNOWN_HOSTS" > ~/.ssh/known_hosts
          chmod 644 ~/.ssh/known_hosts
          test -s ~/.ssh/known_hosts || { echo "SSH_KNOWN_HOSTS secret is empty" >&2; exit 1; }

      - name: Preflight remote docroot
        env:
          SSH_HOST: ${{ secrets.SSH_HOST }}
          SSH_USER: ${{ secrets.SSH_USER }}
          SSH_PORT: ${{ secrets.SSH_PORT }}
          DEPLOY_PATH: ${{ secrets.DEPLOY_PATH }}
          FIRST_DEPLOY: ${{ inputs.first_deploy }}
        run: |
          set -euo pipefail
          ssh -i ~/.ssh/deploy_key -p "$SSH_PORT" \
            "$SSH_USER@$SSH_HOST" \
            "DEPLOY_PATH='$DEPLOY_PATH' FIRST_DEPLOY='$FIRST_DEPLOY' bash -s" <<'REMOTE'
          set -euo pipefail
          if [ ! -d "$DEPLOY_PATH" ]; then
              echo "FAIL: DEPLOY_PATH '$DEPLOY_PATH' is not a directory" >&2
              exit 1
          fi
          if [ "$FIRST_DEPLOY" != "true" ] && [ ! -f "$DEPLOY_PATH/index.html" ]; then
              echo "FAIL: '$DEPLOY_PATH' has no index.html - wrong path?" >&2
              echo "      Re-run with first_deploy=true if this is genuinely the first deploy." >&2
              exit 1
          fi
          echo "OK: docroot $DEPLOY_PATH verified"
          REMOTE

      - name: Snapshot current docroot
        env:
          SSH_HOST: ${{ secrets.SSH_HOST }}
          SSH_USER: ${{ secrets.SSH_USER }}
          SSH_PORT: ${{ secrets.SSH_PORT }}
          DEPLOY_PATH: ${{ secrets.DEPLOY_PATH }}
          SHORT_SHA: ${{ github.sha }}
        run: |
          set -euo pipefail
          ssh -i ~/.ssh/deploy_key -p "$SSH_PORT" \
            "$SSH_USER@$SSH_HOST" \
            "DEPLOY_PATH='$DEPLOY_PATH' SHORT_SHA='${SHORT_SHA:0:7}' bash -s" <<'REMOTE'
          set -euo pipefail
          BACKUP_DIR="$(dirname "$DEPLOY_PATH")/.hds-deploy-backups"
          mkdir -p "$BACKUP_DIR"
          STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
          ARCHIVE="$BACKUP_DIR/${STAMP}-${SHORT_SHA}.tgz"
          tar czf "$ARCHIVE" -C "$DEPLOY_PATH" .
          echo "OK: snapshot $ARCHIVE ($(du -h "$ARCHIVE" | cut -f1))"
          # Keep only the 3 most recent snapshots.
          ls -1t "$BACKUP_DIR"/*.tgz 2>/dev/null | tail -n +4 | while read -r old; do
              echo "    pruning $old"
              rm -f "$old"
          done
          REMOTE

      - name: Dry-run rsync and check blast radius
        env:
          SSH_HOST: ${{ secrets.SSH_HOST }}
          SSH_USER: ${{ secrets.SSH_USER }}
          SSH_PORT: ${{ secrets.SSH_PORT }}
          DEPLOY_PATH: ${{ secrets.DEPLOY_PATH }}
          FORCE_DELETE: ${{ inputs.force_delete }}
        run: |
          set -euo pipefail
          rsync -azn --delete --delay-updates --itemize-changes \
            --exclude-from=.deployignore \
            -e "ssh -i ~/.ssh/deploy_key -p $SSH_PORT" \
            ./ "$SSH_USER@$SSH_HOST:$DEPLOY_PATH/" | tee /tmp/dryrun.txt

          echo "--- Planned deletions ---"
          grep '^\*deleting' /tmp/dryrun.txt || echo "(none)"
          DELETIONS="$(grep -c '^\*deleting' /tmp/dryrun.txt || true)"
          echo "Deletion count: $DELETIONS"

          if [ "$DELETIONS" -gt 10 ] && [ "$FORCE_DELETE" != "true" ]; then
              echo "FAIL: $DELETIONS deletions exceeds the threshold of 10." >&2
              echo "      This usually means DEPLOY_PATH is wrong." >&2
              echo "      If the deletions above are intended, re-run via" >&2
              echo "      workflow_dispatch with force_delete=true." >&2
              exit 1
          fi

      - name: Deploy
        env:
          SSH_HOST: ${{ secrets.SSH_HOST }}
          SSH_USER: ${{ secrets.SSH_USER }}
          SSH_PORT: ${{ secrets.SSH_PORT }}
          DEPLOY_PATH: ${{ secrets.DEPLOY_PATH }}
        run: |
          set -euo pipefail
          rsync -az --delete --delay-updates --itemize-changes \
            --exclude-from=.deployignore \
            -e "ssh -i ~/.ssh/deploy_key -p $SSH_PORT" \
            ./ "$SSH_USER@$SSH_HOST:$DEPLOY_PATH/"

      - name: Smoke test
        env:
          SITE_URL: ${{ vars.SITE_URL }}
        run: |
          set -euo pipefail
          ./scripts/smoke-test.sh \
            "$SITE_URL" \
            "${{ github.sha }}" \
            "Home for Deranged Scientists"

      - name: Clean up SSH key
        if: always()
        run: rm -f ~/.ssh/deploy_key
```

- [ ] **Step 2: Lint the completed workflow**

Run: `docker run --rm -v "$PWD:/repo" -w /repo rhysd/actionlint:1.7.7 -color`
Expected: no output, exit 0. Fix any reported issue before committing — this file cannot be tested any other way without pushing.

- [ ] **Step 3: Confirm the checks job stays secret-free**

The `checks` job runs on pull requests, including from forks. A secret reference
there would expose credentials to untrusted code. This check uses `awk` rather
than a YAML library because `pyyaml` is not installed on this machine (verified).

```bash
awk '/^  checks:/{f=1;next} /^  [a-z_-]+:/{f=0} f' .github/workflows/deploy.yml \
  > /tmp/checks-job.yml
wc -l < /tmp/checks-job.yml   # sanity: must be > 0, else the awk range is wrong
if grep -q 'secrets\.' /tmp/checks-job.yml; then
    echo "FAIL: checks job references secrets"; exit 1
else
    echo "ok: checks job is secret-free"
fi
```

Expected: a non-zero line count, then `ok: checks job is secret-free`. If the line
count is 0 the extraction silently matched nothing — fix the awk range before
trusting the result.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/deploy.yml
git commit -m "feat: add deploy job with preflight, snapshot, and smoke test"
```

---

### Task 8: Setup runbook

**Files:**
- Create: `docs/DEPLOY.md`

**Interfaces:**
- Consumes: everything above. Documents the human-side setup that cannot be automated from this repo.

- [ ] **Step 1: Write the runbook**

````bash
cat > docs/DEPLOY.md <<'EOF'
# Deploy Runbook

Pushing to `main` deploys this site to the Apache host and verifies the live URL
is serving that exact commit. Design: `docs/superpowers/specs/2026-08-20-apache-rsync-deploy-pipeline-design.md`

## One-time setup

### 1. Generate a dedicated deploy key

Use a key that exists only for this workflow, so revoking it costs nothing.
Do **not** reuse a personal key.

```bash
ssh-keygen -t ed25519 -f ~/.ssh/hds_deploy -C "github-actions-hds-site" -N ""
```

Install the public half on the server:

```bash
ssh-copy-id -i ~/.ssh/hds_deploy.pub -p <PORT> <USER>@<HOST>
```

Verify it works before going further:

```bash
ssh -i ~/.ssh/hds_deploy -p <PORT> <USER>@<HOST> 'echo connected; pwd'
```

### 2. Capture the host key

The workflow pins the host key rather than running `ssh-keyscan` at deploy time.
Keyscan-on-every-run is trust-on-first-use repeated forever — it trusts whatever
answers on the day. Capture it once, here, and eyeball it:

```bash
ssh-keyscan -p <PORT> -H <HOST>
```

Compare the fingerprint against what your known-hosts already has from a session
you trust:

```bash
ssh-keygen -lf <(ssh-keyscan -p <PORT> <HOST> 2>/dev/null)
```

### 3. Populate GitHub secrets and variables

```bash
gh secret set SSH_PRIVATE_KEY  < ~/.ssh/hds_deploy
gh secret set SSH_KNOWN_HOSTS  # paste the ssh-keyscan output from step 2
gh secret set SSH_HOST         # e.g. homeforderangedscientists.net
gh secret set SSH_USER
gh secret set SSH_PORT         # 22 unless your host differs
gh secret set DEPLOY_PATH      # absolute docroot, e.g. /home/<user>/public_html
gh variable set SITE_URL       # e.g. https://homeforderangedscientists.net
```

`DEPLOY_PATH` must have **no trailing slash** and must be the directory whose
contents are served — the one that already contains `index.html`.

### 4. First deploy

If the docroot already contains an `index.html`, just push to `main`.

If it is genuinely empty, the preflight check will refuse. Run it manually once:

```bash
gh workflow run Deploy -f first_deploy=true
gh run watch
```

## Routine deploys

Push to `main`. Watch it:

```bash
gh run watch
```

To redeploy the current `main` without an empty commit:

```bash
gh workflow run Deploy
```

## When rsync wants to delete more than 10 files

The job stops and prints the deletion list. This almost always means
`DEPLOY_PATH` points somewhere unintended. **Read the printed list before
overriding.** If the deletions are genuinely correct:

```bash
gh workflow run Deploy -f force_delete=true
```

## Rollback

Rollback is manual and snapshot-backed. The deploy job archives the docroot
before every deploy, keeping the 3 most recent:

```bash
ssh -i ~/.ssh/hds_deploy -p <PORT> <USER>@<HOST>
ls -1t "$(dirname <DEPLOY_PATH>)/.hds-deploy-backups"/*.tgz
tar xzf <chosen-archive> -C <DEPLOY_PATH>
```

Then confirm from outside — do not trust the extraction alone:

```bash
curl -sS https://<site>/build-info.json | jq .commit
```

Alternatively, re-run the workflow at the last good commit from the GitHub UI
(Actions → Deploy → the good run → "Re-run all jobs").

## What the smoke test actually proves

It fetches `build-info.json` from the live site and asserts its `commit` equals
the SHA that was just pushed. A check that only asserted "HTTP 200 with the right
text" would pass against a stale cached copy — including one where rsync silently
wrote nothing. The commit comparison is the load-bearing assertion.

If the smoke test fails, **the files may already be on the server.** The deploy
is not rolled back automatically. Diagnose before re-pushing.
EOF
````

- [ ] **Step 2: Verify every command in the runbook is syntactically valid**

Run: `grep -oE '^(ssh|rsync|gh|tar|curl|ssh-keygen|ssh-copy-id|ssh-keyscan) [^|]*' docs/DEPLOY.md | head -30`
Expected: prints the commands; read them and confirm each flag exists (`gh secret set --help`, `gh variable set --help`). Fix any that do not.

- [ ] **Step 3: Commit**

```bash
git add docs/DEPLOY.md
git commit -m "docs: add deploy setup and rollback runbook"
```

---

### Task 9: Prove the pipeline works — and prove it can fail

**Files:** none created; this task is verification.

**Interfaces:** Consumes the complete pipeline from Tasks 1–8.

This is the task that turns "the workflow went green" into "the pipeline is known
to work." A verification step that has never failed is not known to work.

- [ ] **Step 1: Merge to main and confirm a real deploy**

```bash
git push origin main
gh run watch
curl -sS "$(gh variable get SITE_URL)/build-info.json" | jq .
```

Expected: workflow green; the served `.commit` equals `git rev-parse HEAD`.

- [ ] **Step 2: Prove the smoke test can go red**

Temporarily change the expected string in the workflow to something absent:

```bash
sed -i.bak 's/"Home for Deranged Scientists"/"This String Is Not On The Page"/' .github/workflows/deploy.yml
git commit -am "test: deliberately break smoke test assertion"
git push origin main
gh run watch
```

Expected: the deploy steps succeed, then **Smoke test fails** after 6 attempts,
and the workflow is red. If it goes green, the smoke test is not actually
asserting anything — stop and fix it before proceeding.

Then revert:

```bash
git revert --no-edit HEAD
git push origin main
gh run watch
```

Expected: green again.

- [ ] **Step 3: Prove `--delete` actually removes files**

```bash
echo "delete me" > scratch-delete-test.txt
git add scratch-delete-test.txt && git commit -m "test: add file to verify --delete"
git push origin main && gh run watch
curl -sS -o /dev/null -w '%{http_code}\n' "$(gh variable get SITE_URL)/scratch-delete-test.txt"
```

Expected: `200`.

```bash
git rm scratch-delete-test.txt && git commit -m "test: remove file to verify --delete"
git push origin main && gh run watch
curl -sS -o /dev/null -w '%{http_code}\n' "$(gh variable get SITE_URL)/scratch-delete-test.txt"
```

Expected: `404`. This proves the repo is genuinely the source of truth.

- [ ] **Step 4: Prove the preflight catches a bad DEPLOY_PATH**

```bash
gh secret set DEPLOY_PATH --body "/home/nonexistent/wrong-path"
gh workflow run Deploy && gh run watch
```

Expected: the **Preflight remote docroot** step fails with
`FAIL: DEPLOY_PATH '/home/nonexistent/wrong-path' is not a directory`, and rsync
never runs. Restore immediately:

```bash
gh secret set DEPLOY_PATH --body "<the real docroot>"
gh workflow run Deploy && gh run watch
```

Expected: green.

- [ ] **Step 5: Prove the blast-radius guard blocks a large deletion**

The guard is the main protection against a wrong `DEPLOY_PATH` combined with
`--delete`. Verify it actually triggers rather than assuming the arithmetic is
right.

```bash
mkdir -p scratch-blast
for i in $(seq 1 11); do echo "file $i" > "scratch-blast/f$i.txt"; done
git add scratch-blast && git commit -m "test: stage 11 files for blast-radius check"
git push origin main && gh run watch    # deploys them; 11 additions, 0 deletions
```

Expected: green (the guard counts deletions, not additions).

```bash
git rm -r scratch-blast && git commit -m "test: remove 11 files to trip the guard"
git push origin main && gh run watch
```

Expected: the **Dry-run rsync** step prints 11 `*deleting` lines and fails with
`FAIL: 11 deletions exceeds the threshold of 10.` rsync never runs for real, and
the 11 files are still live. Confirm:

```bash
curl -sS -o /dev/null -w '%{http_code}\n' "$(gh variable get SITE_URL)/scratch-blast/f1.txt"
```

Expected: `200` — the deletion was blocked, not applied.

Now clear them intentionally, exercising the documented override:

```bash
gh workflow run Deploy -f force_delete=true && gh run watch
curl -sS -o /dev/null -w '%{http_code}\n' "$(gh variable get SITE_URL)/scratch-blast/f1.txt"
```

Expected: green, then `404`. This proves both halves: the guard blocks by default,
and the override works when you genuinely mean it.

- [ ] **Step 6: Confirm the snapshot exists on the server**

```bash
ssh -i ~/.ssh/hds_deploy -p <PORT> <USER>@<HOST> \
  'ls -1t "$(dirname <DEPLOY_PATH>)/.hds-deploy-backups"/*.tgz | head -5'
```

Expected: at most 3 archives, newest first — proving both that snapshots are
written and that retention prunes correctly.

- [ ] **Step 7: Record the evidence**

Paste the actual command output from Steps 1–5 into the PR or a comment on the
deploy spec. Prose summaries of verification are indistinguishable from
hallucinations; the output is the evidence.

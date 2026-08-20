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
answers on the day, so a run-time keyscan gives you no protection against a
man-in-the-middle that shows up after setup. Capture the key once, here, verify
it by eye, and it becomes a fixed secret the workflow checks every run instead of
blindly trusting.

```bash
ssh-keyscan -p <PORT> -H <HOST>
```

Compare the fingerprint against what your known-hosts already has from a session
you trust:

```bash
ssh-keygen -lf <(ssh-keyscan -p <PORT> <HOST> 2>/dev/null)
```

### 3. Populate GitHub secrets and variables

The workflow reads exactly six secrets and one variable. Names must match
exactly — these are what `.github/workflows/deploy.yml` references:

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
contents are already served — the one that already contains `index.html`.

### 4. First deploy

If the docroot already contains this site's `index.html` (i.e. it contains the
text `Home for Deranged Scientists`), just push to `main`.

If it is genuinely empty, or does not yet contain that marker, the preflight
check will refuse. Run it manually once, bypassing both checks:

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

## Continuous checks on pull requests

Every push and every pull request against `main` runs a `checks` job first:
it lints the workflow itself, validates `index.html` with `html-validate`
(pinned to `9.7.1`), checks that referenced assets actually exist, and guards
`.htaccess`. This job never touches secrets, so it runs safely on pull requests
from any branch. The `deploy` job only runs after `checks` passes, and only on
pushes to `main` — pull requests never trigger a deploy.

## Preflight: what stops a bad `DEPLOY_PATH` from doing damage

Before every deploy, the workflow SSHes in and verifies three things about
`DEPLOY_PATH`:

1. It is a directory that exists.
2. It contains an `index.html`.
3. That `index.html` contains the text `Home for Deranged Scientists`.

The third check exists because "a directory with an `index.html`" is not proof
it's *this* site's docroot — it could belong to another site entirely. If it
doesn't, preflight fails with:

```
FAIL: '<DEPLOY_PATH>/index.html' does not contain the expected site marker.
      The docroot appears to belong to a different site.
```

Both the `index.html` check and the marker check are skipped when the run is
dispatched with `first_deploy=true` (see "First deploy" above) — there is
nothing to verify against on a truly empty docroot.

## When rsync wants to delete more than 10 files

The job stops and prints the deletion list. This almost always means
`DEPLOY_PATH` points somewhere unintended. **Read the printed list before
overriding.** If the deletions are genuinely correct:

```bash
gh workflow run Deploy -f force_delete=true
```

The same guard also fails closed if the deletion count it parsed isn't a plain
number — rather than risk proceeding on a miscounted or garbled value, it
treats an unparseable count as a reason to stop.

## Rollback

Rollback is manual and snapshot-backed. The deploy job archives the docroot
before every deploy, as a sibling directory of the docroot itself — so the
snapshot directory is never web-servable and is never touched by the deploy's
own rsync (which only ever touches `DEPLOY_PATH`). Archives live at:

```
$(dirname <DEPLOY_PATH>)/.hds-deploy-backups/<utc-timestamp>-<short-sha>.tgz
```

The 3 most recent snapshots are kept; older ones are pruned automatically.

**If the smoke test fails, the files are already on the server.** The deploy
job writes to the docroot with rsync, then smoke-tests the result — it does
not wait for the smoke test to pass before writing. A failed smoke test means
something bad may now be live, not that nothing happened. Diagnose before
re-pushing.

To restore a snapshot:

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
wrote nothing. Comparing commits is what distinguishes "a website exists and
responds" from "my deploy landed" — the two are not the same claim, and only the
commit comparison proves the second one.

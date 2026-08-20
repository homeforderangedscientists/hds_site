# Deploy Pipeline: GitHub Actions → Apache host over rsync

**Date:** 2026-08-20
**Status:** Approved design, pending implementation plan
**Repo:** `homeforderangedscientists/hds_site` (public)

## Problem

Pushing to `main` currently changes nothing on the live site. Deploys are manual,
which means the live site and `main` can silently diverge, and nobody can answer
"what commit is production running?" without guessing.

## Goal

A push to `main` publishes the site to the existing Apache host, and the workflow
fails loudly if the live site does not end up serving that exact commit.

## Constraints (established, not assumed)

- Host is an existing **Apache shared host / VPS**, reachable over **SSH**. Staying on it.
- The **repo is the complete docroot** — no server-side files to preserve.
- The repo is **public**, so `.htaccess`'s blocking of `CLAUDE.md` and dotfiles
  provides no secrecy. It is retained for tidiness, not treated as a control.
- Site is static: one `index.html` plus `images/` (~2.8 MB). No build step.

## Approach

**Chosen: rsync in place with `--delay-updates`.** Files stage in a temporary
directory on the *receiving* side and are renamed into place in one batch at the
end, so the window where the docroot is half-updated is milliseconds rather than
the duration of the transfer.

**Rejected — versioned release dirs + `current` symlink:** genuinely atomic and
gives instant rollback, but requires the docroot itself to be a symlink. On cPanel
`public_html` that is often disallowed, and it is a larger change to a host we
explicitly decided not to disturb.

**Rejected — `git pull` on the server:** simplest to write, but places a git
checkout inside the webroot and makes an `.htaccess` regex the only thing between
the public and `.git/`. Not a dependency worth taking.

## Architecture

Single workflow, `.github/workflows/deploy.yml`, two jobs.

```
push to main ──▶ [job: checks] ──▶ [job: deploy] ──▶ green
                       │                  │
                  no secrets    preflight → snapshot → dry-run →
                                rsync → smoke test
```

The smoke test is the final *step of the deploy job*, not a separate job — it must
fail the same job that performed the deploy, so the run record shows one red
deploy rather than a green deploy followed by a red check.

- `on: push` (branches: `main`) and `workflow_dispatch` for redeploy without an
  empty commit.
- `concurrency: { group: deploy-production, cancel-in-progress: false }` — two
  fast pushes queue rather than racing two rsyncs at the same docroot.
- `permissions: contents: read` at workflow level.
- All third-party actions **SHA-pinned** with the human version in a trailing comment.

### Job 1 — `checks`

Runs on every push and PR. Touches no secrets, so it is safe to run on untrusted refs.

1. **actionlint** — the workflow is code; lint it before trusting it. Run via the
   pinned `rhysd/actionlint` container rather than a `curl | bash` installer.
2. **HTML validity** — `html-validate` against `index.html`, config committed as
   `.htmlvalidate.json` so local and CI agree.
3. **Asset/link check** — parse every `src`/`href` in `index.html`; for
   repo-relative targets, assert the file exists on disk. **The checker must
   percent-decode before the filesystem check, and must tolerate an already-decoded
   literal space.** Verified against the current source: `index.html` references
   `src="images/HDS Logo.png"` with a *literal* space, not `%20`. Both spellings
   are valid HTML and both must resolve, so the checker decodes and then falls back
   to the raw string. `mailto:` and other non-http schemes are skipped entirely.
   External `http(s)` links are reported but never fail the build (network flake is
   not a code defect).
4. **`.htaccess` guard** — assert the file exists, is non-empty, and contains
   `RewriteEngine On`. Losing it silently is a plausible outcome of an editing
   mistake, and nothing else in the pipeline would notice.

### Job 2 — `deploy`

`needs: checks`, gated on `github.ref == 'refs/heads/main'`. Declares
`environment: { name: production, url: <SITE_URL> }` so GitHub records deployment
history. No manual approval gate (explicitly chosen).

1. **Build stamp.** Generate `build-info.json` at deploy time (never committed;
   added to `.gitignore`) containing `commit`, `ref`, `deployed_at`, `deployed_by`,
   `run_id`. Also inject `<!-- build: <short-sha> <timestamp> -->` before `</head>`
   in `index.html`. This is what makes verification honest — see *Smoke test*.
2. **SSH setup, done inline.** Write the key to `~/.ssh/deploy_key` at mode 600 and
   write `~/.ssh/known_hosts` from the **`SSH_KNOWN_HOSTS` secret**. Deliberately
   *not* `ssh-keyscan` at runtime — that trusts whatever answers on the day, which
   is trust-on-first-use repeated every single run. The host key is captured once,
   verified out of band, and stored. Deliberately not a third-party SSH action:
   this step handles the private key, so it has the fewest supply-chain
   dependencies of anything in the pipeline.
3. **Preflight.** Over SSH, assert `DEPLOY_PATH` exists, is a directory, and
   already contains `index.html`. A wrong or empty `DEPLOY_PATH` combined with
   `--delete` is the worst outcome this pipeline can produce; this check makes that
   failure impossible rather than unlikely. A `first_deploy` `workflow_dispatch`
   input bypasses the `index.html` requirement for the initial run.
4. **Server-side snapshot.** `tar czf` the current docroot into
   `$(dirname "$DEPLOY_PATH")/.hds-deploy-backups/<utc-timestamp>-<short-sha>.tgz`,
   retaining the **3 most recent** and deleting older ones. The directory sits
   outside the docroot so the backups are never web-reachable; the deploy fails if
   it cannot be created. At 2.8 MB this is free, and it turns
   rollback from "re-run an old commit and hope" into a documented one-line restore.
5. **Dry run first.** `rsync -azn --delete --itemize-changes`, output printed to the
   log so the deletion set is visible in the run record. **Fail the job if the dry
   run would delete more than 10 files** unless a `force_delete` dispatch input is
   set. Blast radius is a thing to bound, not to discover.
6. **Real rsync.** `rsync -az --delete --delay-updates --exclude-from=.deployignore`.
   `.deployignore` excludes `.git/`, `.github/`, `.gitignore`, `docs/`, `scripts/`,
   `CLAUDE.md`, `.DS_Store`, `.htmlvalidate.json`, `.deployignore`.
   **`.htaccess` is explicitly not excluded** — a blanket dotfile exclude would drop
   it, so the exclude list is enumerated rather than pattern-based.

### Smoke test

Runs after rsync, in the same job, against the public URL — not against the
filesystem it just wrote, which would only prove rsync exited 0.

1. `GET $SITE_URL` → assert HTTP 200.
2. Assert the body contains a known string (`Home for Deranged Scientists`).
3. `GET $SITE_URL/build-info.json?_cb=<sha>` with `Cache-Control: no-cache` →
   parse with `jq` → **assert `.commit == github.sha`**.

Step 3 is the one that matters. Steps 1–2 pass just as happily against a stale
cached copy of last month's site; only the commit comparison distinguishes "a
website exists" from "my deploy landed." Retries with backoff for ~30 s absorb
host-side caching. `.htaccess` does not block `.json`, so `build-info.json` is
reachable — a rule change there would break verification and is worth a comment
in the file.

Failure of any step fails the workflow. Rollback is **manual and documented**, not
automatic: restore the most recent snapshot over SSH, or re-run
`workflow_dispatch` at the previous good commit.

## Secrets and variables

| Name | Kind | Purpose |
|---|---|---|
| `SSH_PRIVATE_KEY` | secret | Dedicated deploy key, not a personal key |
| `SSH_KNOWN_HOSTS` | secret | Pinned host key, captured and verified once |
| `SSH_HOST` | secret | Hostname |
| `SSH_USER` | secret | SSH user |
| `SSH_PORT` | secret | SSH port (default 22) |
| `DEPLOY_PATH` | secret | Absolute docroot path |
| `SITE_URL` | variable | Public URL for the smoke test |

A **dedicated keypair used only by this workflow** is recommended over reusing a
personal key, so revocation costs nothing. Restrict it on the server side where
the host allows it.

## Verification plan

The pipeline is not "done" when it goes green once. It is done when these have
been demonstrated, with output pasted into the PR:

- [ ] A real push to `main` deploys, and the smoke test's commit assertion passes.
- [ ] **Break the smoke test on purpose** (assert a string that is not on the page)
      and confirm the workflow goes red. A verification step that has never failed
      is not known to work.
- [ ] Point `SITE_URL` at a stale copy and confirm the commit assertion catches it.
- [ ] Delete a file, push, confirm it disappears from the live site (`--delete` works).
- [ ] Stage an 11-file deletion and confirm the blast-radius guard blocks it.
- [ ] Confirm preflight fails cleanly against a bogus `DEPLOY_PATH`.

## Non-goals

- No staging environment.
- No automatic rollback (manual, documented, snapshot-backed).
- No CDN, minification, or image optimization.
- No change to hosting, DNS, or `.htaccess` behavior.

## Open items to supply at setup

- Live URL for `SITE_URL`.
- Absolute docroot path for `DEPLOY_PATH`.
- Confirmation the host permits a dedicated SSH key.

None of these block writing the pipeline; all are filled in as GitHub
secrets/variables, so none land in the repo.

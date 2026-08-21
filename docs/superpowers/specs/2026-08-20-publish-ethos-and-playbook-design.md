# Publishing the Ethos and the Playbook as Site Pages

**Date:** 2026-08-20
**Status:** Approved design, pending implementation plan
**Repo:** `homeforderangedscientists/hds_site` (public)

## Problem

Two documents that explain what the lab is and how it works —
`hfds-ethos.md` (303 lines) and `engineer-agent-playbook-v2.md` (1,724 lines) —
live only in the `groundskeeper` repo as markdown. The public site says what HDS
ships but not what it believes or how it works.

## Goal

Publish both documents as readable pages on the site, linked from the homepage,
without disturbing the deploy pipeline and without letting a published page
silently drift from its source.

## Constraints (established, not assumed)

- Both documents originate in the **separate `groundskeeper` repo**. Sync into
  this repo is **manual and deliberate** — chosen over submodules or cross-repo
  CI to keep the deploy self-contained.
- `.htaccess` blocks `.md` files (`RewriteRule \.md$ - [F,L]`), so raw markdown
  can never be served. Every page must be real HTML.
- The site has no build system and the deploy is a plain rsync of files already
  in git. **That must remain true** — the deploy pipeline was verified end to end
  on 2026-08-20 and this work must not add a build step to it.
- The site's palette is cream `#f5f3eb`, forest `#2d4a3e`, accent `#7fb069`,
  with muted greens `#4a6a5a` / `#5a7a6a` / `#6a8a7a`.
- **Verified:** `# CLAUDE.md` at playbook line 310 sits **inside a ```markdown
  fence** — it is a sample file shown as an example, not a section heading.
  Splitting on `^# ` without fence tracking invents a phantom page and truncates
  Part I mid-example.

## Approach

**Chosen: generate at author time, commit the HTML, gate on drift.**
A script renders markdown to HTML on the maintainer's machine; the HTML is
committed; CI re-runs the generator and fails if the committed output differs
from what the source produces. The deploy keeps rsyncing files that are already
in git.

**Rejected — build in CI, don't commit HTML:** would make the deploy depend on a
build step, complicating the `repo == docroot` model that the smoke test's
commit assertion relies on, and letting a generator failure block unrelated
deploys.

**Rejected — hand-authored HTML:** reasonable for the ethos alone, untenable for
nine playbook pages, and it makes every future doc edit a manual re-transcription
with no mechanical check that it was faithful.

## Page inventory

Verified section boundaries (fence-aware count): 10 top-level sections.

| URL | Source | Approx. lines |
|---|---|---|
| `/ethos/` | `content/hfds-ethos.md` (whole) | 303 |
| `/playbook/` | front matter — thesis, all rules at a glance, reader routing | 202 |
| `/playbook/foundations.html` | Part I — Foundations | 314 |
| `/playbook/working-together.html` | Part II — Working Together | 198 |
| `/playbook/when-it-goes-wrong.html` | Part III — When It Goes Wrong | 144 |
| `/playbook/leveling-up.html` | Part IV — Leveling Up | 225 |
| `/playbook/field-notes.html` | Part V — Field Notes from the Case Studies | 362 |
| `/playbook/coda.html` | Coda | 25 |
| `/playbook/appendix-a-agents.html` | Appendix A — If you are an agent reading this | 137 |
| `/playbook/appendix-b-glossary.html` | Appendix B — Glossary | 38 |
| `/playbook/appendix-c-case-studies.html` | Appendix C — About the case studies | 79 |

The ethos stays one page: at 303 lines it reads whole, and its clusters are
sections rather than chapters.

`/ethos/` and `/playbook/` are directories containing `index.html`, so Apache's
`DirectoryIndex` serves them without a visible filename. Part pages carry `.html`
rather than each becoming its own directory — nine extra directories buys nothing.

## Architecture

```
content/*.md            hand-copied snapshots (excluded from deploy)
        │
        ▼
scripts/build-pages.py  fence-aware split → npx marked@18.0.10 → heading ids
        │                → contents rail → shared template
        ▼
ethos/index.html        committed HTML, deployed as static files
playbook/*.html
assets/docs.css
```

### `scripts/build-pages.py`

Python 3 standard library only, matching `scripts/check-assets.py`. It owns
everything except markdown parsing itself:

1. **Fence-aware splitting.** Track ```-fence state; only `^# ` headings outside
   a fence are section boundaries. This is not defensive coding — the playbook
   contains exactly this case at line 310.
2. **Markdown → HTML** by invoking `npx --yes marked@18.0.10 -i <file>`, pinned
   exactly (the same discipline as `html-validate@9.7.1` in CI). Verified to
   handle every construct these documents use: GFM tables, `~~strikethrough~~`
   → `<del>`, fenced code with language classes, blockquotes, and Unicode
   (⭐ · —) passed through intact.
3. **Heading IDs.** marked emits no `id` attributes, so the script slugifies
   `<h1>`–`<h3>` text (lowercase, non-alphanumerics → hyphens, emoji stripped)
   and de-duplicates collisions with a numeric suffix. Anchors are what the
   contents rail links to.
4. **Contents rail** built from the same heading pass.
5. **Template wrap** — masthead, rail, body, prev/next, footer.

**CLI contract:**
- `build-pages.py` — regenerate all pages in place.
- `build-pages.py --check` — regenerate into a temp directory and diff against
  the committed output. Exit 0 if identical, exit 1 with a diff summary if not.
  Writes nothing.

### The drift gate

CI runs `build-pages.py --check`. Editing `content/` without rebuilding turns the
build red. This is the same principle as the deploy smoke test: a published
artifact must be provably derived from its source, not assumed to be.

The gate does **not** detect drift between `groundskeeper` and `content/` — that
boundary is manual by decision. The runbook records how to re-sync.

### Layout

A shared `assets/docs.css` serves all eleven generated pages (the ethos page plus the playbook's index and nine parts). `index.html` keeps its inline
CSS untouched — it is not part of this system and rewriting it is out of scope.

- Sticky contents rail, left, highlighting the current section.
- Body measure ~68 characters; serif body text; sans-serif headings matching the
  homepage's system stack.
- Below 768px the rail becomes a collapsed contents block above the content, and
  nothing is position-sticky.
- Playbook part pages carry previous/next links; every page links home and to its
  document's index.

### Homepage

A line from the ethos sits beneath the logo as the site's statement of purpose,
with both documents linked under it, above `Projects`. The existing Projects and
Contact sections are untouched apart from position.

## Accessibility

The ethos names **Access** as a standing aim ("an instrument may ship imperfect;
it may not settle there"), so these pages should honor it rather than merely
claim it:

- Real landmarks (`<nav aria-label>`, `<main>`), a skip-to-content link.
- Heading levels nested without skipping, driven by the source's own structure.
- Usable at 320px with no horizontal scrolling; wide tables scroll inside their
  own container rather than the page.
- Cluster emoji (⭐ 🧩 🛡 🌱 🔨 🧭) never carry meaning alone — they always sit
  beside the cluster's written name.
- Contrast, **measured against `#f5f3eb`** rather than assumed:

  | Colour | Ratio | Verdict |
  |---|---|---|
  | `#2d4a3e` forest | 8.75:1 | AA body text |
  | `#4a6a5a` muted | 5.40:1 | AA body text |
  | `#5a7a6a` muted | 4.27:1 | large text only (≥18.66px bold / 24px) |
  | `#6a8a7a` muted | 3.42:1 | large text only |
  | `#7fb069` accent | 2.27:1 | **fails AA — decoration only** |

  So body copy and contents-rail links use `#2d4a3e` or `#4a6a5a` only.
  `#7fb069` is restricted to borders, rules, and the active-item marker, never
  to text. `#5a7a6a` / `#6a8a7a` may be used for large display text only.
  (Note: the browser mockup used `#6a8a7a` for rail items; the built pages must
  not — the rail is small text.)

## CI

The existing `checks` job validates only `index.html`. It extends to:

- `html-validate` over every committed HTML page.
- `check-assets.py` over every committed HTML page.
- `build-pages.py --check` — the drift gate.

`check-assets.py` already handles root-relative paths (`/assets/docs.css`) and
fragment-only links (`#anchor`), both verified in its test suite. Its skip rules
mean the many external links in these documents are reported, never failed.

## Deploy

`content/` is added to `.deployignore`. `ethos/`, `playbook/`, and `assets/`
are **not** excluded and must reach the server.

Before merging, a real `rsync --dry-run` against the live docroot must confirm:
the new directories transfer, `content/` does not, and **nothing is deleted** —
the same verification that caught the `blog/` and `.well-known/` problem on
2026-08-20.

## Deliberate decision recorded

Publishing the playbook makes the lab's engineering practice public, including
six case studies of things that went wrong. This is the intent, not a side
effect, and is recorded here so it is a decision rather than a drift.

## Non-goals

- No search, no client-side JavaScript, no syntax highlighting.
- No automated sync from `groundskeeper`.
- No redesign of `index.html` beyond adding the new section.
- No print stylesheet, no dark mode, no RSS.

## Verification plan

Done when these are demonstrated, with output pasted:

- [ ] `build-pages.py` output contains no phantom `CLAUDE.md` page, and Part I
      ends where the source ends — the fence case is handled.
- [ ] Every heading anchor in a rail resolves to an element on that page.
- [ ] Round-trip: a table, a `~~strikethrough~~`, a fenced code block, and a
      blockquote each render correctly in the output.
- [ ] `build-pages.py --check` passes on committed output, and **fails** when a
      `content/` file is edited without rebuilding. A gate that has never failed
      is not known to work.
- [ ] `html-validate` and `check-assets.py` pass on all 12 committed pages
      (the 11 generated pages plus the existing `index.html`).
- [ ] Pages usable at 320px; no horizontal page scroll.
- [ ] Real rsync dry-run: new dirs transfer, `content/` excluded, zero deletions.

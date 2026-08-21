# Publish the Ethos and Playbook — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish `hfds-ethos.md` and `engineer-agent-playbook-v2.md` as eleven readable HTML pages linked from the homepage, generated from committed markdown and gated in CI against drift.

**Architecture:** Markdown snapshots live in `content/`. `scripts/build-pages.py` splits the playbook on top-level headings (skipping any inside code fences), shells out to `npx marked@18.0.10` for markdown parsing, injects slugified heading IDs, builds a contents rail, and wraps everything in a shared template. The generated HTML is committed, so the deploy stays a plain rsync of files already in git. CI re-runs the generator with `--check` and fails if committed output differs from source.

**Tech Stack:** Python 3 (standard library only), `npx marked@18.0.10`, plain CSS, no client-side JavaScript.

**Spec:** `docs/superpowers/specs/2026-08-20-publish-ethos-and-playbook-design.md`

## Global Constraints

- **Python: standard library only.** No pip installs. Matches `scripts/check-assets.py`.
- **`npx --yes marked@18.0.10`** — pinned exactly, never a range.
- **No client-side JavaScript** on any generated page. No external fonts, no CDN requests.
- **`.htaccess` must never be excluded** from deploy, and `content/` must be.
- **Colours** (measured against `#f5f3eb`): body text and contents-rail links use **only** `#2d4a3e` (8.75:1) or `#4a6a5a` (5.40:1). `#7fb069` (2.27:1) is **decoration only — never text**. `#5a7a6a` (4.27:1) and `#6a8a7a` (3.42:1) are large-display-text only.
- **Every bash step** starts with `set -euo pipefail`.
- **Fence awareness is mandatory**: `# CLAUDE.md` at playbook line 310 is inside a ```markdown fence. Any split that ignores fences is wrong.
- Generated pages must pass `html-validate@9.7.1` and `scripts/check-assets.py`.
- The site's existing `index.html` inline CSS is **not** refactored.

---

## File Structure

| File | Responsibility |
|---|---|
| `content/hfds-ethos.md` | Hand-synced snapshot from `groundskeeper` |
| `content/engineer-agent-playbook-v2.md` | Hand-synced snapshot from `groundskeeper` |
| `scripts/build_pages_lib.py` | Pure functions: fence-aware splitting, slugify, dedupe, heading-ID injection, TOC extraction. No I/O, no subprocess. |
| `scripts/build-pages.py` | CLI: orchestration, `npx marked` invocation, templating, file writing, `--check` |
| `scripts/test-build-pages.py` | `unittest` suite for `build_pages_lib.py` |
| `assets/docs.css` | Shared stylesheet for all generated pages |
| `ethos/index.html` | Generated |
| `playbook/index.html` + 9 part pages | Generated |
| `index.html` | Modified: new section above Projects |
| `.deployignore` | Modified: exclude `content/` |
| `.github/workflows/deploy.yml` | Modified: extend checks |
| `docs/DEPLOY.md` | Modified: how to re-sync from groundskeeper |

Pure logic lives in `build_pages_lib.py` so it is unit-testable without running `npx` or touching the filesystem. The CLI wrapper owns everything impure.

---

### Task 1: Content snapshots and deploy exclusion

**Files:**
- Create: `content/hfds-ethos.md`, `content/engineer-agent-playbook-v2.md`
- Modify: `.deployignore`

**Interfaces:**
- Produces: `content/*.md` — the source of truth inside this repo. Later tasks read these paths.

- [ ] **Step 1: Copy the snapshots**

```bash
set -euo pipefail
mkdir -p content
cp ../groundskeeper/docs/hfds-ethos.md content/
cp ../groundskeeper/docs/engineer-agent-playbook-v2.md content/
wc -l content/*.md
```

Expected: `303 content/hfds-ethos.md` and `1724 content/engineer-agent-playbook-v2.md` (line counts may differ if the source has changed; record what you actually got).

- [ ] **Step 2: Exclude content/ from deploy**

Add `content/` to `.deployignore` in the **first** group (repo-internal paths), immediately after `docs/`. Do not touch the "Server-managed paths" group.

- [ ] **Step 3: Verify the exclusion and the .htaccess invariant**

```bash
set -euo pipefail
echo "htaccess in pattern lines: $(grep -vE '^\s*(#|$)' .deployignore | grep -c 'htaccess')"
rsync -avn --delete --exclude-from=.deployignore ./ /tmp/dp-t1/ 2>/dev/null | grep -E '^content/' && echo "FAIL: content/ would deploy" || echo "OK: content/ excluded"
rsync -avn --delete --exclude-from=.deployignore ./ /tmp/dp-t1/ 2>/dev/null | grep -E '^\.htaccess$' && echo "OK: .htaccess still transfers"
```

Expected: `htaccess in pattern lines: 0`, `OK: content/ excluded`, `OK: .htaccess still transfers`.

- [ ] **Step 4: Commit**

```bash
git add content .deployignore
git commit -m "content: add ethos and playbook snapshots, exclude from deploy"
```

---

### Task 2: Pure text functions — fence-aware split, slugs

**Files:**
- Create: `scripts/build_pages_lib.py`
- Create: `scripts/test-build-pages.py`

**Interfaces:**
- Produces:
  - `split_sections(md: str) -> list[tuple[str, str]]` — returns `(title, body)` pairs. `title` is the heading text without `# `. `body` is the full markdown for that section **including** its heading line. Text before the first top-level heading is returned as a leading section titled `""`. Headings inside ``` fences are ignored.
  - `slugify(text: str) -> str` — lowercase; strips HTML tags, emoji and punctuation; spaces and separators become single hyphens; no leading/trailing hyphen. Returns `"section"` if nothing survives.
  - `dedupe_slugs(slugs: list[str]) -> list[str]` — appends `-2`, `-3`, … to repeats, preserving order.

- [ ] **Step 1: Write the failing tests**

```python
cat > scripts/test-build-pages.py <<'EOF'
#!/usr/bin/env python3
"""Unit tests for build_pages_lib. Run: python3 scripts/test-build-pages.py"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_pages_lib import split_sections, slugify, dedupe_slugs, add_heading_ids


class TestSplitSections(unittest.TestCase):
    def test_splits_on_top_level_headings(self):
        md = "# One\n\nalpha\n\n# Two\n\nbeta\n"
        got = split_sections(md)
        self.assertEqual([t for t, _ in got], ["One", "Two"])
        self.assertIn("alpha", got[0][1])
        self.assertTrue(got[0][1].startswith("# One"))

    def test_ignores_headings_inside_code_fences(self):
        # This is the real playbook case: a sample CLAUDE.md shown as an example.
        md = (
            "# Part I\n\nprose\n\n"
            "```markdown\n"
            "# CLAUDE.md\n"
            "\n"
            "## Project Status\n"
            "```\n\n"
            "more prose\n\n"
            "# Part II\n\nbeta\n"
        )
        got = split_sections(md)
        self.assertEqual([t for t, _ in got], ["Part I", "Part II"])
        self.assertIn("# CLAUDE.md", got[0][1])
        self.assertIn("more prose", got[0][1])

    def test_preamble_before_first_heading_is_its_own_section(self):
        md = "intro line\n\n# One\n\nalpha\n"
        got = split_sections(md)
        self.assertEqual(got[0][0], "")
        self.assertIn("intro line", got[0][1])
        self.assertEqual(got[1][0], "One")

    def test_h2_is_not_a_split_point(self):
        md = "# One\n\n## Two\n\nalpha\n"
        self.assertEqual(len(split_sections(md)), 1)

    def test_tilde_fences_are_also_respected(self):
        md = "# One\n\n~~~\n# Not A Heading\n~~~\n\n# Two\n"
        self.assertEqual([t for t, _ in split_sections(md)], ["One", "Two"])


class TestSlugify(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(slugify("The Cardinal Pair"), "the-cardinal-pair")

    def test_strips_emoji(self):
        self.assertEqual(slugify("⭐ The Cardinal Pair"), "the-cardinal-pair")

    def test_strips_html_tags(self):
        self.assertEqual(slugify("Ask <em>before</em> you diagnose"),
                         "ask-before-you-diagnose")

    def test_punctuation_and_separators(self):
        self.assertEqual(slugify("Part I — Foundations"), "part-i-foundations")
        self.assertEqual(slugify("Rule: Don't guess."), "rule-dont-guess")

    def test_collapses_and_trims_hyphens(self):
        self.assertEqual(slugify("  A  ·  B  "), "a-b")

    def test_empty_input_gets_fallback(self):
        self.assertEqual(slugify("⭐⭐⭐"), "section")


class TestDedupeSlugs(unittest.TestCase):
    def test_appends_numeric_suffixes(self):
        self.assertEqual(dedupe_slugs(["a", "a", "b", "a"]),
                         ["a", "a-2", "b", "a-3"])

    def test_leaves_unique_alone(self):
        self.assertEqual(dedupe_slugs(["a", "b"]), ["a", "b"])


class TestAddHeadingIds(unittest.TestCase):
    def test_injects_ids_and_returns_toc(self):
        html, toc = add_heading_ids("<h2>The Purpose</h2>\n<p>x</p>\n<h3>Edges</h3>")
        self.assertIn('<h2 id="the-purpose">The Purpose</h2>', html)
        self.assertIn('<h3 id="edges">Edges</h3>', html)
        self.assertEqual(toc, [(2, "the-purpose", "The Purpose"),
                               (3, "edges", "Edges")])

    def test_keeps_inline_markup_in_the_heading_but_not_the_slug(self):
        html, toc = add_heading_ids("<h2>Ask <em>before</em> you diagnose</h2>")
        self.assertIn('id="ask-before-you-diagnose"', html)
        self.assertIn("<em>before</em>", html)
        self.assertEqual(toc[0][2], "Ask before you diagnose")

    def test_dedupes_repeated_headings(self):
        html, toc = add_heading_ids("<h2>Notes</h2><h2>Notes</h2>")
        self.assertIn('id="notes"', html)
        self.assertIn('id="notes-2"', html)
        self.assertEqual([t[1] for t in toc], ["notes", "notes-2"])

    def test_ignores_h4_and_below(self):
        html, toc = add_heading_ids("<h4>Deep</h4>")
        self.assertEqual(toc, [])
        self.assertEqual(html, "<h4>Deep</h4>")


if __name__ == "__main__":
    unittest.main(verbosity=2)
EOF
chmod +x scripts/test-build-pages.py
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 scripts/test-build-pages.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'build_pages_lib'`.

- [ ] **Step 3: Write the implementation**

```python
cat > scripts/build_pages_lib.py <<'EOF'
#!/usr/bin/env python3
"""Pure text helpers for build-pages.py.

No file I/O and no subprocesses live here, so every function is unit-testable
in isolation. The CLI wrapper owns everything impure.
"""
import re

FENCE_RE = re.compile(r"^(```|~~~)")
TOP_HEADING_RE = re.compile(r"^# (.+)$")
HEADING_TAG_RE = re.compile(r"<h([123])>(.*?)</h\1>", re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")


def split_sections(md):
    """Split markdown on top-level '# ' headings that are outside code fences.

    Returns [(title, body_markdown), ...]. The body INCLUDES its heading line.
    Any text before the first top-level heading becomes a leading section whose
    title is the empty string.

    Fence tracking is not defensive politeness: the playbook embeds a sample
    CLAUDE.md inside a ```markdown fence, and its '# CLAUDE.md' line would
    otherwise be read as a section boundary -- inventing a page and truncating
    the section it sits in.
    """
    lines = md.splitlines()
    in_fence = False
    starts = []  # (line_index, title)
    for i, line in enumerate(lines):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = TOP_HEADING_RE.match(line)
        if m:
            starts.append((i, m.group(1).strip()))

    sections = []
    if not starts:
        return [("", md)]
    if starts[0][0] > 0:
        sections.append(("", "\n".join(lines[: starts[0][0]]).strip() + "\n"))
    for n, (idx, title) in enumerate(starts):
        end = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        sections.append((title, "\n".join(lines[idx:end]).strip() + "\n"))
    return sections


def slugify(text):
    """Lowercase ASCII slug: strips tags, emoji and punctuation."""
    text = TAG_RE.sub("", text)
    text = text.lower()
    text = re.sub(r"[’'`]", "", text)          # don't -> dont
    text = re.sub(r"[^a-z0-9]+", "-", text)    # everything else -> hyphen
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "section"


def dedupe_slugs(slugs):
    """Append -2, -3 ... to repeated slugs, preserving order."""
    seen = {}
    out = []
    for s in slugs:
        if s in seen:
            seen[s] += 1
            out.append(f"{s}-{seen[s]}")
        else:
            seen[s] = 1
            out.append(s)
    return out


def add_heading_ids(html_fragment):
    """Inject id attributes into h1-h3 and return (html, toc).

    toc is [(level:int, slug:str, plain_text:str), ...]. Inline markup inside a
    heading is preserved in the HTML but stripped for the slug and the TOC text.
    """
    matches = list(HEADING_TAG_RE.finditer(html_fragment))
    raw_slugs = [slugify(m.group(2)) for m in matches]
    slugs = dedupe_slugs(raw_slugs)

    toc = []
    out = []
    last = 0
    for m, slug in zip(matches, slugs):
        level = int(m.group(1))
        inner = m.group(2)
        plain = re.sub(r"\s+", " ", TAG_RE.sub("", inner)).strip()
        out.append(html_fragment[last:m.start()])
        out.append(f'<h{level} id="{slug}">{inner}</h{level}>')
        last = m.end()
        toc.append((level, slug, plain))
    out.append(html_fragment[last:])
    return "".join(out), toc
EOF
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 scripts/test-build-pages.py`
Expected: PASS — `OK`, 16 tests.

- [ ] **Step 5: Prove the fence case against the real document**

```bash
set -euo pipefail
python3 -c "
import sys; sys.path.insert(0,'scripts')
from build_pages_lib import split_sections
secs = split_sections(open('content/engineer-agent-playbook-v2.md').read())
print(f'sections: {len(secs)}')
for t,_ in secs: print('  ', t[:60])
assert not any(t == 'CLAUDE.md' for t,_ in secs), 'FAIL: fenced heading became a section'
print('OK: no phantom CLAUDE.md section')
"
```

Expected: 10 sections (one untitled front-matter section plus 9 real ones — note the playbook's own title line `# The Engineer + Agent Playbook — Second Edition` is itself a top-level heading, so the front matter arrives as a *titled* section, not an empty one; record the actual list), and `OK: no phantom CLAUDE.md section`.

- [ ] **Step 6: Commit**

```bash
git add scripts/build_pages_lib.py scripts/test-build-pages.py
git commit -m "feat: add fence-aware markdown splitting and slug helpers"
```

---

### Task 3: Markdown rendering via marked

**Files:**
- Modify: `scripts/build_pages_lib.py` (no change — this task only consumes it)
- Create: `scripts/build-pages.py` (rendering portion only)

**Interfaces:**
- Consumes: `split_sections`, `add_heading_ids` from Task 2.
- Produces: `render_markdown(md: str) -> str` in `scripts/build-pages.py` — writes markdown to a temp file, runs `npx --yes marked@18.0.10 -i <file>`, returns the HTML fragment. Raises `SystemExit` with a clear message if marked fails.

- [ ] **Step 1: Create the CLI skeleton with rendering only**

```python
cat > scripts/build-pages.py <<'EOF'
#!/usr/bin/env python3
"""Render content/*.md into committed HTML pages.

Usage:
  build-pages.py            regenerate all pages in place
  build-pages.py --check    regenerate to a temp dir and diff; write nothing
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_pages_lib import add_heading_ids, slugify, split_sections  # noqa: E402

MARKED = "marked@18.0.10"
ROOT = Path(__file__).resolve().parent.parent


def render_markdown(md):
    """Markdown -> HTML fragment via the pinned marked CLI."""
    with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8",
                                     delete=False) as fh:
        fh.write(md)
        tmp = fh.name
    try:
        proc = subprocess.run(
            ["npx", "--yes", MARKED, "-i", tmp],
            capture_output=True, text=True,
        )
    finally:
        Path(tmp).unlink(missing_ok=True)
    if proc.returncode != 0:
        sys.exit(f"FAIL: {MARKED} exited {proc.returncode}\n{proc.stderr}")
    return proc.stdout
EOF
chmod +x scripts/build-pages.py
```

- [ ] **Step 2: Verify rendering handles every construct these documents use**

```bash
set -euo pipefail
python3 -c "
import sys; sys.path.insert(0,'scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('bp','scripts/build-pages.py')
bp = importlib.util.module_from_spec(spec); spec.loader.exec_module(bp)
md = '''| A | B |
|---|---|
| x | y |

~~struck~~ and **bold** and \`code\`

> quote

\`\`\`bash
echo hi
\`\`\`
'''
out = bp.render_markdown(md)
for needle in ['<table>', '<del>struck</del>', '<strong>bold</strong>',
               '<blockquote>', 'language-bash']:
    assert needle in out, f'MISSING {needle}'
print('OK: tables, strikethrough, bold, blockquote, fenced code all render')
"
```

Expected: `OK: tables, strikethrough, bold, blockquote, fenced code all render`.

- [ ] **Step 3: Verify it fails loudly on a marked error**

```bash
set -euo pipefail
python3 -c "
import sys; sys.path.insert(0,'scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('bp','scripts/build-pages.py')
bp = importlib.util.module_from_spec(spec); spec.loader.exec_module(bp)
bp.MARKED = 'marked@0.0.0-nonexistent'
try:
    bp.render_markdown('# x')
    print('FAIL: should have exited')
except SystemExit as e:
    print('OK: exits with message ->', str(e).splitlines()[0])
"
```

Expected: `OK: exits with message -> FAIL: marked@0.0.0-nonexistent exited 1`.

- [ ] **Step 4: Commit**

```bash
git add scripts/build-pages.py
git commit -m "feat: add pinned marked rendering to page builder"
```

---

### Task 4: Page template and full generation

**Files:**
- Modify: `scripts/build-pages.py`
- Create (generated): `ethos/index.html`, `playbook/index.html`, `playbook/foundations.html`, `playbook/working-together.html`, `playbook/when-it-goes-wrong.html`, `playbook/leveling-up.html`, `playbook/field-notes.html`, `playbook/coda.html`, `playbook/appendix-a-agents.html`, `playbook/appendix-b-glossary.html`, `playbook/appendix-c-case-studies.html`

**Interfaces:**
- Consumes: `render_markdown` (Task 3), `split_sections` / `add_heading_ids` (Task 2).
- Produces: `build_all(out_root: Path) -> list[Path]` — writes every page under `out_root` and returns the paths written, relative to `out_root`. Task 5's `--check` calls this with a temp directory.

- [ ] **Step 1: Add the page model, template and build_all**

Append to `scripts/build-pages.py`:

```python
cat >> scripts/build-pages.py <<'PYEOF'


# Playbook section title -> output filename. Titles are matched by their
# leading text so a subtitle change after the em-dash does not break the build.
PLAYBOOK_PAGES = [
    ("Part I", "foundations.html", "Part I — Foundations"),
    ("Part II", "working-together.html", "Part II — Working Together"),
    ("Part III", "when-it-goes-wrong.html", "Part III — When It Goes Wrong"),
    ("Part IV", "leveling-up.html", "Part IV — Leveling Up"),
    ("Part V", "field-notes.html", "Part V — Field Notes"),
    ("Coda", "coda.html", "Coda"),
    ("Appendix A", "appendix-a-agents.html", "Appendix A — For Agents"),
    ("Appendix B", "appendix-b-glossary.html", "Appendix B — Glossary"),
    ("Appendix C", "appendix-c-case-studies.html", "Appendix C — Case Studies"),
]

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Home for Deranged Scientists</title>
<meta name="description" content="{description}">
<link rel="stylesheet" href="{css_path}">
</head>
<body>
<a class="skip-link" href="#content">Skip to content</a>
<div class="doc-layout">
<nav class="doc-rail" aria-label="Contents">
<a class="doc-home" href="{home_path}">&larr; Home for Deranged Scientists</a>
{rail_title}
<h2 class="rail-heading">Contents</h2>
<ol class="rail-list">
{rail_items}
</ol>
</nav>
<main class="doc-main" id="content">
<header class="doc-masthead">
<p class="doc-eyebrow">{eyebrow}</p>
<h1 class="doc-title">{title}</h1>
<p class="doc-meta">{meta}</p>
</header>
<div class="doc-body">
{body}
</div>
{pager}
<footer class="doc-footer">
<p>{footer_note}</p>
<p>&copy; 2026 Home for Deranged Scientists</p>
</footer>
</main>
</div>
</body>
</html>
"""


def esc(text):
    """Escape for use in an HTML attribute or text node."""
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def build_rail(toc):
    """Contents rail markup from a TOC list."""
    items = []
    for level, slug, text in toc:
        if level > 3:
            continue
        items.append(f'<li class="rail-l{level}"><a href="#{slug}">{esc(text)}</a></li>')
    return "\n".join(items) if items else '<li class="rail-l2">(no sections)</li>'


def build_pager(prev_link, next_link):
    if not prev_link and not next_link:
        return ""
    parts = ['<nav class="doc-pager" aria-label="Document sections">']
    if prev_link:
        parts.append(f'<a class="pager-prev" href="{prev_link[0]}">'
                     f'<span class="pager-dir">Previous</span>'
                     f'<span class="pager-name">{esc(prev_link[1])}</span></a>')
    if next_link:
        parts.append(f'<a class="pager-next" href="{next_link[0]}">'
                     f'<span class="pager-dir">Next</span>'
                     f'<span class="pager-name">{esc(next_link[1])}</span></a>')
    parts.append("</nav>")
    return "\n".join(parts)


def write_page(out_path, **kw):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(PAGE_TEMPLATE.format(**kw), encoding="utf-8")


def build_ethos(out_root):
    md = (ROOT / "content" / "hfds-ethos.md").read_text(encoding="utf-8")
    body, toc = add_heading_ids(render_markdown(md))
    out = out_root / "ethos" / "index.html"
    write_page(
        out,
        title="The HFDS Ethos",
        description="The thirteen tenets Home for Deranged Scientists builds by.",
        css_path="../assets/docs.css",
        home_path="../",
        rail_title="",
        rail_items=build_rail(toc),
        eyebrow="Home for Deranged Scientists",
        meta="Thirteen tenets in five clusters",
        body=body,
        pager="",
        footer_note='This document is the lab&rsquo;s constitution. '
                    'Instruments are tested against it.',
    )
    return [Path("ethos/index.html")]


def build_playbook(out_root):
    md = (ROOT / "content" / "engineer-agent-playbook-v2.md").read_text(encoding="utf-8")
    sections = split_sections(md)

    # Map each configured page to its section; anything unmatched (the title
    # block and its front matter) becomes the playbook index.
    by_prefix = {}
    front = []
    for title, section_md in sections:
        match = next((p for p in PLAYBOOK_PAGES if title.startswith(p[0])), None)
        if match:
            by_prefix[match[1]] = (match[2], section_md)
        else:
            front.append(section_md)

    missing = [p[1] for p in PLAYBOOK_PAGES if p[1] not in by_prefix]
    if missing:
        sys.exit(f"FAIL: no source section matched these pages: {missing}\n"
                 f"      Section titles found: {[t for t, _ in sections]}")

    written = []
    order = [p[1] for p in PLAYBOOK_PAGES]

    # Index page from the front matter.
    body, toc = add_heading_ids(render_markdown("\n\n".join(front)))
    nav_items = "\n".join(
        f'<li class="rail-l2"><a href="{fn}">{esc(by_prefix[fn][0])}</a></li>'
        for fn in order
    )
    write_page(
        out_root / "playbook" / "index.html",
        title="The Engineer + Agent Playbook",
        description="Seventy-one rules for working with coding agents, "
                    "drawn from six case studies.",
        css_path="../assets/docs.css",
        home_path="../",
        rail_title=f'<h2 class="rail-heading">Parts</h2>\n<ol class="rail-list">\n{nav_items}\n</ol>',
        rail_items=build_rail(toc),
        eyebrow="Home for Deranged Scientists",
        meta="Second edition &middot; 71 rules &middot; 6 case studies",
        body=body,
        pager=build_pager(None, (order[0], by_prefix[order[0]][0])),
        footer_note='How the work actually gets done.',
    )
    written.append(Path("playbook/index.html"))

    for i, fn in enumerate(order):
        label, section_md = by_prefix[fn]
        body, toc = add_heading_ids(render_markdown(section_md))
        prev_link = (order[i - 1], by_prefix[order[i - 1]][0]) if i > 0 else ("index.html", "Playbook contents")
        next_link = (order[i + 1], by_prefix[order[i + 1]][0]) if i + 1 < len(order) else None
        write_page(
            out_root / "playbook" / fn,
            title=label,
            description=f"{label} of the Engineer + Agent Playbook.",
            css_path="../assets/docs.css",
            home_path="../",
            rail_title=f'<p class="rail-doc"><a href="index.html">The Engineer + Agent Playbook</a></p>',
            rail_items=build_rail(toc),
            eyebrow="The Engineer + Agent Playbook",
            meta=label,
            body=body,
            pager=build_pager(prev_link, next_link),
            footer_note='Part of the Engineer + Agent Playbook.',
        )
        written.append(Path("playbook") / fn)
    return written


def build_all(out_root):
    return build_ethos(out_root) + build_playbook(out_root)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="regenerate to a temp dir and diff; write nothing")
    args = ap.parse_args()
    if args.check:
        return check()
    written = build_all(ROOT)
    for p in written:
        print(f"  wrote {p}")
    print(f"{len(written)} pages generated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF
```

- [ ] **Step 2: Build and inspect the output**

Run: `python3 scripts/build-pages.py`
Expected: 11 lines of `wrote …` then `11 pages generated`. This will fail with `NameError: name 'check' is not defined` only if `--check` is passed — that function arrives in Task 5, and a plain build must not touch it.

- [ ] **Step 3: Verify the fence case did not create a phantom page and content is complete**

```bash
set -euo pipefail
ls playbook/
test ! -f playbook/claude-md.html && echo "OK: no phantom CLAUDE.md page"
grep -c 'CLAUDE.md' playbook/foundations.html | sed 's/^/CLAUDE.md mentions inside Part I: /'
grep -q 'Skills are for procedures' playbook/foundations.html && echo "OK: Part I content continues past the fenced example"
```

Expected: nine part pages plus `index.html`; `OK: no phantom CLAUDE.md page`; a non-zero mention count; `OK: Part I content continues past the fenced example`.

- [ ] **Step 4: Verify every rail anchor resolves on its own page**

```bash
set -euo pipefail
python3 - <<'PY'
import re, pathlib, sys
bad = 0
for p in list(pathlib.Path('.').glob('playbook/*.html')) + [pathlib.Path('ethos/index.html')]:
    html = p.read_text(encoding='utf-8')
    ids = set(re.findall(r'<h[123] id="([^"]+)"', html))
    anchors = set(re.findall(r'href="#([^"]+)"', html))
    missing = anchors - ids
    if missing:
        bad += 1
        print(f"  {p}: {len(missing)} dangling anchors -> {sorted(missing)[:5]}")
print("OK: every in-page anchor resolves" if not bad else f"FAIL: {bad} page(s) with dangling anchors")
sys.exit(1 if bad else 0)
PY
```

Expected: `OK: every in-page anchor resolves`.

- [ ] **Step 5: Commit**

```bash
git add scripts/build-pages.py ethos playbook
git commit -m "feat: generate ethos and playbook pages from markdown"
```

---

### Task 5: The drift gate

**Files:**
- Modify: `scripts/build-pages.py`

**Interfaces:**
- Consumes: `build_all` (Task 4).
- Produces: `check() -> int` — regenerates into a temp directory, compares byte-for-byte against committed output, returns 0 if identical and 1 with a summary otherwise. Writes nothing into the repo.

- [ ] **Step 1: Add the check function**

Insert into `scripts/build-pages.py` immediately **before** `def main():`:

```python
def check():
    """Regenerate into a temp dir and diff against committed output."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        (tmp_root / "content").symlink_to(ROOT / "content")
        written = build_all(tmp_root)
        differing, missing = [], []
        for rel in written:
            committed = ROOT / rel
            fresh = tmp_root / rel
            if not committed.exists():
                missing.append(rel)
            elif committed.read_bytes() != fresh.read_bytes():
                differing.append(rel)
    if not differing and not missing:
        print(f"OK: all {len(written)} generated pages match their source")
        return 0
    print("FAIL: committed pages do not match content/", file=sys.stderr)
    for rel in missing:
        print(f"  missing:   {rel}", file=sys.stderr)
    for rel in differing:
        print(f"  differs:   {rel}", file=sys.stderr)
    print("\n  Run: python3 scripts/build-pages.py   then commit the result.",
          file=sys.stderr)
    return 1
```

Note: `build_all` reads sources via the module-level `ROOT`, so the symlink is belt-and-braces — it keeps the temp tree self-describing if `build_all` ever takes its input path from `out_root`.

- [ ] **Step 2: Verify the gate passes on clean output**

Run: `python3 scripts/build-pages.py --check; echo "exit=$?"`
Expected: `OK: all 11 generated pages match their source` and `exit=0`.

- [ ] **Step 3: Prove the gate FAILS when source changes without a rebuild**

A gate that has never failed is not known to work.

```bash
set -euo pipefail
cp content/hfds-ethos.md /tmp/ethos.bak
printf '\n\nA sentence added without rebuilding.\n' >> content/hfds-ethos.md
python3 scripts/build-pages.py --check; echo "exit=$? (want 1)"
cp /tmp/ethos.bak content/hfds-ethos.md
python3 scripts/build-pages.py --check; echo "exit=$? (want 0)"
```

Expected: first run prints `differs:   ethos/index.html` and `exit=1`; after restoring, `exit=0`.

- [ ] **Step 4: Prove it fails when a generated page is edited by hand**

```bash
set -euo pipefail
cp ethos/index.html /tmp/ethos-page.bak
printf '<!-- hand edit -->\n' >> ethos/index.html
python3 scripts/build-pages.py --check; echo "exit=$? (want 1)"
cp /tmp/ethos-page.bak ethos/index.html
python3 scripts/build-pages.py --check; echo "exit=$? (want 0)"
```

Expected: `exit=1` then `exit=0`.

- [ ] **Step 5: Commit**

```bash
git add scripts/build-pages.py
git commit -m "feat: add --check drift gate for generated pages"
```

---

### Task 6: The stylesheet

**Files:**
- Create: `assets/docs.css`

**Interfaces:**
- Consumes: the class names emitted by `PAGE_TEMPLATE` in Task 4 — `skip-link`, `doc-layout`, `doc-rail`, `doc-home`, `rail-heading`, `rail-list`, `rail-l1`/`rail-l2`/`rail-l3`, `rail-doc`, `doc-main`, `doc-masthead`, `doc-eyebrow`, `doc-title`, `doc-meta`, `doc-body`, `doc-pager`, `pager-prev`, `pager-next`, `pager-dir`, `pager-name`, `doc-footer`.

- [ ] **Step 1: Write the stylesheet**

```bash
cat > assets/docs.css <<'CSSEOF'
/* Shared stylesheet for the generated document pages.
   index.html keeps its own inline CSS and is deliberately untouched.

   Colour rules, measured against #f5f3eb:
     #2d4a3e  8.75:1  body text OK
     #4a6a5a  5.40:1  body text OK
     #5a7a6a  4.27:1  LARGE text only
     #6a8a7a  3.42:1  LARGE text only
     #7fb069  2.27:1  DECORATION ONLY - never text
*/

:root {
  --bg: #f5f3eb;
  --ink: #2d4a3e;
  --ink-soft: #4a6a5a;
  --accent: #7fb069;
  --rule: #d9d5c6;
  --panel: #f9f9f7;
  --measure: 68ch;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  background: var(--bg);
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  line-height: 1.6;
}

.skip-link {
  position: absolute; left: -9999px;
  background: var(--ink); color: var(--bg);
  padding: 0.6rem 1rem; z-index: 10;
}
.skip-link:focus { left: 1rem; top: 1rem; }

a { color: var(--ink); text-underline-offset: 0.15em; }
a:hover { color: var(--ink-soft); }
:focus-visible { outline: 2px solid var(--ink); outline-offset: 2px; }

/* ---- layout ---- */
.doc-layout {
  display: grid;
  grid-template-columns: minmax(210px, 250px) minmax(0, 1fr);
  gap: 3rem;
  max-width: 1180px;
  margin: 0 auto;
  padding: 2rem 1.5rem 4rem;
  align-items: start;
}

.doc-rail {
  position: sticky;
  top: 2rem;
  max-height: calc(100vh - 4rem);
  overflow-y: auto;
  font-size: 0.85rem;
  border-right: 1px solid var(--rule);
  padding-right: 1.25rem;
}
.doc-home, .rail-doc a {
  display: block;
  color: var(--ink-soft);
  text-decoration: none;
  font-size: 0.8rem;
  margin-bottom: 1.25rem;
}
.doc-home:hover, .rail-doc a:hover { text-decoration: underline; }
.rail-doc { margin-bottom: 1.25rem; font-weight: 600; }
.rail-heading {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--ink-soft);
  margin-bottom: 0.6rem;
  font-weight: 700;
}
.rail-list { list-style: none; margin-bottom: 1.75rem; }
.rail-list li { margin: 0.3rem 0; line-height: 1.4; }
.rail-list a { color: var(--ink-soft); text-decoration: none; }
.rail-list a:hover { color: var(--ink); text-decoration: underline; }
.rail-l1 { font-weight: 700; margin-top: 0.9rem !important; }
.rail-l1 a { color: var(--ink); }
.rail-l3 { padding-left: 0.85rem; font-size: 0.95em; }

/* ---- masthead ---- */
.doc-main { min-width: 0; }
.doc-masthead { border-bottom: 2px solid var(--accent); padding-bottom: 1.25rem; margin-bottom: 2rem; }
.doc-eyebrow {
  font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.16em;
  color: var(--ink-soft); font-weight: 700;
}
.doc-title {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: clamp(1.8rem, 4vw, 2.6rem);
  line-height: 1.15; margin: 0.5rem 0 0.35rem; font-weight: 400;
}
.doc-meta { color: var(--ink-soft); font-size: 0.9rem; }

/* ---- body ---- */
.doc-body { max-width: var(--measure); font-family: Georgia, 'Times New Roman', serif; font-size: 1.05rem; line-height: 1.75; color: #3d5a4c; }
.doc-body h1, .doc-body h2, .doc-body h3 {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: var(--ink); line-height: 1.25; scroll-margin-top: 1.5rem;
}
.doc-body h1 { font-size: 1.7rem; margin: 3rem 0 1rem; padding-top: 1.5rem; border-top: 1px solid var(--rule); }
.doc-body h2 { font-size: 1.3rem; margin: 2.25rem 0 0.75rem; }
.doc-body h3 { font-size: 1.05rem; margin: 1.75rem 0 0.5rem; }
.doc-body p, .doc-body ul, .doc-body ol { margin-bottom: 1.1rem; }
.doc-body ul, .doc-body ol { padding-left: 1.4rem; }
.doc-body li { margin-bottom: 0.4rem; }
.doc-body strong { color: var(--ink); }
.doc-body hr { border: 0; border-top: 1px solid var(--rule); margin: 2.5rem 0; }

.doc-body blockquote {
  border-left: 3px solid var(--accent);
  padding: 0.2rem 0 0.2rem 1.1rem;
  margin: 1.5rem 0;
  color: var(--ink-soft);
}
.doc-body blockquote p:last-child { margin-bottom: 0; }

.doc-body code {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.88em; background: var(--panel);
  border: 1px solid var(--rule); border-radius: 3px; padding: 0.1em 0.35em;
}
.doc-body pre {
  background: var(--panel); border: 1px solid var(--rule); border-radius: 5px;
  padding: 1rem; overflow-x: auto; margin-bottom: 1.25rem;
}
.doc-body pre code { background: none; border: 0; padding: 0; font-size: 0.85rem; }

/* Wide tables scroll inside their own box, never the page. */
.doc-body table {
  display: block; overflow-x: auto; max-width: 100%;
  border-collapse: collapse; margin-bottom: 1.5rem; font-size: 0.92rem;
  font-family: -apple-system, BlinkMacSystemFont, sans-serif;
}
.doc-body th, .doc-body td {
  border: 1px solid var(--rule); padding: 0.5rem 0.7rem;
  text-align: left; vertical-align: top;
}
.doc-body th { background: var(--panel); color: var(--ink); font-weight: 700; }

/* ---- pager and footer ---- */
.doc-pager {
  display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap;
  border-top: 1px solid var(--rule); margin-top: 3rem; padding-top: 1.25rem;
}
.doc-pager a { text-decoration: none; max-width: 46%; }
.pager-next { margin-left: auto; text-align: right; }
.pager-dir {
  display: block; font-size: 0.7rem; text-transform: uppercase;
  letter-spacing: 0.12em; color: var(--ink-soft); font-weight: 700;
}
.pager-name { display: block; color: var(--ink); }
.doc-pager a:hover .pager-name { text-decoration: underline; }
.doc-footer {
  border-top: 1px solid var(--rule); margin-top: 3rem; padding-top: 1.25rem;
  font-size: 0.85rem; color: var(--ink-soft);
}
.doc-footer p { margin-bottom: 0.3rem; }

/* ---- narrow screens: rail becomes a contents block, nothing sticks ---- */
@media (max-width: 768px) {
  .doc-layout { grid-template-columns: 1fr; gap: 1.75rem; padding: 1.25rem 1rem 3rem; }
  .doc-rail {
    position: static; max-height: none; overflow: visible;
    border-right: 0; border-bottom: 1px solid var(--rule);
    padding-right: 0; padding-bottom: 1.25rem;
  }
  .doc-body { font-size: 1rem; }
}

@media (prefers-reduced-motion: reduce) {
  * { scroll-behavior: auto !important; }
}
CSSEOF
```

- [ ] **Step 2: Verify no disallowed colour is used for text**

```bash
set -euo pipefail
grep -n '#7fb069' assets/docs.css
echo "--- each hit above must be a border/background/decoration, not a text colour ---"
grep -nE 'color:\s*(var\(--accent\)|#7fb069)' assets/docs.css && echo "FAIL: accent used as text colour" || echo "OK: accent never used as text colour"
grep -nE 'color:\s*#(5a7a6a|6a8a7a)' assets/docs.css && echo "FAIL: large-text-only colour used" || echo "OK: no large-text-only colours used"
```

Expected: `OK: accent never used as text colour` and `OK: no large-text-only colours used`. (`border-left: 3px solid var(--accent)` and similar are fine and expected.)

- [ ] **Step 3: Commit**

```bash
git add assets/docs.css
git commit -m "feat: add shared stylesheet for document pages"
```

---

### Task 7: Homepage integration

**Files:**
- Modify: `index.html`

**Interfaces:**
- Consumes: the generated pages' URLs `/ethos/` and `/playbook/`.

- [ ] **Step 1: Add the CSS for the new section**

In `index.html`, inside the existing `<style>` block, immediately **before** the closing `</style>`, add:

```css
        .ethos-intro {
            max-width: 34rem;
            margin: 0 auto 2.5rem;
            padding-bottom: 2rem;
            border-bottom: 1px solid #d9d5c6;
        }
        .ethos-quote {
            font-family: Georgia, 'Times New Roman', serif;
            font-style: italic;
            font-size: 1.05rem;
            line-height: 1.65;
            color: #3d5a4c;
            margin-bottom: 1rem;
        }
        .ethos-links {
            list-style: none;
            display: flex;
            gap: 1.5rem;
            justify-content: center;
            flex-wrap: wrap;
            font-size: 0.9rem;
        }
        .ethos-links a { color: #4a6a5a; }
        .ethos-links .doc-kind {
            display: block;
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: #4a6a5a;
            font-weight: 700;
        }
```

- [ ] **Step 2: Add the section markup**

In `index.html`, immediately after the `<img ... class="logo">` line and **before** `<section class="section">` (the Projects section), insert:

```html
            <section class="ethos-intro">
                <p class="ethos-quote">Small, precise, slightly ceremonial digital tools for examining and enjoying a finite life.</p>
                <ul class="ethos-links">
                    <li>
                        <span class="doc-kind">Constitution</span>
                        <a href="/ethos/">The HFDS Ethos</a>
                    </li>
                    <li>
                        <span class="doc-kind">Practice</span>
                        <a href="/playbook/">The Engineer + Agent Playbook</a>
                    </li>
                </ul>
            </section>
```

- [ ] **Step 3: Verify the homepage still passes its gates**

```bash
set -euo pipefail
npx --yes html-validate@9.7.1 index.html && echo "html OK"
python3 scripts/check-assets.py index.html && echo "assets OK"
```

Expected: both pass, exit 0. `check-assets.py` resolves `/ethos/` and `/playbook/` as root-relative directory paths — if it reports them MISSING, that is a real finding: the checker tests `os.path.isfile`, and a directory is not a file. In that case, change the two hrefs to `/ethos/index.html` and `/playbook/index.html` **and record that you did so and why**; do not weaken the checker.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: link the ethos and playbook from the homepage"
```

---

### Task 8: CI gates

**Files:**
- Modify: `.github/workflows/deploy.yml`

**Interfaces:**
- Consumes: `scripts/build-pages.py --check`, `scripts/test-build-pages.py`.

- [ ] **Step 1: Extend the checks job**

In `.github/workflows/deploy.yml`, replace the `Validate HTML` and `Check asset references` steps with versions that cover every page, and add two new steps after `Run script tests`:

```yaml
      - name: Validate HTML
        run: |
          set -euo pipefail
          find . -name '*.html' -not -path './.git/*' -not -path './.superpowers/*' -print0 \
            | xargs -0 npx --yes html-validate@9.7.1

      - name: Check asset references
        run: |
          set -euo pipefail
          find . -name '*.html' -not -path './.git/*' -not -path './.superpowers/*' -print0 \
            | xargs -0 -n1 python3 scripts/check-assets.py
```

And after the existing `Run script tests` step:

```yaml
      - name: Run page builder tests
        run: |
          set -euo pipefail
          python3 scripts/test-build-pages.py

      - name: Check generated pages match their source
        run: |
          set -euo pipefail
          python3 scripts/build-pages.py --check
```

- [ ] **Step 2: Lint the workflow**

Run: `actionlint`
Expected: no output, exit 0.

- [ ] **Step 3: Confirm the checks job is still secret-free**

```bash
set -euo pipefail
awk '/^  checks:/{f=1;next} /^  [a-z_-]+:/{f=0} f' .github/workflows/deploy.yml > /tmp/cj.yml
echo "lines=$(wc -l < /tmp/cj.yml) secrets=$(grep -c 'secrets\.' /tmp/cj.yml || true)"
```

Expected: line count greater than 0 and `secrets=0`. The `checks` job runs on pull requests, including from forks.

- [ ] **Step 4: Run the whole gate locally, exactly as CI will**

```bash
set -euo pipefail
find . -name '*.html' -not -path './.git/*' -not -path './.superpowers/*' -print0 | xargs -0 npx --yes html-validate@9.7.1 && echo "[1] html OK"
find . -name '*.html' -not -path './.git/*' -not -path './.superpowers/*' -print0 | xargs -0 -n1 python3 scripts/check-assets.py >/dev/null && echo "[2] assets OK"
./scripts/check-htaccess.sh .htaccess >/dev/null && echo "[3] htaccess OK"
./scripts/test-check-assets.sh >/dev/null && ./scripts/test-check-htaccess.sh >/dev/null && echo "[4] script tests OK"
python3 scripts/test-build-pages.py 2>&1 | tail -1
python3 scripts/build-pages.py --check && echo "[6] drift gate OK"
```

Expected: all six pass. If `html-validate` reports errors in generated pages, **fix the generator or the stylesheet** — do not disable rules.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/deploy.yml
git commit -m "ci: validate all pages and gate generated output against drift"
```

---

### Task 9: Runbook, deploy verification, and accessibility check

**Files:**
- Modify: `docs/DEPLOY.md`

**Interfaces:** Consumes everything above.

- [ ] **Step 1: Document the re-sync procedure**

Append to `docs/DEPLOY.md`, before the `## Rollback` section:

````markdown
## Updating the ethos or the playbook

Both documents are authored in the separate `groundskeeper` repo. This repo holds
hand-synced **snapshots** in `content/`, and the published HTML is generated from
those snapshots — not from `groundskeeper` directly. Nothing detects drift across
that boundary, so re-syncing is a deliberate act:

```bash
cp ../groundskeeper/docs/hfds-ethos.md content/
cp ../groundskeeper/docs/engineer-agent-playbook-v2.md content/
python3 scripts/build-pages.py
git add content ethos playbook
git commit -m "content: re-sync ethos and playbook from groundskeeper"
```

If you edit `content/` and forget to rebuild, CI fails with
`FAIL: committed pages do not match content/` and names the stale files. That gate
covers `content/` → HTML. It does **not** cover `groundskeeper` → `content/`.

### If the playbook grows a new Part

`PLAYBOOK_PAGES` in `scripts/build-pages.py` maps section titles to filenames. A
new top-level section that isn't listed there is folded into the index page
instead of getting its own. A listed page with no matching section fails the
build loudly rather than emitting an empty page.
````

- [ ] **Step 2: Verify accessibility properties that were designed for**

```bash
set -euo pipefail
P=ethos/index.html
grep -q 'class="skip-link"' "$P" && echo "OK: skip link present"
grep -q '<nav class="doc-rail" aria-label="Contents">' "$P" && echo "OK: rail is a labelled nav"
grep -q '<main class="doc-main" id="content">' "$P" && echo "OK: main landmark with skip target"
grep -q '<html lang="en">' "$P" && echo "OK: lang declared"
echo "--- heading levels present in the ethos body ---"
grep -oE '<h[1-6] ' "$P" | sort | uniq -c
```

Expected: all four `OK:` lines. The heading histogram should show `h1`/`h2`/`h3` with no `h5`/`h6` appearing before an `h4` — the source's own structure drives this.

- [ ] **Step 3: Verify the pages actually work at 320px**

The spec requires no horizontal page scroll at 320px. Measure it in a real
browser engine rather than eyeballing the CSS — wide tables and long unbroken
code strings are the usual culprits, and both appear in these documents.

```bash
set -euo pipefail
python3 -m http.server 8099 --bind 127.0.0.1 >/dev/null 2>&1 &
SRV=$!
sleep 1
cat > /tmp/narrow-check.mjs <<'JS'
import { chromium } from 'playwright';
const pages = [
  '/ethos/', '/playbook/', '/playbook/foundations.html',
  '/playbook/field-notes.html', '/'
];
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 320, height: 720 } });
let bad = 0;
for (const path of pages) {
  const page = await ctx.newPage();
  await page.goto('http://127.0.0.1:8099' + path, { waitUntil: 'load' });
  const { sw, cw, culprit } = await page.evaluate(() => {
    const d = document.documentElement;
    let culprit = null;
    if (d.scrollWidth > d.clientWidth) {
      for (const el of document.querySelectorAll('*')) {
        const r = el.getBoundingClientRect();
        if (r.right > d.clientWidth + 1) {
          culprit = el.tagName + (el.className ? '.' + String(el.className).split(' ')[0] : '');
          break;
        }
      }
    }
    return { sw: d.scrollWidth, cw: d.clientWidth, culprit };
  });
  const ok = sw <= cw + 1;
  if (!ok) bad++;
  console.log(`  ${ok ? 'OK  ' : 'FAIL'} ${path}  scrollWidth=${sw} clientWidth=${cw}` +
              (culprit ? `  first overflow: ${culprit}` : ''));
  await page.close();
}
await browser.close();
process.exit(bad ? 1 : 0);
JS
npx --yes playwright@1.56.0 install chromium >/dev/null 2>&1
npx --yes --package=playwright@1.56.0 node /tmp/narrow-check.mjs; RC=$?
kill $SRV 2>/dev/null || true
echo "exit=$RC"
```

Expected: `OK` for all five pages and `exit=0`. If a page overflows, the script
names the first offending element — fix it in `assets/docs.css` (tables and
`pre` blocks should scroll inside their own box, which the stylesheet already
sets up) rather than suppressing the check.

If `npx --package=playwright node …` cannot resolve the module (the same
resolution problem that ruled out running `marked` this way), install into a
scratch directory instead: `mkdir -p /tmp/pw && cd /tmp/pw && npm i
playwright@1.56.0 && node /tmp/narrow-check.mjs`. Do not skip this step — record
which method you used.

- [ ] **Step 4: Verify the deploy, for real, against the live server**

This is the step that caught the `blog/` and `.well-known/` problem last time.

```bash
set -euo pipefail
rsync -azn --delete --delete-delay --delay-updates --itemize-changes \
  --exclude-from=.deployignore \
  -e "ssh -i $HOME/.ssh/hds_deploy -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=15 -p 22" \
  ./ sml_hds@iad1-shared-e1-06.dreamhost.com:/home/sml_hds/homeforderangedscientists.com/ \
  > /tmp/dryrun-docs.txt 2>&1
echo "--- WOULD DELETE (must be none) ---"
grep '^\*deleting' /tmp/dryrun-docs.txt || echo "  NONE"
echo "--- new directories that must transfer ---"
grep -E '^(cd|>f).*(ethos|playbook|assets)' /tmp/dryrun-docs.txt | head -20
echo "--- content/ must NOT appear ---"
grep -c '^.*content/' /tmp/dryrun-docs.txt | sed 's/^/content refs: /'
```

Expected: `NONE` deletions; `ethos/`, `playbook/` and `assets/` present in the transfer list; `content refs: 0`.

- [ ] **Step 5: Commit**

```bash
git add docs/DEPLOY.md
git commit -m "docs: record the ethos and playbook re-sync procedure"
```

- [ ] **Step 6: Push and verify live**

```bash
set -euo pipefail
git push origin main
gh run watch
curl -sS -o /dev/null -w 'ethos    %{http_code}\n' https://www.homeforderangedscientists.com/ethos/
curl -sS -o /dev/null -w 'playbook %{http_code}\n' https://www.homeforderangedscientists.com/playbook/
curl -sS -o /dev/null -w 'part     %{http_code}\n' https://www.homeforderangedscientists.com/playbook/foundations.html
curl -sS -o /dev/null -w 'css      %{http_code}\n' https://www.homeforderangedscientists.com/assets/docs.css
curl -sS -o /dev/null -w 'content  %{http_code}  (want 403 or 404 - must NOT be 200)\n' https://www.homeforderangedscientists.com/content/hfds-ethos.md
curl -sS "https://www.homeforderangedscientists.com/build-info.json?_cb=$$" | jq -r .commit
git rev-parse HEAD
```

Expected: `200` for the four pages, **not 200** for the markdown source, and the served commit equal to `git rev-parse HEAD`.

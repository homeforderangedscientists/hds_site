#!/usr/bin/env python3
"""Render content/*.md into committed HTML pages.

Usage:
  build-pages.py            regenerate all pages in place
  build-pages.py --check    regenerate to a temp dir and diff; write nothing

Generation is two-pass. Pass one renders every page's body -- markdown to
HTML, own leading heading stripped and moved to the masthead, remaining
headings shifted so the shallowest is h2, ids injected -- and builds a
site-wide map of heading slug -> the page that owns it. Pass two rewrites
every in-page href="#slug" whose slug is owned by a DIFFERENT page into a
cross-page link, then writes the file. After every page is written, every
anchor on every page is checked against the ids that actually exist on its
target page; any that don't resolve fail the build loudly rather than
shipping a page with dead internal links.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_pages_lib import (  # noqa: E402
    add_heading_ids,
    find_unresolved_anchors,
    heading_levels,
    rewrite_cross_page_anchors,
    shift_headings,
    slugify,
    split_sections,
    strip_leading_heading,
)

MARKED = "marked@18.0.10"
ROOT = Path(__file__).resolve().parent.parent


def render_markdown(md, label=None):
    """Markdown -> HTML fragment via the pinned marked CLI."""
    with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8",
                                     delete=False) as fh:
        fh.write(md)
        tmp = fh.name
    try:
        proc = subprocess.run(
            ["npx", "--yes", MARKED, "-i", tmp],
            capture_output=True, text=True, encoding="utf-8",
        )
    finally:
        Path(tmp).unlink(missing_ok=True)
    if proc.returncode != 0:
        where = f" ({label})" if label else ""
        sys.exit(f"FAIL: {MARKED} exited {proc.returncode}{where}\n{proc.stderr}")
    return proc.stdout


def render_body(md, label=None):
    """Render one page's markdown into a masthead-ready (body, toc, title_id).

    The section's own leading '# ' heading is pulled off before rendering
    (the masthead carries it instead), the remaining headings are shifted
    so the shallowest becomes h2 (clamped at h6), and heading ids are
    injected. title_id is the slug for the masthead's own h1 -- computed
    from the REMOVED heading's actual text, not any display label, since
    that's what other pages' cross-page links were generated against.
    """
    raw_title, remaining_md = strip_leading_heading(md)
    html = render_markdown(remaining_md, label=label)
    levels = heading_levels(html)
    delta = (2 - min(levels)) if levels else 0
    html = shift_headings(html, delta)
    body, toc = add_heading_ids(html)
    title_id = slugify(raw_title) if raw_title else "section"
    return body, toc, title_id


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
<h1 class="doc-title" id="{title_id}">{title}</h1>
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


def collect_ethos_page(out_root):
    """Pass-one render of the ethos page. Returns {relpath: page_spec}."""
    md = (ROOT / "content" / "hfds-ethos.md").read_text(encoding="utf-8")
    body, toc, title_id = render_body(md, label="ethos")
    spec = dict(
        out_path=out_root / "ethos" / "index.html",
        title="The HFDS Ethos",
        title_id=title_id,
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
        toc=toc,
    )
    return {"ethos/index.html": spec}


def collect_playbook_pages(out_root):
    """Pass-one render of every playbook page. Returns {relpath: page_spec}."""
    md = (ROOT / "content" / "engineer-agent-playbook-v2.md").read_text(encoding="utf-8")
    try:
        sections = split_sections(md)
    except ValueError as exc:
        raise ValueError(f"engineer-agent-playbook-v2.md: {exc}") from exc

    # Map each configured page to its section; anything unmatched (the title
    # block and its front matter) becomes the playbook index. Matching is by
    # exact equality on the title text before the em-dash (not startswith),
    # so "Part I" and "Part II" cannot collide -- "Part I" is a literal
    # string prefix of "Part II"/"Part III"/"Part IV".
    by_prefix = {}
    front = []
    for title, section_md in sections:
        key = title.split("—", 1)[0].strip()
        match = next((p for p in PLAYBOOK_PAGES if p[0] == key), None)
        if match:
            by_prefix[match[1]] = (match[2], section_md)
        else:
            front.append(section_md)

    missing = [p[1] for p in PLAYBOOK_PAGES if p[1] not in by_prefix]
    if missing:
        sys.exit(f"FAIL: no source section matched these pages: {missing}\n"
                 f"      Section titles found: {[t for t, _ in sections]}")

    pages = {}
    order = [p[1] for p in PLAYBOOK_PAGES]

    # Index page from the front matter.
    body, toc, title_id = render_body("\n\n".join(front), label="playbook index")
    nav_items = "\n".join(
        f'<li class="rail-l2"><a href="{fn}">{esc(by_prefix[fn][0])}</a></li>'
        for fn in order
    )
    pages["playbook/index.html"] = dict(
        out_path=out_root / "playbook" / "index.html",
        title="The Engineer + Agent Playbook",
        title_id=title_id,
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
        toc=toc,
    )

    for i, fn in enumerate(order):
        label, section_md = by_prefix[fn]
        body, toc, title_id = render_body(section_md, label=fn)
        prev_link = (order[i - 1], by_prefix[order[i - 1]][0]) if i > 0 else ("index.html", "Playbook contents")
        next_link = (order[i + 1], by_prefix[order[i + 1]][0]) if i + 1 < len(order) else None
        pages[f"playbook/{fn}"] = dict(
            out_path=out_root / "playbook" / fn,
            title=label,
            title_id=title_id,
            description=f"{label} of the Engineer + Agent Playbook.",
            css_path="../assets/docs.css",
            home_path="../",
            rail_title='<p class="rail-doc"><a href="index.html">The Engineer + Agent Playbook</a></p>',
            rail_items=build_rail(toc),
            eyebrow="The Engineer + Agent Playbook",
            meta=label,
            body=body,
            pager=build_pager(prev_link, next_link),
            footer_note='Part of the Engineer + Agent Playbook.',
            toc=toc,
        )
    return pages


def generate(out_root):
    """Render, cross-link, write, and audit every page. Returns relpaths written.

    Pass one (collect_ethos_page / collect_playbook_pages) renders every
    page's body and its toc without writing anything. This function does
    pass two: build the site-wide slug -> owning-page map from every page's
    title_id and toc, rewrite each page's cross-page anchors against it,
    write the file, then audit every anchor on every written page and fail
    loudly if any doesn't resolve to a real id on its target page.
    """
    pages = {}
    pages.update(collect_ethos_page(out_root))
    pages.update(collect_playbook_pages(out_root))

    slug_owner = {}
    for relpath, spec in pages.items():
        slug_owner[spec["title_id"]] = relpath
        for level, slug, _text in spec["toc"]:
            slug_owner[slug] = relpath

    written = []
    final_html = {}
    for relpath, spec in pages.items():
        spec = dict(spec)
        out_path = spec.pop("out_path")
        spec.pop("toc")
        spec["body"] = rewrite_cross_page_anchors(spec["body"], relpath, slug_owner)
        html = PAGE_TEMPLATE.format(**spec)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")
        final_html[relpath] = html
        written.append(out_path.relative_to(out_root))

    unresolved = find_unresolved_anchors(final_html)
    if unresolved:
        print("FAIL: unresolved internal anchors:", file=sys.stderr)
        for relpath, href in unresolved:
            print(f"  {relpath}: {href}", file=sys.stderr)
        sys.exit(1)

    return written


def check():
    """Regenerate into a temp directory and diff against the committed pages."""
    import filecmp

    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        generate(tmp_root)
        mismatches = []
        for rel_dir in ("ethos", "playbook"):
            src = ROOT / rel_dir
            dst = tmp_root / rel_dir
            committed = sorted(p.name for p in src.glob("*.html")) if src.exists() else []
            regenerated = sorted(p.name for p in dst.glob("*.html")) if dst.exists() else []
            if committed != regenerated:
                mismatches.append(f"{rel_dir}: file list differs "
                                  f"(committed={committed} regenerated={regenerated})")
                continue
            for name in committed:
                if not filecmp.cmp(src / name, dst / name, shallow=False):
                    mismatches.append(f"{rel_dir}/{name}: content differs from committed")
        if mismatches:
            print("FAIL: generated pages do not match committed pages:", file=sys.stderr)
            for m in mismatches:
                print(f"  {m}", file=sys.stderr)
            return 1
        print("OK: committed pages match a fresh regeneration.")
        return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="regenerate to a temp dir and diff; write nothing")
    args = ap.parse_args()
    if args.check:
        return check()
    written = generate(ROOT)
    for p in written:
        print(f"  wrote {p}")
    print(f"{len(written)} pages generated")
    return 0


if __name__ == "__main__":
    sys.exit(main())

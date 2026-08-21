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
    body, toc = add_heading_ids(render_markdown(md, label="ethos"))
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

    written = []
    order = [p[1] for p in PLAYBOOK_PAGES]

    # Index page from the front matter.
    body, toc = add_heading_ids(render_markdown("\n\n".join(front), label="playbook index"))
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
        body, toc = add_heading_ids(render_markdown(section_md, label=fn))
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

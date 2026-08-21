#!/usr/bin/env python3
"""Pure text helpers for build-pages.py.

No file I/O and no subprocesses live here, so every function is unit-testable
in isolation. The CLI wrapper owns everything impure.
"""
import html
import posixpath
import re

FENCE_LINE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
TOP_HEADING_RE = re.compile(r"^# (.+)$")
ATX_CLOSING_HASHES_RE = re.compile(r"[ \t]+#+[ \t]*$")
HEADING_TAG_RE = re.compile(r"<h([1234])>(.*?)</h\1>", re.DOTALL)
TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")
NON_SLUG_CHAR_RE = re.compile(r"[^a-z0-9 -]")
HEADING_LEVEL_RE = re.compile(r"<(/?)h([1-6])((?:\s[^>]*)?)>", re.IGNORECASE)
LOCAL_HREF_RE = re.compile(r'href="#([^"]+)"')
PAGE_HREF_RE = re.compile(
    r'href="((?:(?!https?://|mailto:)[^"#])+\.html)#([^"]+)"'
)
ID_ATTR_RE = re.compile(r'\bid="([^"]+)"')


def split_sections(md):
    """Split markdown on top-level '# ' headings that are outside code fences.

    Returns [(title, body_markdown), ...]. The body INCLUDES its heading line.
    Any text before the first top-level heading becomes a leading section whose
    title is the empty string.

    Fence tracking follows CommonMark's actual rules, not naive toggling on any
    ``` or ~~~ line: an opening fence is a run of 3+ backticks or 3+ tildes
    (indented at most 3 spaces); a closing fence must use the SAME character, a
    run at least as long as the opening, and nothing but trailing whitespace
    after it. Anything else -- a different character, a shorter run, or trailing
    text -- is fence content, not a delimiter. This is what lets a ~~~ block
    contain a literal ``` line, and a ````-fence wrap a ```-fence example,
    without either one falsely toggling fence state and exposing a '# Heading'
    inside the example as a fabricated section boundary.

    A fence left open at end of file is a malformed document: this raises
    ValueError naming the line where it opened, rather than silently truncating
    everything after it.
    """
    lines = md.splitlines()
    in_fence = False
    fence_char = None
    fence_len = 0
    fence_open_line = None  # 1-based
    starts = []  # (line_index, title)
    for i, line in enumerate(lines):
        m = FENCE_LINE_RE.match(line)
        if in_fence:
            if m:
                run, rest = m.group(1), m.group(2)
                if run[0] == fence_char and len(run) >= fence_len and rest.strip() == "":
                    in_fence = False
                    fence_char = None
                    fence_len = 0
                    fence_open_line = None
            continue
        if m:
            run, rest = m.group(1), m.group(2)
            in_fence = True
            fence_char = run[0]
            fence_len = len(run)
            fence_open_line = i + 1
            continue
        hm = TOP_HEADING_RE.match(line)
        if hm:
            title = ATX_CLOSING_HASHES_RE.sub("", hm.group(1)).strip()
            starts.append((i, title))

    if in_fence:
        raise ValueError(f"unterminated code fence opened at line {fence_open_line}")

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
    """GitHub-compatible ASCII slug.

    Mirrors GitHub's own heading-anchor algorithm exactly, hyphen runs and
    all: strip tags, lowercase, drop (not replace) any character that isn't
    a-z, 0-9, space or hyphen, turn each surviving space into its own
    hyphen, then trim leading/trailing hyphens. The no-collapsing step is
    load-bearing -- an em-dash (or any punctuation) flanked by spaces drops
    out from between them and leaves both spaces standing, which is exactly
    how GitHub turns "Part I — Foundations" into "part-i--foundations" (two
    hyphens). Collapsing those runs is what silently broke every link in
    the source document that used an em-dash in its heading.

    Headings arrive here as rendered-HTML inner text, so a literal "&" in
    the markdown source shows up as the entity "&amp;" -- decoded back to
    "&" (and any other entity) right after tags are stripped, so the slug
    is computed against the same plain text GitHub's own slugifier sees.
    """
    text = TAG_RE.sub("", text)
    text = html.unescape(text)
    text = text.lower()
    text = NON_SLUG_CHAR_RE.sub("", text)  # drop, don't replace
    text = text.replace(" ", "-")
    text = text.strip("-")
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
    """Inject id attributes into h1-h4 and return (html, toc).

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
        plain = re.sub(r"\s+", " ", html.unescape(TAG_RE.sub("", inner))).strip()
        out.append(html_fragment[last:m.start()])
        out.append(f'<h{level} id="{slug}">{inner}</h{level}>')
        last = m.end()
        toc.append((level, slug, plain))
    out.append(html_fragment[last:])
    return "".join(out), toc


def strip_leading_heading(md):
    """Pull a leading top-level '# ' heading line off md.

    Returns (title, remaining_md). Used so a page whose masthead already
    carries the section title doesn't also render that title as a
    duplicate first heading in the body. If md doesn't start with a
    top-level heading, returns ("", md) unchanged. ATX closing hashes
    ("# Title #") are stripped from the returned title the same way
    split_sections does it, so the two stay consistent.
    """
    lines = md.splitlines()
    if not lines:
        return "", md
    m = TOP_HEADING_RE.match(lines[0])
    if not m:
        return "", md
    title = ATX_CLOSING_HASHES_RE.sub("", m.group(1)).strip()
    rest = "\n".join(lines[1:]).strip()
    return title, (rest + "\n") if rest else ""


def heading_levels(html):
    """Levels of every opening heading tag (h1-h6) in html, in order."""
    return [int(m.group(2)) for m in HEADING_LEVEL_RE.finditer(html) if not m.group(1)]


def shift_headings(html, delta):
    """Shift every heading tag's level by delta, clamped to h1..h6.

    Rewrites both the opening and closing tag of each heading so pairs stay
    matched, and preserves any attributes already on the opening tag.
    delta == 0 is a no-op.
    """
    if delta == 0:
        return html

    def repl(m):
        slash, level, attrs = m.group(1), int(m.group(2)), m.group(3)
        new_level = min(6, max(1, level + delta))
        return f"<{slash}h{new_level}{attrs}>"

    return HEADING_LEVEL_RE.sub(repl, html)


def rewrite_cross_page_anchors(html, own_page, slug_owner):
    """Rewrite href="#slug" to href="<page>#slug" for slugs owned elsewhere.

    own_page and the values in slug_owner are POSIX-style paths relative to
    the site root (e.g. "playbook/foundations.html"). A slug owned by a
    page other than own_page is rewritten to a path relative to own_page's
    directory. A slug owned by own_page itself, or not present in
    slug_owner at all (an unknown/dead anchor -- left for the unresolved-
    anchor audit to catch), is left untouched.
    """
    def repl(m):
        slug = m.group(1)
        owner = slug_owner.get(slug)
        if owner is None or owner == own_page:
            return m.group(0)
        rel = posixpath.relpath(owner, start=posixpath.dirname(own_page) or ".")
        return f'href="{rel}#{slug}"'

    return LOCAL_HREF_RE.sub(repl, html)


def find_unresolved_anchors(pages):
    """Audit every in-page and cross-page anchor across a built site.

    pages is {relpath: full_page_html}, relpath POSIX-style relative to the
    site root. Returns [(relpath, href_text), ...] for every
    href="#slug" or href="page.html#slug" whose target id is not actually
    present on the resolved target page. An empty list means every internal
    link resolves.
    """
    ids_by_page = {
        relpath: set(ID_ATTR_RE.findall(html)) for relpath, html in pages.items()
    }
    unresolved = []
    for relpath, html in pages.items():
        own_dir = posixpath.dirname(relpath)
        for m in PAGE_HREF_RE.finditer(html):
            target_rel, slug = m.group(1), m.group(2)
            target_page = posixpath.normpath(posixpath.join(own_dir, target_rel))
            target_ids = ids_by_page.get(target_page)
            if target_ids is None or slug not in target_ids:
                unresolved.append((relpath, m.group(0)))
        for m in LOCAL_HREF_RE.finditer(html):
            slug = m.group(1)
            if slug not in ids_by_page[relpath]:
                unresolved.append((relpath, m.group(0)))
    return unresolved

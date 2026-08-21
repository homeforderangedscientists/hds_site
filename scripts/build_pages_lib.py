#!/usr/bin/env python3
"""Pure text helpers for build-pages.py.

No file I/O and no subprocesses live here, so every function is unit-testable
in isolation. The CLI wrapper owns everything impure.
"""
import re

FENCE_LINE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
TOP_HEADING_RE = re.compile(r"^# (.+)$")
ATX_CLOSING_HASHES_RE = re.compile(r"[ \t]+#+[ \t]*$")
HEADING_TAG_RE = re.compile(r"<h([123])>(.*?)</h\1>", re.DOTALL)
TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")


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

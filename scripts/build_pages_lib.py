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

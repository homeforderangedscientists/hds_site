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

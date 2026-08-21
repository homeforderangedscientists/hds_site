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

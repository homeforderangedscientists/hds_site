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

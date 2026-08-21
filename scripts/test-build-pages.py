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

    def test_tilde_fence_containing_a_backtick_line_still_splits_correctly(self):
        # A literal ``` line inside a ~~~ block must not close the fence: it is
        # the wrong delimiter character. Confirmed failure mode: naive toggling
        # on ANY ``` or ~~~ line collapsed 3 real headings down to 1.
        md = (
            "# One\n\n~~~\n```\n# Not A Heading\n~~~\n\nmiddle\n\n"
            "# Two\n\nprose\n\n# Three\n"
        )
        got = split_sections(md)
        self.assertEqual([t for t, _ in got], ["One", "Two", "Three"])
        self.assertIn("middle", got[0][1])

    def test_four_backtick_fence_wrapping_a_three_backtick_example(self):
        # The standard way to show fence syntax in docs: wrap a ```-fenced
        # example in a longer ```` fence. The inner ``` must NOT close the
        # outer fence, so the '# Heading' inside the example must NOT become
        # a real section boundary (that would fabricate a phantom page).
        md = (
            "# One\n\n````markdown\n```\n# Heading inside example\n```\n````\n\n"
            "# Two\n"
        )
        got = split_sections(md)
        self.assertEqual([t for t, _ in got], ["One", "Two"])
        self.assertIn("# Heading inside example", got[0][1])

    def test_indented_fence_up_to_three_spaces_is_respected(self):
        md = "# One\n\n   ```\n# Not A Heading\n   ```\n\n# Two\n"
        got = split_sections(md)
        self.assertEqual([t for t, _ in got], ["One", "Two"])

    def test_closing_fence_longer_than_opening_still_closes(self):
        # CommonMark: a closing fence only needs to be AT LEAST as long as the
        # opening one.
        md = "# One\n\n```\n# Not A Heading\n````\n\n# Two\n"
        got = split_sections(md)
        self.assertEqual([t for t, _ in got], ["One", "Two"])

    def test_trailing_text_after_closing_delimiter_does_not_close_fence(self):
        # A closing fence line may have nothing after the delimiter run but
        # whitespace. "``` oops" is content, not a close.
        md = "# One\n\n```\n# Not A Heading\n``` oops\n```\n\n# Two\n"
        got = split_sections(md)
        self.assertEqual([t for t, _ in got], ["One", "Two"])
        self.assertIn("# Not A Heading", got[0][1])

    def test_unterminated_fence_raises_value_error_naming_the_line(self):
        md = "# One\n\nprose\n\n```\nunterminated\n\n# Two\n"
        with self.assertRaises(ValueError) as ctx:
            split_sections(md)
        self.assertIn("5", str(ctx.exception))

    def test_atx_closing_hashes_are_stripped_from_title(self):
        md = "# Title #\n\nbody\n"
        got = split_sections(md)
        self.assertEqual(got[0][0], "Title")


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

    def test_stray_angle_brackets_are_not_mistaken_for_tags(self):
        # "age < 18 > check" has no real HTML tag in it. A naive <[^>]+> strips
        # " 18 " right out of the slug -- that's the defect being fixed.
        self.assertEqual(slugify("Rule: age < 18 > check"), "rule-age-18-check")


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

    def test_stray_angle_brackets_survive_into_slug_and_toc_text(self):
        html, toc = add_heading_ids("<h2>Rule: age < 18 > check</h2>")
        self.assertIn('id="rule-age-18-check"', html)
        self.assertEqual(toc[0][1], "rule-age-18-check")
        self.assertEqual(toc[0][2], "Rule: age < 18 > check")


if __name__ == "__main__":
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""Unit tests for build_pages_lib. Run: python3 scripts/test-build-pages.py"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_pages_lib import (
    add_heading_ids,
    dedupe_slugs,
    find_unresolved_anchors,
    heading_levels,
    rewrite_cross_page_anchors,
    shift_headings,
    slugify,
    split_sections,
    strip_leading_heading,
)


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
        # GitHub's algorithm does NOT collapse hyphen runs: an em-dash
        # flanked by spaces drops out from between them and leaves both
        # spaces standing, producing a double hyphen. This is the load-
        # bearing behavior change for defect 1 -- collapsing this run is
        # exactly what broke every em-dash heading link in the source doc.
        self.assertEqual(slugify("Part I — Foundations"), "part-i--foundations")
        self.assertEqual(slugify("Rule: Don't guess."), "rule-dont-guess")

    def test_trims_leading_and_trailing_hyphens_but_does_not_collapse_runs(self):
        # Was "test_collapses_and_trims_hyphens" under the old (GitHub-
        # incompatible) algorithm. GitHub's algorithm strips punctuation
        # without replacing it, so "·" flanked by two spaces on each side
        # disappears and leaves all four spaces standing as four hyphens;
        # only the leading/trailing runs get trimmed.
        self.assertEqual(slugify("  A  ·  B  "), "a----b")

    def test_empty_input_gets_fallback(self):
        self.assertEqual(slugify("⭐⭐⭐"), "section")

    def test_stray_angle_brackets_are_not_mistaken_for_tags(self):
        # "age < 18 > check" has no real HTML tag in it. A naive <[^>]+> strips
        # " 18 " right out of the slug -- that's the defect being fixed.
        # Both "<" and ">" are flanked by a space on each side, so each
        # removal leaves a double hyphen behind, same as the em-dash case.
        self.assertEqual(slugify("Rule: age < 18 > check"), "rule-age--18--check")

    def test_decodes_html_entities_before_slugifying(self):
        # add_heading_ids hands slugify rendered-HTML inner text, so a
        # literal "&" typed in the markdown source (e.g. "§11 Failure
        # modes & recovery") arrives here as the entity "&amp;". Decode it
        # back to "&" -- which then drops out as a disallowed character,
        # same as any other punctuation -- rather than leaving the literal
        # letters "amp" stuck in the slug.
        self.assertEqual(slugify("Failure modes &amp; recovery"),
                         "failure-modes--recovery")

    def test_github_anchor_style_verification_cases(self):
        # The exact cases the fix was verified against: real double-hyphen
        # headings from content/engineer-agent-playbook-v2.md and
        # content/hfds-ethos.md, run through GitHub's actual anchor
        # algorithm (steps: strip tags, lowercase, drop disallowed chars
        # without replacing them, spaces -> hyphens with no collapsing,
        # trim ends).
        self.assertEqual(slugify("Part I — Foundations"), "part-i--foundations")
        self.assertEqual(slugify("§10 Diagnosis — build the lab"),
                         "10-diagnosis--build-the-lab")
        self.assertEqual(slugify("Appendix C — About the case studies"),
                         "appendix-c--about-the-case-studies")
        self.assertEqual(slugify("⭐ The Cardinal Pair"), "the-cardinal-pair")


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

    def test_ids_h4_headings_too(self):
        # Defect 3: shifted ethos cluster children land on h4, and they
        # still need anchors or the shift breaks their own inbound links.
        html, toc = add_heading_ids("<h4>Deep</h4>")
        self.assertIn('<h4 id="deep">Deep</h4>', html)
        self.assertEqual(toc, [(4, "deep", "Deep")])

    def test_ignores_h5_and_below(self):
        html, toc = add_heading_ids("<h5>Deeper</h5>")
        self.assertEqual(toc, [])
        self.assertEqual(html, "<h5>Deeper</h5>")

    def test_stray_angle_brackets_survive_into_slug_and_toc_text(self):
        html, toc = add_heading_ids("<h2>Rule: age < 18 > check</h2>")
        self.assertIn('id="rule-age--18--check"', html)
        self.assertEqual(toc[0][1], "rule-age--18--check")
        self.assertEqual(toc[0][2], "Rule: age < 18 > check")


class TestStripLeadingHeading(unittest.TestCase):
    def test_pulls_off_the_first_top_level_heading(self):
        title, rest = strip_leading_heading("# Part I — Foundations\n\nprose\n")
        self.assertEqual(title, "Part I — Foundations")
        self.assertEqual(rest, "prose\n")

    def test_only_removes_the_very_first_heading_not_later_ones(self):
        # The ethos case: the doc title is removed, but the six cluster
        # '# ' headings further down the SAME body must survive untouched
        # so they can be shifted to h2 like everything else.
        md = "# Doc Title\n\n## Preamble\n\n# Cluster One\n\nbody\n"
        title, rest = strip_leading_heading(md)
        self.assertEqual(title, "Doc Title")
        self.assertIn("## Preamble", rest)
        self.assertIn("# Cluster One", rest)

    def test_no_leading_heading_is_a_no_op(self):
        title, rest = strip_leading_heading("just prose\n")
        self.assertEqual(title, "")
        self.assertEqual(rest, "just prose\n")


class TestHeadingShift(unittest.TestCase):
    def test_shifts_every_heading_by_delta_clamped_to_h6(self):
        html = "<h1>Top</h1><p>x</p><h3>Deep</h3>"
        self.assertEqual(
            shift_headings(html, 1),
            "<h2>Top</h2><p>x</p><h4>Deep</h4>",
        )
        self.assertEqual(shift_headings("<h6>Bottom</h6>", 3), "<h6>Bottom</h6>")

    def test_zero_delta_is_a_no_op(self):
        html = "<h2>Already right</h2>"
        self.assertEqual(shift_headings(html, 0), html)

    def test_heading_levels_reports_opening_tags_only(self):
        self.assertEqual(heading_levels("<h1>A</h1><h3>B</h3>"), [1, 3])

    def test_playbook_part_pages_have_zero_delta_ethos_clusters_shift_by_one(self):
        # Mirrors defect 3's own worked examples: a playbook part body is
        # already shallowest-h2 (delta 0); the ethos body's shallowest
        # heading after its title is removed is h1 (the cluster headings),
        # so delta is +1 and cluster children (h2/h3) move to h3/h4.
        part_html = "<h2>§1 Mental models</h2><h3>Rule</h3>"
        levels = heading_levels(part_html)
        delta = 2 - min(levels)
        self.assertEqual(delta, 0)
        self.assertEqual(shift_headings(part_html, delta), part_html)

        ethos_html = "<h1>The Cardinal Pair</h1><h3>Why</h3><h2>Whimsy</h2>"
        levels = heading_levels(ethos_html)
        delta = 2 - min(levels)
        self.assertEqual(delta, 1)
        self.assertEqual(
            shift_headings(ethos_html, delta),
            "<h2>The Cardinal Pair</h2><h4>Why</h4><h3>Whimsy</h3>",
        )


class TestCrossPageAnchors(unittest.TestCase):
    def test_leaves_same_page_anchors_alone(self):
        html = '<a href="#local-slug">here</a>'
        owner = {"local-slug": "playbook/foundations.html"}
        out = rewrite_cross_page_anchors(html, "playbook/foundations.html", owner)
        self.assertEqual(out, html)

    def test_rewrites_anchors_owned_by_a_different_page_in_the_same_dir(self):
        html = '<a href="#10-diagnosis--build-the-lab">jump</a>'
        owner = {"10-diagnosis--build-the-lab": "playbook/when-it-goes-wrong.html"}
        out = rewrite_cross_page_anchors(html, "playbook/index.html", owner)
        self.assertEqual(
            out, '<a href="when-it-goes-wrong.html#10-diagnosis--build-the-lab">jump</a>'
        )

    def test_rewrites_with_a_relative_path_across_directories(self):
        html = '<a href="#some-slug">jump</a>'
        owner = {"some-slug": "ethos/index.html"}
        out = rewrite_cross_page_anchors(html, "playbook/foundations.html", owner)
        self.assertEqual(out, '<a href="../ethos/index.html#some-slug">jump</a>')

    def test_unknown_slug_is_left_for_the_audit_to_catch(self):
        html = '<a href="#does-not-exist-anywhere">dead</a>'
        out = rewrite_cross_page_anchors(html, "playbook/index.html", {})
        self.assertEqual(out, html)


class TestUnresolvedAnchors(unittest.TestCase):
    def test_no_unresolved_anchors_is_a_clean_pass(self):
        pages = {
            "playbook/index.html": '<main id="content"><a href="#content">skip</a>'
                                    '<a href="foundations.html#part-i--foundations">Part I</a></main>',
            "playbook/foundations.html": '<h1 id="part-i--foundations">Part I</h1>',
        }
        self.assertEqual(find_unresolved_anchors(pages), [])

    def test_flags_a_same_page_anchor_with_no_matching_id(self):
        pages = {"playbook/index.html": '<a href="#ghost">dead</a>'}
        got = find_unresolved_anchors(pages)
        self.assertEqual(got, [("playbook/index.html", 'href="#ghost"')])

    def test_flags_a_cross_page_anchor_whose_target_id_is_missing(self):
        pages = {
            "playbook/index.html": '<a href="foundations.html#missing">jump</a>',
            "playbook/foundations.html": '<h1 id="part-i--foundations">Part I</h1>',
        }
        got = find_unresolved_anchors(pages)
        self.assertEqual(
            got, [("playbook/index.html", 'href="foundations.html#missing"')]
        )

    def test_flags_a_cross_page_anchor_whose_target_page_does_not_exist(self):
        pages = {"playbook/index.html": '<a href="nowhere.html#slug">jump</a>'}
        got = find_unresolved_anchors(pages)
        self.assertEqual(got, [("playbook/index.html", 'href="nowhere.html#slug"')])


if __name__ == "__main__":
    unittest.main(verbosity=2)

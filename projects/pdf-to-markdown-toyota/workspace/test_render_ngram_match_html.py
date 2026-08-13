import unittest

from render_ngram_match_html import matched_position_mask, missing_ngrams, render_masked_text


class NgramHtmlTest(unittest.TestCase):
    def test_missing_ngrams_are_reference_strings(self):
        self.assertEqual(missing_ngrams("abcdef", "abcXYZ", 3), ["bcd", "cde", "def"])

    def test_matched_positions_cover_the_matching_window(self):
        self.assertEqual(matched_position_mask("abcXYZ", 3, {"abc"}), [True, True, True, False, False, False])

    def test_rendered_text_escapes_html(self):
        rendered = render_masked_text("a<b", [True, False, False], "match", "unmatched")
        self.assertIn("&lt;", rendered)
        self.assertIn('class="match"', rendered)


if __name__ == "__main__":
    unittest.main()
